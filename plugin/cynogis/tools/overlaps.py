from __future__ import annotations

from typing import Any

from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsProject,
    QgsSpatialIndex,
    QgsWkbTypes,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.units import AREA_UNITS, convert_area
from .common import (
    area_m2,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    require_field,
)
from .features import FILTER_HELP
from .geoprocessing import OUTPUT_NAME
from .outputs import run_to_project


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche de polygones à contrôler (layer_id)."),
    "other_layer_id": Param("string", "Seconde couche de polygones. Si absente : chevauchements "
                            "internes à layer_id.", required=False),
    "min_area_m2": Param("number", "Surface minimale d'un chevauchement en m² (ignore les "
                         "micro-recouvrements dus aux arrondis).", required=False, default=0.01,
                         minimum=0),
    "area_unit": Param("string", "Unité des surfaces renvoyées.", required=False, default="m2",
                       enum=tuple(AREA_UNITS)),
    "filter_expression": Param("string", "Filtre sur layer_id. " + FILTER_HELP, required=False),
    "limit": Param("integer", "Nombre max de paires renvoyées (les plus grandes d'abord).",
                   required=False, default=100, minimum=1, maximum=500),
})
def detect_overlaps(layer_id: str, other_layer_id: str | None, min_area_m2: float,
                    area_unit: str, filter_expression: str | None, limit: int) -> ToolResult:
    """Détecte les chevauchements entre polygones : à l'intérieur d'une couche, ou entre deux
    couches (reprojection automatique). Renvoie les paires de fid qui se chevauchent avec la
    surface commune (mesure ellipsoïdale), triées par surface décroissante, et la surface totale.
    Pour voir les entités concernées : get_features avec filter_expression='$id IN (…)'."""
    layer_a = get_vector_layer(layer_id)
    internal = other_layer_id is None or other_layer_id == layer_id
    layer_b = layer_a if internal else get_vector_layer(other_layer_id)
    for lyr in (layer_a, layer_b):
        if geometry_kind(lyr) != "polygon":
            raise ToolError(ErrorCode.INVALID_PARAMS, f"{lyr.name()} n'est pas une couche de "
                            "polygones.")
    da = distance_area(layer_a.crs(), "ellipsoidal")
    transform = None
    if not internal and layer_b.crs() != layer_a.crs():
        transform = QgsCoordinateTransform(layer_b.crs(), layer_a.crs(), QgsProject.instance())

    # 1. Index spatial de la couche B, géométries gardées en mémoire (dans le SCR de A)
    if internal:
        request_b = feature_request(layer_a, filter_expression, [], True)
    else:
        request_b = QgsFeatureRequest()
        request_b.setNoAttributes()
    index = QgsSpatialIndex()
    geoms_b: dict[int, QgsGeometry] = {}
    transform_failures = 0
    for feature in layer_b.getFeatures(request_b):
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            continue
        geom = QgsGeometry(geom)
        if transform is not None:
            try:
                geom.transform(transform)
            except QgsCsException:
                transform_failures += 1
                continue
        geoms_b[feature.id()] = geom
        index.addFeature(feature.id(), geom.boundingBox())

    # 2. Pour chaque polygone A : candidats via l'index, test préparé, puis intersection
    if internal:
        source = list(geoms_b.items())
    else:
        source = ((f.id(), f.geometry()) for f in
                  layer_a.getFeatures(feature_request(layer_a, filter_expression, [], True)))
    pairs: list[tuple[float, int, int]] = []
    checked = failures = 0
    for fid_a, geom_a in source:
        if geom_a.isNull() or geom_a.isEmpty():
            continue
        checked += 1
        candidates = index.intersects(geom_a.boundingBox())
        if internal:
            candidates = [c for c in candidates if c > fid_a]  # chaque paire une seule fois
        if not candidates:
            continue
        engine = QgsGeometry.createGeometryEngine(geom_a.constGet())
        engine.prepareGeometry()
        for fid_b in candidates:
            geom_b = geoms_b[fid_b]
            if not engine.intersects(geom_b.constGet()):
                continue
            intersection = geom_a.intersection(geom_b)
            if intersection.isNull():  # échec GEOS : géométrie invalide probable
                failures += 1
                continue
            area = area_m2(da, intersection)
            if area > 0 and area >= min_area_m2:
                pairs.append((area, fid_a, fid_b))

    pairs.sort(reverse=True)
    total = sum(p[0] for p in pairs)
    data = {
        "mode": "internal" if internal else "between_layers",
        "features_checked": checked,
        "overlap_pairs": len(pairs),
        "area_unit": area_unit,
        "total_overlap_area": round(convert_area(total, area_unit), 4),
        "pairs": [{"fid_a": a, "fid_b": b, "overlap_area": round(convert_area(s, area_unit), 4)}
                  for s, a, b in pairs[:limit]],
        "truncated": len(pairs) > limit,
    }
    warnings = []
    if failures:
        warnings.append(f"{failures} intersection(s) en échec (géométries invalides probables) : "
                        "lance check_geometries.")
    if transform_failures:
        warnings.append(f"{transform_failures} entité(s) de la seconde couche non reprojetables.")
    if internal and pairs:
        warnings.append("Une zone couverte par 3 entités ou plus est comptée plusieurs fois dans "
                        "total_overlap_area.")
    return ToolResult(data, warnings)


