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
    add_to_memory,
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
    polygon_parts,
    prepare_expression,
    require_field,
    to_json_value,
)
from .features import FILTER_HELP
from .geoprocessing import OUTPUT_NAME
from .outputs import save_to_project

HULL_METHODS = ("ordered", "convex_hull", "concave_hull", "buffer")
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


def _grid(geometries: dict[int, QgsGeometry], size: float):
    """(id, maille, fids des points) pour chaque maille carrée alignée sur les multiples de
    size, sur l'emprise des points. Chaque point compte dans une seule maille (bords ouest et
    sud inclus), même s'il tombe sur une limite."""
    cells: dict[tuple[int, int], list[int]] = {}
    for fid, geometry in geometries.items():
        point = geometry.boundingBox().center()
        key = (math.floor(point.x() / size), math.floor(point.y() / size))
        cells.setdefault(key, []).append(fid)
    xs, ys = [k[0] for k in cells], [k[1] for k in cells]
    if (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1) > MAX_GRID_CELLS:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Plus de {MAX_GRID_CELLS} mailles : "
                        "augmente grid_size_m ou filtre les points.")
    for i in range(min(xs), max(xs) + 1):
        for j in range(min(ys), max(ys) + 1):
            yield (f"{i * size:.0f}_{j * size:.0f}",
                   QgsGeometry.fromRect(QgsRectangle(i * size, j * size,
                                                     (i + 1) * size, (j + 1) * size)),
                   cells.get((i, j), []))

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
    "protected_expression": Param("string", "Expression QGIS vraie pour une observation "
                                  "d'espèce protégée, ex. \"taxon\" IN ('Tec-tec', 'Gecko "
                                  "vert de Manapany') ou \"statut\" = 'PN'. Requiert "
                                  "taxon_field.", required=False),
    "invasive_expression": Param("string", "Expression QGIS vraie pour une espèce exotique "
                                 "envahissante (EEE), même forme. Requiert taxon_field.",
                                 required=False),
    "point_filter": Param("string", "Filtre sur les points. " + FILTER_HELP, required=False),
    "output_name": OUTPUT_NAME,
})
def count_observations(point_layer_id: str, polygon_layer_id: str | None,
                       grid_size_m: float | None, taxon_field: str | None,
                       count_field: str | None, protected_expression: str | None,
                       invasive_expression: str | None,
                       point_filter: str | None, output_name: str | None) -> ToolResult:
    """Couche de synthèse des observations par polygone d'habitat ou par maille, à
    cartographier : nb_obs, richesse (taxons distincts), effectif (somme), taxons (liste),
    plus les champs des polygones d'habitat. Avec protected_expression / invasive_expression :
    nb_prot, sp_prot, nb_eee, sp_eee (taxons protégés / EEE distincts et leur liste). Les
    listes d'espèces ne sont pas fournies par Cynogis : demande-les à l'utilisateur (arrêtés
    de protection, liste EEE du territoire). Mailles INPN 10 km : grid_size_m=10000 en
    EPSG:2975 / EPSG:4471. Pour un simple tableau sans couche : count_points_in_polygon."""
    if bool(polygon_layer_id) == bool(grid_size_m):
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique soit polygon_layer_id, soit "
                        "grid_size_m.")
    points = _layer(point_layer_id, "point")
    taxon_field = _field(points, taxon_field)
    count_field = _field(points, count_field)
    statuses = {key: text for key, text in (("prot", protected_expression),
                                            ("eee", invasive_expression)) if text}
    if statuses and not taxon_field:
        raise ToolError(ErrorCode.INVALID_PARAMS, "protected_expression et "
                        "invasive_expression requièrent taxon_field.")
    flagged: dict[str, set[int]] = {}
    for key, text in statuses.items():
        expression, context = prepare_expression(text, points, f"{key}_expression")
        flagged[key] = set()
        for feature in points.getFeatures(feature_request(points, point_filter, None, False)):
            context.setFeature(feature)
            if expression.evaluate(context):
                flagged[key].add(feature.id())
    if polygon_layer_id:
        polygons = _layer(polygon_layer_id, "polygon")
        crs, base_fields = polygons.crs(), polygons.fields()
        cells = iter_geometries(polygons, feature_request(polygons))
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
    units = (_grid(geometries, float(grid_size_m)) if grid_size_m
             else _point_hits(cells, index, geometries))

    fields = QgsFields(base_fields)
    added = {}
    for name, type_name in (("nb_obs", "integer"), ("richesse", "integer"),
                            ("effectif", "real"), ("taxons", "string"),
                            *((f"{prefix}_{key}", kind) for key in statuses
                              for prefix, kind in (("nb", "integer"), ("sp", "string")))):
        added[name] = unique_field_name(name, fields.names())
        fields.append(make_field(added[name], type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("observations", fields,
                                                      Qgis.WkbType.MultiPolygon, crs)
    features, inside = [], set()
    for item, polygon, hits in units:
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
        for key, fids in flagged.items():
            special = sorted({str(attributes[h][1]) for h in hits
                              if h in fids and attributes[h][1] is not None})
            feature[added[f"nb_{key}"]] = len(special)
            feature[added[f"sp_{key}"]] = "; ".join(special)
        features.append(feature)
    notes = add_to_memory(memory, features)

    default = f"obs_maille_{float(grid_size_m):g}m" if grid_size_m else "obs_par_habitat"
    result = save_to_project(memory, output_name or default)
    result.warnings.extend(notes)
    counts = [f[added["nb_obs"]] for f in features]
    richness = [f[added["richesse"]] for f in features] if taxon_field else []
    all_taxa = {str(a[1]) for a in attributes.values() if a[1] is not None}
    result.data.update({
        "units": len(features), "units_with_obs": sum(1 for c in counts if c),
        "observations": len(geometries), "observations_inside": len(inside),
        "taxa_total": len(all_taxa) if taxon_field else None,
        "max_richness": max(richness, default=None), "fields": added,
        "flagged_observations": {key: len(fids & set(geometries))
                                 for key, fids in flagged.items()},
        "next_step": f"apply_graduated_style sur {added['richesse']} ou {added['nb_obs']}.",
    })
    if len(geometries) - len(inside):
        result.warnings.append(f"{len(geometries) - len(inside)} observation(s) hors de tout "
                               "polygone.")
    if not taxon_field:
        result.warnings.append("Sans taxon_field : richesse non calculée.")
    return result

def _eee_patches(layer: QgsVectorLayer, crs: Any, expression: str | None,
                 taxon_field: str | None, cover_field: str | None):
    """Index des taches d'EEE (dans crs) et (géométrie, taxon, recouvrement %) par fid."""
    index = QgsSpatialIndex()
    patches: dict[int, tuple[QgsGeometry, Any, float | None]] = {}
    request = feature_request(layer, expression, [f for f in (taxon_field, cover_field) if f])
    for feature, geometry in iter_geometries(layer, request, crs):
        cover = to_float(to_json_value(feature[cover_field])) if cover_field else None
        patches[feature.id()] = (geometry, group_key(feature[taxon_field]) if taxon_field
                                 else None, cover)
        index.addFeature(feature.id(), geometry.boundingBox())
    return index, patches


@tool(level=Level.CREATE, params={
    "polygon_layer_id": Param("string", "Polygones d'analyse (layer_id) : habitats, parcelles, "
                              "aire d'étude…"),
    "eee_layer_id": Param("string", "Observations (points) ou taches (polygones) d'espèces "
                          "exotiques envahissantes (layer_id), ex. sortie de "
                          "taxon_status_join."),
    "eee_filter": Param("string", "Entités à retenir comme EEE. Défaut : \"eee\" = 1 si le "
                        "champ eee existe (taxon_status_join), sinon toutes. " + FILTER_HELP,
                        required=False),
    "taxon_field": Param("string", "Champ du taxon (liste et nombre d'espèces).",
                         required=False),
    "cover_field": Param("string", "Taches : champ du recouvrement de l'EEE dans la tache "
                         "(%, 0-100). Absent : tache entièrement envahie.", required=False),
    "output_name": OUTPUT_NAME,
})
def invasive_species_map(polygon_layer_id: str, eee_layer_id: str, eee_filter: str | None,
                         taxon_field: str | None, cover_field: str | None,
                         output_name: str | None) -> ToolResult:
    """Pression des espèces exotiques envahissantes par polygone, en couche à cartographier.
    Points : eee_nb (observations), eee_dens (observations / ha). Taches : eee_nb (taches),
    eee_ha (surface envahie, pondérée par cover_field ; sans lui, taches qui se chevauchent
    comptées une fois) et eee_rec (% du polygone). Dans les deux cas : eee_nsp (espèces) et
    eee_taxa. Les champs des polygones sont conservés."""
    polygons = _layer(polygon_layer_id, "polygon")
    eee = get_vector_layer(eee_layer_id)
    kind = geometry_kind(eee)
    if kind not in ("point", "polygon"):
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{eee.name()} doit contenir des points "
                        "(observations) ou des polygones (taches).")
    taxon_field, cover_field = _field(eee, taxon_field), _field(eee, cover_field)
    if cover_field and kind == "point":
        raise ToolError(ErrorCode.INVALID_PARAMS, "cover_field ne s'applique qu'aux taches "
                        "(polygones).")
    warnings = []
    if eee_filter is None:
        if eee.fields().indexOf("eee") >= 0:
            eee_filter = '"eee" = 1'
        else:
            warnings.append(f"Ni eee_filter ni champ eee : toutes les entités de {eee.name()} "
                            "sont considérées comme des EEE.")
    if kind == "point":
        index, geometries, attributes = _index_points(eee, polygons.crs(), eee_filter, None,
                                                      taxon_field)
        total = len(geometries)
    else:
        index, patches = _eee_patches(eee, polygons.crs(), eee_filter, taxon_field,
                                      cover_field)
        total = len(patches)
    if not total:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune EEE retenue : vérifie eee_filter.",
                        {"eee_filter": eee_filter})

    fields = QgsFields(polygons.fields())
    added = {}
    for name, type_name in (("eee_nb", "integer"), ("eee_dens", "real"), ("eee_ha", "real"),
                            ("eee_rec", "real"), ("eee_nsp", "integer"),
                            ("eee_taxa", "string")):
        added[name] = unique_field_name(name, fields.names())
        fields.append(make_field(added[name], type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("eee", fields, polygons.wkbType(),
                                                      polygons.crs())
    da = distance_area(polygons.crs())
    features: list[QgsFeature] = []
    taxa_total: Counter = Counter()
    over = 0
    for feature, polygon in iter_geometries(polygons, feature_request(polygons)):
        area = area_m2(da, polygon)
        values: dict[str, Any] = {}
        taxa: Counter = Counter()
        if kind == "point":
            for _, _, hits in _point_hits([(None, polygon)], index, geometries):
                taxa.update(attributes[h][1] for h in hits if attributes[h][1] is not None)
                values["eee_nb"] = len(hits)
                values["eee_dens"] = round(len(hits) / (area / M2_PER_HA), 4) if area else None
        else:
            pieces = []
            for fid in index.intersects(polygon.boundingBox()):
                geometry, taxon, cover = patches[fid]
                piece = polygon.intersection(geometry)
                if not piece.isEmpty() and area_m2(da, piece) > 0:
                    pieces.append((piece, taxon, cover))
            if cover_field:
                invaded = sum(area_m2(da, piece) * max(min(cover or 0.0, 100.0), 0.0) / 100.0
                              for piece, _, cover in pieces)
            elif pieces:
                invaded = area_m2(da, QgsGeometry.unaryUnion([p for p, _, _ in pieces]))
            else:
                invaded = 0.0
            if area and invaded > area * 1.0001:
                over += 1
                invaded = area
            for piece, taxon, _ in pieces:
                if taxon is not None:
                    taxa[taxon] += area_m2(da, piece) / M2_PER_HA
            values["eee_nb"] = len(pieces)
            values["eee_ha"] = round(invaded / M2_PER_HA, 4)
            values["eee_rec"] = round(invaded / area * 100.0, 2) if area else None
        taxa_total.update(taxa)
        values["eee_nsp"] = len(taxa) if taxon_field else None
        values["eee_taxa"] = "; ".join(str(t) for t, _ in taxa.most_common()) or None
        copy = QgsFeature(fields)
        copy.setGeometry(polygon)
        for name in polygons.fields().names():
            copy[name] = feature[name]
        for name, value in values.items():
            copy[added[name]] = value
        features.append(copy)
    notes = add_to_memory(memory, features)

    result = save_to_project(memory, output_name or f"eee_{polygons.name()}")
    result.warnings.extend(notes)
    key = added["eee_dens"] if kind == "point" else added["eee_rec"]
    ranked = sorted(features, key=lambda f: -(f[key] or 0))
    result.data.update({
        "eee_source": kind, "eee_filter": eee_filter, "eee_features": total,
        "polygons": len(features),
        "polygons_invaded": sum(1 for f in features if f[added["eee_nb"]]),
        "fields": added, "ranking_field": key,
        "most_invaded": [{key: f[key], "taxa": f[added["eee_taxa"]],
                          **{n: to_json_value(f[n]) for n in polygons.fields().names()[:3]}}
                         for f in ranked[:10] if f[key]],
        "taxa": {str(t): round(n, 4) for t, n in taxa_total.most_common(30)},
        "taxa_unit": "observations" if kind == "point" else "ha (surface brute des taches)",
        "next_step": f"apply_graduated_style sur {key}.",
    })
    if over:
        warnings.append(f"{over} polygone(s) avec un recouvrement cumulé > 100 % (taches qui "
                        "se chevauchent) : ramené à 100 %.")
    result.warnings[:0] = warnings
    return result

@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche de points (layer_id)."),
    "method": Param("string", "ordered : relie les points dans l'ordre de order_field (levé "
                    "de sommets d'une parcelle) ; convex_hull : enveloppe convexe ; "
                    "concave_hull : enveloppe concave (suit mieux la forme du nuage) ; "
                    "buffer : polygone de présence (union des tampons de buffer_m autour des "
                    "points).", required=False, default="convex_hull", enum=HULL_METHODS),
    "group_field": Param("string", "Un polygone par valeur de ce champ (ex. n° de parcelle, "
                         "taxon pour une aire par espèce). Absent : un seul polygone.",
                         required=False),
    "order_field": Param("string", "Champ d'ordre des sommets (obligatoire pour ordered), "
                         "ex. n° de point.", required=False),
    "concave_ratio": Param("number", "concave_hull : 0 = très ajusté, 1 = enveloppe "
                           "convexe.", required=False, default=0.3, minimum=0, maximum=1),
    "buffer_m": Param("number", "Marge (m, SCR projeté) : rayon du polygone de présence "
                      "(buffer) ; pour les enveloppes, élargissement, et polygone de présence "
                      "pour les groupes de moins de 3 points au lieu de les ignorer.",
                      required=False, default=0, minimum=0, maximum=100000),
    "filter_expression": Param("string", "Filtre sur les points. " + FILTER_HELP,
                               required=False),
    "output_name": OUTPUT_NAME,
})
def points_to_polygon(layer_id: str, method: str, group_field: str | None,
                      order_field: str | None, concave_ratio: float, buffer_m: float,
                      filter_expression: str | None, output_name: str | None) -> ToolResult:
    """Construit des polygones à partir de points (nouvelle couche dans mcp_outputs/) : un par
    groupe, avec nb_points, surface_m2 et perimetre (ellipsoïdaux), et methode (enveloppe ou
    présence de repli). Ex. : sommets levés au GPS → parcelle ; observations avec
    group_field = taxon → aire de répartition (enveloppe) ou polygone de présence (buffer)
    par espèce."""
    layer = _layer(layer_id, "point")
    if method == "ordered" and not order_field:
        raise ToolError(ErrorCode.INVALID_PARAMS, "La méthode ordered exige order_field.")
    if method == "buffer" and not buffer_m:
        raise ToolError(ErrorCode.INVALID_PARAMS, "La méthode buffer exige buffer_m > 0.")
    if buffer_m and method == "ordered":
        raise ToolError(ErrorCode.INVALID_PARAMS, "buffer_m ne s'applique pas à ordered.")
    if buffer_m and layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{layer.name()} est en degrés : "
                        "reprojette-la (reproject_layer) pour une marge en mètres.")
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
                            ("perimetre", "real"), ("methode", "string")):
        fields.append(make_field(name, type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("points_to_polygon", fields,
                                                      Qgis.WkbType.MultiPolygon, layer.crs())
    da = distance_area(layer.crs())
    features, skipped, fallback, repaired = [], [], [], 0
    for key, pts in groups.items():
        polygon = _hull(method, pts, concave_ratio, buffer_m)
        used = method
        if polygon is None and buffer_m:  # pas d'enveloppe possible : polygone de présence
            polygon, used = _hull("buffer", pts, concave_ratio, buffer_m), "buffer"
            fallback.append(str(key))
        if polygon is None:
            skipped.append(str(key))
            continue
        if not polygon.isGeosValid():  # ordre des sommets qui se croise (nœud papillon)
            fixed = polygon_parts(polygon.makeValid())
            if fixed is not None:
                polygon = fixed
            repaired += 1
        polygon.convertToMultiType()
        feature = QgsFeature(fields)
        if group_field:
            feature["groupe"] = "" if key is None else str(key)
        feature["nb_points"] = len(pts)
        feature["surface_m2"] = round(area_m2(da, polygon), 2)
        feature["perimetre"] = round(perimeter_m(da, polygon), 2)
        feature["methode"] = used
        feature.setGeometry(polygon)
        features.append(feature)
    if not features:
        raise ToolError(ErrorCode.INVALID_GEOMETRY, "Aucun polygone constructible : il faut au "
                        "moins 3 points non alignés par groupe.")
    notes = add_to_memory(memory, features)

    result = save_to_project(memory, output_name or f"{method}_{layer.name()}")
    result.warnings.extend(notes)
    result.data.update({"method": method, "buffer_m": buffer_m, "polygons": len(features),
                        "skipped_groups": skipped[:50], "presence_fallback": fallback[:50]})
    if fallback:
        result.warnings.append(f"{len(fallback)} groupe(s) sans enveloppe possible (moins de "
                               "3 points non alignés) : polygone de présence "
                               f"({buffer_m:g} m) à la place.")
    if skipped:
        result.warnings.append(f"{len(skipped)} groupe(s) ignoré(s) : moins de 3 points non "
                               "alignés (buffer_m > 0 pour un polygone de présence).")
    if repaired:
        result.warnings.append(f"{repaired} polygone(s) auto-intersecté(s) réparé(s) : vérifie "
                               "l'ordre des points (order_field).")
    return result


def _hull(method: str, points: list[tuple[Any, float, float]], concave_ratio: float,
          buffer_m: float = 0.0) -> QgsGeometry | None:
    """Polygone construit selon la méthode (élargi de buffer_m), ou None si les points ne le
    permettent pas."""
    if method == "buffer":
        cloud = QgsGeometry.fromMultiPointXY([QgsPointXY(x, y) for _, x, y in points])
        return cloud.buffer(buffer_m, 16)
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
    return polygon.buffer(buffer_m, 16) if buffer_m else polygon


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
