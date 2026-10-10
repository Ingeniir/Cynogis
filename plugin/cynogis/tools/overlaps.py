from __future__ import annotations

from qgis.core import (
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProject,
    QgsSpatialIndex,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.units import AREA_UNITS, convert_area
from .common import area_m2, distance_area, feature_request, geometry_kind, get_vector_layer
from .features import FILTER_HELP


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