def _priority_order(features: list[QgsFeature], field: str | None,
                    descending: bool) -> list[QgsFeature]:
    """Tri par priorité (valeurs nulles en dernier) ; sans champ, ordre des fid."""
    if field is None:
        return features
    keyed = [(group_key(f[field]), f) for f in features]
    filled = sorted((kf for kf in keyed if kf[0] is not None), key=lambda kf: kf[0],
                    reverse=descending)
    return [f for _, f in filled] + [f for k, f in keyed if k is None]


def _as_multipolygon(geom: QgsGeometry) -> QgsGeometry | None:
    """Ne garde que les parties surfaciques (une différence peut produire lignes ou points)."""
    poly = geom.convertToType(Qgis.GeometryType.Polygon, True)
    return None if poly is None or poly.isNull() or poly.isEmpty() else poly


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche de polygones (layer_id)."),
    "priority_field": Param("string", "Champ de priorité : l'entité la plus prioritaire garde la "
                            "zone commune. Défaut : ordre des fid (la première l'emporte).",
                            required=False),
    "descending": Param("boolean", "Priorité aux valeurs les plus grandes de priority_field.",
                        required=False, default=True),
    "output_name": OUTPUT_NAME,
})
def resolve_overlaps(layer_id: str, priority_field: str | None, descending: bool,
                     output_name: str | None) -> ToolResult:
    """Produit une copie de la couche SANS chevauchements : chaque zone couverte par plusieurs
    polygones est attribuée à un seul, le plus prioritaire ; les autres sont découpés. Attributs
    conservés, couche d'origine intacte. Les entités entièrement recouvertes disparaissent
    (fid listés dans removed_fids). Utilise detect_overlaps avant pour mesurer l'enjeu."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    field = require_field(layer, priority_field) if priority_field else None
    da = distance_area(layer.crs(), "ellipsoidal")
    result = QgsMemoryProviderUtils.createMemoryLayer(
        "resolve_overlaps", layer.fields(), QgsWkbTypes.multiType(layer.wkbType()), layer.crs())

    index = QgsSpatialIndex()
    placed: dict[int, QgsGeometry] = {}
    out: list[QgsFeature] = []
    removed: list[int] = []
    failed: list[int] = []
    trimmed = repaired = 0
    removed_area = 0.0
    for feature in _priority_order(list(layer.getFeatures()), field, descending):
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            continue
        if not geom.isGeosValid():
            geom = geom.makeValid()
            repaired += 1
        candidates = [placed[i] for i in index.intersects(geom.boundingBox())]
        blockers = [g for g in candidates if g.intersects(geom)]
        if blockers:
            cut = geom.difference(QgsGeometry.unaryUnion(blockers))
            if cut.isNull():  # échec GEOS
                failed.append(feature.id())
                continue
            removed_area += area_m2(da, geom) - (area_m2(da, cut) if not cut.isEmpty() else 0)
            geom = cut
        poly = _as_multipolygon(geom)
        if poly is None:
            removed.append(feature.id())
            continue
        trimmed += bool(blockers)
        placed[feature.id()] = poly
        index.addFeature(feature.id(), poly.boundingBox())
        new = QgsFeature(feature)
        new.setGeometry(poly)
        out.append(new)
    if not result.dataProvider().addFeatures(out):
        raise ToolError(ErrorCode.INTERNAL_ERROR, "Copie des entités impossible.",
                        {"error": result.dataProvider().lastError()})

    tool_result = run_to_project("native:savefeatures", {"INPUT": result},
                                 output_name or f"sans_chevauchement_{layer.name()}")
    stats: dict[str, Any] = {
        "features_out": len(out), "trimmed": trimmed, "removed_fids": removed[:200],
        "removed_count": len(removed), "repaired_inputs": repaired,
        "overlap_area_removed_m2": round(removed_area, 2),
        "priority": f"{field} {'desc' if descending else 'asc'}" if field else "fid",
    }
    tool_result.data.update(stats)
    if failed:
        tool_result.warnings.append(f"{len(failed)} entité(s) non traitées (échec GEOS), "
                                    f"absentes de la sortie : fid {failed[:50]}.")
    if repaired:
        tool_result.warnings.append(f"{repaired} géométrie(s) invalide(s) réparée(s) à la volée.")
    return tool_result
