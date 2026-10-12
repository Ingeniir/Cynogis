"""Analyses de proximité : comptage de points, polygones à partir de points, plus proches
voisins et matrices de distances. Distances ellipsoïdales en mètres (bord à bord)."""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable
from typing import Any

from qgis.core import (
    Qgis,
    QgsDistanceArea,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsPointXY,
    QgsRectangle,
    QgsSpatialIndex,
    QgsVectorLayer,
)

from ..core import proximity
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.fields import unique_field_name
from ..core.metrics import M2_PER_HA
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.stats import describe, to_float
from ..core.units import LENGTH_UNITS, convert_length
from .common import (
    area_m2,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    iter_geometries,
    length_m,
    make_field,
    perimeter_m,
    require_field,
    to_json_value,
)
from .features import FILTER_HELP
from .geoprocessing import OUTPUT_NAME
from .outputs import save_to_project

HULL_METHODS = ("ordered", "convex_hull", "concave_hull")
MATRIX_FORMATS = ("matrix", "pairs")
MAX_PAIRS = 5000
MAX_GRID_CELLS = 200_000  # au-delà, QGIS gèlerait trop longtemps
METERS_PER_DEGREE = 111_320.0  # ordre de grandeur, pour pré-filtrer en SCR géographique
UNIT = Param("string", "Unité des distances renvoyées.", required=False, default="m",
             enum=tuple(LENGTH_UNITS))


KIND_LABELS = {"point": "points", "polygon": "polygones"}


def _layer(layer_id: str, kind: str) -> QgsVectorLayer:
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != kind:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"{layer.name()} n'est pas une couche de {KIND_LABELS[kind]}.")
    return layer


def _field(layer: QgsVectorLayer, name: str | None) -> str | None:
    """Nom exact du champ (contrôlé), ou None si non demandé."""
    return require_field(layer, name) if name else None


def _label(feature: QgsFeature, id_field: str | None) -> Any:
    return to_json_value(feature[id_field]) if id_field else feature.id()


def _index_points(points: QgsVectorLayer, crs: Any, point_filter: str | None,
                  weight_field: str | None, class_field: str | None):
    """Index spatial des points (dans crs), géométries et (poids, catégorie) par fid."""
    index = QgsSpatialIndex()
    attributes: dict[int, tuple[Any, Any]] = {}
    geometries: dict[int, QgsGeometry] = {}
    request = feature_request(points, point_filter,
                              [f for f in (weight_field, class_field) if f])
    for feature, geometry in iter_geometries(points, request, crs):
        geometries[feature.id()] = geometry
        attributes[feature.id()] = (
            to_float(to_json_value(feature[weight_field])) if weight_field else None,
            group_key(feature[class_field]) if class_field else None)
        index.addFeature(feature.id(), geometry.boundingBox())
    return index, geometries, attributes


def _point_hits(polygons: Iterable[tuple[Any, QgsGeometry]], index: QgsSpatialIndex,
                geometries: dict[int, QgsGeometry]):
    """(polygone, géométrie, fids des points qui le touchent) pour chaque polygone."""
    for item, polygon in polygons:
        engine = QgsGeometry.createGeometryEngine(polygon.constGet())
        engine.prepareGeometry()
        yield item, polygon, [fid for fid in index.intersects(polygon.boundingBox())
                              if engine.intersects(geometries[fid].constGet())]


def _distance_m(da: QgsDistanceArea, a: QgsGeometry, b: QgsGeometry) -> float:
    """Distance bord à bord (0 si les géométries se touchent), mesurée sur l'ellipsoïde."""
    if a.intersects(b):
        return 0.0
    return length_m(da, a.shortestLine(b))


def _collect(layer: QgsVectorLayer, id_field: str | None, expression: str | None,
             crs, limit: int) -> list[tuple[int, Any, QgsGeometry]]:
    """(fid, libellé, géométrie dans crs), au plus limit + 1 entités (pour détecter le
    dépassement)."""
    items = []
    request = feature_request(layer, expression, [id_field] if id_field else [])
    for feature, geometry in iter_geometries(layer, request, crs):
        items.append((feature.id(), _label(feature, id_field), geometry))
        if len(items) > limit:
            break
    return items


@tool(level=Level.READ, params={
    "polygon_layer_id": Param("string", "Couche de polygones (layer_id) : parcelles, zones…"),
    "point_layer_id": Param("string", "Couche de points (layer_id) : arbres, bâtiments, "
                            "relevés…"),
    "polygon_id_field": Param("string", "Champ identifiant les polygones dans le résultat "
                              "(défaut : fid).", required=False),
    "weight_field": Param("string", "Champ numérique des points à additionner (ex. nombre de "
                          "logements).", required=False),
    "class_field": Param("string", "Champ des points pour un décompte par catégorie (ex. "
                         "essence).", required=False),
    "point_filter": Param("string", "Filtre sur les points. " + FILTER_HELP, required=False),
    "limit": Param("integer", "Polygones renvoyés (les plus peuplés d'abord).", required=False,
                   default=100, minimum=1, maximum=2000),
})
def count_points_in_polygon(polygon_layer_id: str, point_layer_id: str,
                            polygon_id_field: str | None, weight_field: str | None,
                            class_field: str | None, point_filter: str | None,
                            limit: int) -> ToolResult:
    """Compte les points contenus dans chaque polygone (reprojection automatique), avec
    densité par hectare, somme d'un champ et décompte par catégorie. class_count = nombre de
    catégories distinctes (richesse spécifique). Un point sur une limite commune compte pour
    chaque polygone touché. Pour écrire le compte dans une nouvelle
    couche : run_algorithm native:countpointsinpolygon."""
    polygons = _layer(polygon_layer_id, "polygon")
    points = _layer(point_layer_id, "point")
    polygon_id_field = _field(polygons, polygon_id_field)
    weight_field, class_field = _field(points, weight_field), _field(points, class_field)
    index, geometries, attributes = _index_points(points, polygons.crs(), point_filter,
                                                  weight_field, class_field)
    da = distance_area(polygons.crs())
    rows, inside = [], set()
    request = feature_request(polygons, None, [polygon_id_field] if polygon_id_field else [])
    for feature, polygon, hits in _point_hits(iter_geometries(polygons, request), index,
                                              geometries):
        inside.update(hits)
        area_ha = area_m2(da, polygon) / M2_PER_HA
        row: dict[str, Any] = {"fid": feature.id(), "id": _label(feature, polygon_id_field),
                               "count": len(hits), "area_ha": round(area_ha, 4),
                               "density_per_ha": round(len(hits) / area_ha, 4) if area_ha
                               else None}
        if weight_field:
            row["weight_sum"] = round(sum(attributes[h][0] or 0.0 for h in hits), 4)
        if class_field:
            row["by_class"] = dict(Counter(str(attributes[h][1]) for h in hits).most_common())
            row["class_count"] = len(row["by_class"])
        rows.append(row)
    if not rows:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{polygons.name()} ne contient aucun "
                        "polygone.")
    rows.sort(key=lambda r: (-r["count"], str(r["id"])))
    warnings = []
    if len(geometries) - len(inside):
        warnings.append(f"{len(geometries) - len(inside)} point(s) hors de tout polygone.")
    return ToolResult({
        "polygon_count": len(rows), "point_count": len(geometries),
        "points_inside": len(inside), "points_outside": len(geometries) - len(inside),
        "empty_polygons": sum(1 for r in rows if r["count"] == 0),
        "count_stats": describe([r["count"] for r in rows]),
        "results": rows[:limit], "truncated": len(rows) > limit,
    }, warnings)


def _grid(extent: QgsRectangle, size: float):
    """Mailles carrées alignées sur les multiples de size, couvrant l'emprise."""
    x0, y0 = math.floor(extent.xMinimum() / size), math.floor(extent.yMinimum() / size)
    x1 = max(math.ceil(extent.xMaximum() / size), x0 + 1)
    y1 = max(math.ceil(extent.yMaximum() / size), y0 + 1)
    if (x1 - x0) * (y1 - y0) > MAX_GRID_CELLS:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Plus de {MAX_GRID_CELLS} mailles : "
                        "augmente grid_size_m ou filtre les points.")
    for i in range(x0, x1):
        for j in range(y0, y1):
            yield (f"{i * size:.0f}_{j * size:.0f}",
                   QgsGeometry.fromRect(QgsRectangle(i * size, j * size,
                                                     (i + 1) * size, (j + 1) * size)))


@tool(level=Level.CREATE, params={
    "point_layer_id": Param("string", "Couche des observations (layer_id), ex. sortie de "
                            "import_field_data."),
    "polygon_layer_id": Param("string", "Polygones d'habitat (layer_id). Sinon : "
                              "grid_size_m.", required=False),
    "grid_size_m": Param("number", "Côté des mailles carrées (m), générées sur l'emprise des "
                         "observations (SCR projeté requis).", required=False, minimum=1),
    "taxon_field": Param("string", "Champ du taxon des points (richesse spécifique), ex. "
                         "taxon.", required=False),
    "count_field": Param("string", "Champ de l'effectif des points (somme ; vide = 0), ex. "
                         "effectif.", required=False),
    "point_filter": Param("string", "Filtre sur les points. " + FILTER_HELP, required=False),
    "output_name": OUTPUT_NAME,
})
def count_observations(point_layer_id: str, polygon_layer_id: str | None,
                       grid_size_m: float | None, taxon_field: str | None,
                       count_field: str | None,
                       point_filter: str | None, output_name: str | None) -> ToolResult:
    """Couche de synthèse des observations par polygone d'habitat ou par maille, à
    cartographier : nb_obs, richesse (taxons distincts), effectif (somme), taxons (liste),
    plus les champs des polygones d'habitat. Pour un simple tableau sans couche :
    count_points_in_polygon."""
    if bool(polygon_layer_id) == bool(grid_size_m):
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique soit polygon_layer_id, soit "
                        "grid_size_m.")
    points = _layer(point_layer_id, "point")
    taxon_field = _field(points, taxon_field)
    count_field = _field(points, count_field)
    if polygon_layer_id:
        polygons = _layer(polygon_layer_id, "polygon")
        crs, base_fields = polygons.crs(), polygons.fields()
        cells: Any = iter_geometries(polygons, feature_request(polygons))
    else:
        crs, base_fields = points.crs(), QgsFields()
        if crs.isGeographic():
            raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{points.name()} est en degrés : "
                            "reprojette-la (reproject_layer) avant de mailler.")
        base_fields.append(make_field("maille", "string", 30))
    index, geometries, attributes = _index_points(points, crs, point_filter, count_field,
                                                  taxon_field)
    if not geometries:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune observation à compter.")
    if grid_size_m:
        extent = QgsRectangle()
        for geometry in geometries.values():
            extent.combineExtentWith(geometry.boundingBox())
        cells = _grid(extent, float(grid_size_m))

    fields = QgsFields(base_fields)
    added = {}
    for name, type_name in (("nb_obs", "integer"), ("richesse", "integer"),
                            ("effectif", "real"), ("taxons", "string")):
        added[name] = unique_field_name(name, fields.names())
        fields.append(make_field(added[name], type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("observations", fields,
                                                      Qgis.WkbType.MultiPolygon, crs)
    features, inside = [], set()
    for item, polygon, hits in _point_hits(cells, index, geometries):
        inside.update(hits)
        taxa = sorted({str(attributes[h][1]) for h in hits if attributes[h][1] is not None})
        feature = QgsFeature(fields)
        polygon.convertToMultiType()
        feature.setGeometry(polygon)
        if isinstance(item, QgsFeature):
            for name in base_fields.names():
                feature[name] = item[name]
        else:
            feature["maille"] = item
        feature[added["nb_obs"]] = len(hits)
        feature[added["richesse"]] = len(taxa) if taxon_field else None
        feature[added["effectif"]] = (sum(attributes[h][0] or 0.0 for h in hits)
                                      if count_field else None)
        feature[added["taxons"]] = "; ".join(taxa) if taxon_field else None
        features.append(feature)
    if not memory.dataProvider().addFeatures(features):
        raise ToolError(ErrorCode.INTERNAL_ERROR, "Création de la couche impossible.",
                        {"error": memory.dataProvider().lastError()})

    default = f"obs_maille_{float(grid_size_m):g}m" if grid_size_m else "obs_par_habitat"
    result = save_to_project(memory, output_name or default)
    counts = [f[added["nb_obs"]] for f in features]
    richness = [f[added["richesse"]] for f in features] if taxon_field else []
    all_taxa = {str(a[1]) for a in attributes.values() if a[1] is not None}
    result.data.update({
        "units": len(features), "units_with_obs": sum(1 for c in counts if c),
        "observations": len(geometries), "observations_inside": len(inside),
        "taxa_total": len(all_taxa) if taxon_field else None,
        "max_richness": max(richness, default=None), "fields": added,
        "next_step": f"apply_graduated_style sur {added['richesse']} ou {added['nb_obs']}.",
    })
    if len(geometries) - len(inside):
        result.warnings.append(f"{len(geometries) - len(inside)} observation(s) hors de tout "
                               "polygone.")
    if not taxon_field:
        result.warnings.append("Sans taxon_field : richesse non calculée.")
    return result

@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche de points (layer_id)."),
    "method": Param("string", "ordered : relie les points dans l'ordre de order_field (levé "
                    "de sommets d'une parcelle) ; convex_hull : enveloppe convexe ; "
                    "concave_hull : enveloppe concave (suit mieux la forme du nuage).",
                    required=False, default="convex_hull", enum=HULL_METHODS),
    "group_field": Param("string", "Un polygone par valeur de ce champ (ex. n° de parcelle). "
                         "Absent : un seul polygone.", required=False),
    "order_field": Param("string", "Champ d'ordre des sommets (obligatoire pour ordered), "
                         "ex. n° de point.", required=False),
    "concave_ratio": Param("number", "concave_hull : 0 = très ajusté, 1 = enveloppe "
                           "convexe.", required=False, default=0.3, minimum=0, maximum=1),
    "filter_expression": Param("string", "Filtre sur les points. " + FILTER_HELP,
                               required=False),
    "output_name": OUTPUT_NAME,
})
def points_to_polygon(layer_id: str, method: str, group_field: str | None,
                      order_field: str | None, concave_ratio: float,
                      filter_expression: str | None, output_name: str | None) -> ToolResult:
    """Construit des polygones à partir de points (nouvelle couche dans mcp_outputs/) : un par
    groupe, avec nb_points, surface_m2 et perimetre (ellipsoïdaux). Ex. : sommets levés au GPS
    → parcelle, nuage d'observations → aire de répartition."""
    layer = _layer(layer_id, "point")
    if method == "ordered" and not order_field:
        raise ToolError(ErrorCode.INVALID_PARAMS, "La méthode ordered exige order_field.")
    group_field, order_field = _field(layer, group_field), _field(layer, order_field)
    groups: dict[Any, list[tuple[Any, float, float]]] = {}
    request = feature_request(layer, filter_expression,
                              [f for f in (group_field, order_field) if f])
    for feature, geometry in iter_geometries(layer, request):
        key = group_key(feature[group_field]) if group_field else None
        order = to_json_value(feature[order_field]) if order_field else None
        for vertex in geometry.vertices():  # couches multipoints comprises
            groups.setdefault(key, []).append((order, vertex.x(), vertex.y()))
    if not groups:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} : aucun point retenu.")

    fields = QgsFields()
    if group_field:
        fields.append(make_field("groupe", "string", 80))
    for name, type_name in (("nb_points", "integer"), ("surface_m2", "real"),
                            ("perimetre", "real")):
        fields.append(make_field(name, type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("points_to_polygon", fields,
                                                      Qgis.WkbType.MultiPolygon, layer.crs())
    da = distance_area(layer.crs())
    features, skipped, repaired = [], [], 0
    for key, pts in groups.items():
        polygon = _hull(method, pts, concave_ratio)
        if polygon is None:
            skipped.append(str(key))
            continue
        if not polygon.isGeosValid():  # ordre des sommets qui se croise (nœud papillon)
            fixed = polygon.makeValid().convertToType(Qgis.GeometryType.Polygon, True)
            if fixed is not None and not fixed.isNull():
                polygon = fixed
            repaired += 1
        polygon.convertToMultiType()
        feature = QgsFeature(fields)
        if group_field:
            feature["groupe"] = "" if key is None else str(key)
        feature["nb_points"] = len(pts)
        feature["surface_m2"] = round(area_m2(da, polygon), 2)
        feature["perimetre"] = round(perimeter_m(da, polygon), 2)
        feature.setGeometry(polygon)
        features.append(feature)
    if not features:
        raise ToolError(ErrorCode.INVALID_GEOMETRY, "Aucun polygone constructible : il faut au "
                        "moins 3 points non alignés par groupe.")
    memory.dataProvider().addFeatures(features)

    result = save_to_project(memory, output_name or f"{method}_{layer.name()}")
    result.data.update({"method": method, "polygons": len(features),
                        "skipped_groups": skipped[:50]})
    if skipped:
        result.warnings.append(f"{len(skipped)} groupe(s) ignoré(s) : moins de 3 points non "
                               "alignés.")
    if repaired:
        result.warnings.append(f"{repaired} polygone(s) auto-intersecté(s) réparé(s) : vérifie "
                               "l'ordre des points (order_field).")
    return result


def _hull(method: str, points: list[tuple[Any, float, float]],
          concave_ratio: float) -> QgsGeometry | None:
    """Polygone construit selon la méthode, ou None si les points ne le permettent pas."""
    if method == "ordered":
        try:
            ring = proximity.ordered_ring(points)
        except ValueError:
            return None
        polygon = QgsGeometry.fromPolygonXY([[QgsPointXY(x, y) for x, y in ring]])
    else:
        cloud = QgsGeometry.fromMultiPointXY([QgsPointXY(x, y) for _, x, y in points])
        polygon = (cloud.convexHull() if method == "convex_hull"
                   else cloud.concaveHull(concave_ratio, False))
    if polygon.isNull() or polygon.type() != Qgis.GeometryType.Polygon:
        return None  # moins de 3 points, ou points alignés (l'enveloppe est une ligne)
    return polygon


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche des entités de départ (layer_id)."),
    "target_layer_id": Param("string", "Couche où chercher les voisins (layer_id). Absent : la "
                             "même couche (l'entité elle-même est exclue).", required=False),
    "k": Param("integer", "Nombre de voisins par entité.", required=False, default=1,
               minimum=1, maximum=10),
    "max_distance_m": Param("number", "Ignorer les voisins au-delà de cette distance (m).",
                            required=False, minimum=0),
    "source_id_field": Param("string", "Champ identifiant les entités de départ (défaut : "
                             "fid).", required=False),
    "target_id_field": Param("string", "Champ identifiant les voisins (défaut : fid).",
                             required=False),
    "filter_expression": Param("string", "Filtre sur les entités de départ. " + FILTER_HELP,
                               required=False),
    "target_filter": Param("string", "Filtre sur les voisins possibles.", required=False),
    "max_features": Param("integer", "Nombre maximal d'entités de départ.", required=False,
                          default=500, minimum=1, maximum=5000),
    "unit": UNIT,
})
def nearest_features(layer_id: str, target_layer_id: str | None, k: int,
                     max_distance_m: float | None, source_id_field: str | None,
                     target_id_field: str | None, filter_expression: str | None,
                     target_filter: str | None, max_features: int, unit: str) -> ToolResult:
    """Plus proches voisins de chaque entité, dans la même couche ou une autre (reprojection
    automatique) : distance bord à bord sur l'ellipsoïde. Ex. : forage le plus proche de chaque
    habitation, distance entre arbres remarquables."""
    source = get_vector_layer(layer_id)
    target = get_vector_layer(target_layer_id) if target_layer_id else source
    same = target.id() == source.id()
    source_id_field = _field(source, source_id_field)
    target_id_field = _field(target, target_id_field)
    sources = _collect(source, source_id_field, filter_expression, None, max_features)
    warnings = []
    if len(sources) > max_features:
        sources = sources[:max_features]
        warnings.append(f"Limité aux {max_features} premières entités : affine "
                        "filter_expression.")

    index = QgsSpatialIndex(QgsSpatialIndex.Flag.FlagStoreFeatureGeometries)
    targets: dict[int, tuple[Any, QgsGeometry]] = {}
    request = feature_request(target, target_filter, [target_id_field] if target_id_field else [])
    for feature, geometry in iter_geometries(target, request, source.crs()):
        copy = QgsFeature(feature.id())
        copy.setGeometry(geometry)
        index.addFeature(copy)
        targets[feature.id()] = (_label(feature, target_id_field), geometry)
    if not targets:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{target.name()} : aucun voisin possible.")

    geographic = source.crs().isGeographic()
    search_radius = 0.0  # 0 = sans limite pour QgsSpatialIndex
    if max_distance_m is not None:
        search_radius = (max_distance_m / METERS_PER_DEGREE * 1.5 if geographic
                         else max_distance_m)
    da = distance_area(source.crs())
    results, first, isolated = [], [], 0
    for fid, label, geometry in sources:
        # L'index classe en distance planaire : quelques candidats de plus, puis tri ellipsoïdal.
        candidates = index.nearestNeighbor(geometry, k + 5 + int(same), search_radius)
        found = proximity.nearest(
            ((other, _distance_m(da, geometry, targets[other][1]))
             for other in candidates if not (same and other == fid)), k, max_distance_m)
        if not found:
            isolated += 1
        else:
            first.append(found[0][1])
        results.append({"fid": fid, "id": label, "neighbors": [
            {"fid": other, "id": targets[other][0],
             "distance": round(convert_length(distance, unit), 4)} for other, distance in found]})
    if isolated:
        warnings.append(f"{isolated} entité(s) sans voisin"
                        + (f" à moins de {max_distance_m:g} m." if max_distance_m else "."))
    stats = describe([convert_length(d, unit) for d in first])
    return ToolResult({"source_layer": source.name(), "target_layer": target.name(), "k": k,
                       "unit": unit, "nearest_distance_stats": stats, "results": results},
                      warnings)


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche des lignes de la matrice (layer_id)."),
    "target_layer_id": Param("string", "Couche des colonnes (layer_id). Absent : la même "
                             "couche (matrice carrée symétrique).", required=False),
    "source_id_field": Param("string", "Champ des libellés de lignes (défaut : fid).",
                             required=False),
    "target_id_field": Param("string", "Champ des libellés de colonnes (défaut : fid).",
                             required=False),
    "filter_expression": Param("string", "Filtre sur les lignes. " + FILTER_HELP,
                               required=False),
    "target_filter": Param("string", "Filtre sur les colonnes.", required=False),
    "max_features": Param("integer", "Nombre maximal d'entités de chaque côté.", required=False,
                          default=100, minimum=2, maximum=300),
    "output_format": Param("string", "matrix : tableau lignes x colonnes ; pairs : liste de "
                           "paires triée par distance.", required=False, default="matrix",
                           enum=MATRIX_FORMATS),
    "unit": UNIT,
})
def distance_matrix(layer_id: str, target_layer_id: str | None, source_id_field: str | None,
                    target_id_field: str | None, filter_expression: str | None,
                    target_filter: str | None, max_features: int, output_format: str,
                    unit: str) -> ToolResult:
    """Distances de chaque entité à chaque autre (bord à bord, ellipsoïdales). Pour un fichier
    tableur, passe le résultat pairs à export_table (paramètre table)."""
    source = get_vector_layer(layer_id)
    target = get_vector_layer(target_layer_id) if target_layer_id else source
    same = target.id() == source.id()
    source_id_field = _field(source, source_id_field)
    target_id_field = _field(target, target_id_field)
    rows = _collect(source, source_id_field, filter_expression, None, max_features)
    columns = rows if same and target_filter is None else _collect(
        target, target_id_field, target_filter, source.crs(), max_features)
    if len(rows) > max_features or len(columns) > max_features:
        raise ToolError(ErrorCode.TOO_MANY_FEATURES,
                        f"Plus de {max_features} entités d'un côté : filtre (filter_expression, "
                        "target_filter) ou augmente max_features (300 au plus).")
    if not rows or not columns:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune entité à comparer.")

    da = distance_area(source.crs())
    distances: dict[tuple[int, int], float] = {}
    for row_fid, _, row_geometry in rows:
        for col_fid, _, col_geometry in columns:
            if same and (col_fid, row_fid) in distances:  # matrice symétrique
                distances[(row_fid, col_fid)] = distances[(col_fid, row_fid)]
            elif not (same and col_fid == row_fid):
                distances[(row_fid, col_fid)] = convert_length(
                    _distance_m(da, row_geometry, col_geometry), unit)
    data: dict[str, Any] = {"source_layer": source.name(), "target_layer": target.name(),
                            "unit": unit, "rows": len(rows), "columns": len(columns),
                            "stats": describe(list(distances.values()))}
    warnings = []
    if output_format == "matrix":
        data["matrix"] = proximity.distance_matrix([(fid, label) for fid, label, _ in rows],
                                                   [(fid, label) for fid, label, _ in columns],
                                                   distances, 4)
    else:
        labels = {fid: label for fid, label, _ in rows} | {fid: label for fid, label, _ in columns}
        pairs = sorted(((d, a, b) for (a, b), d in distances.items() if not (same and b < a)),
                       key=lambda item: (item[0], item[1], item[2]))
        data["pairs"] = [{"from": labels[a], "to": labels[b], "distance": round(d, 4)}
                         for d, a, b in pairs[:MAX_PAIRS]]
        if len(pairs) > MAX_PAIRS:
            warnings.append(f"{len(pairs)} paires : seules les {MAX_PAIRS} plus courtes sont "
                            "renvoyées.")
    return ToolResult(data, warnings)
