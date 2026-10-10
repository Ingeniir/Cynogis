from __future__ import annotations

from collections import Counter
from typing import Any

from qgis.core import Qgis, QgsGeometry

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    rect_to_list,
    require_field,
    to_json_value,
)

MAX_WKT_CHARS = 10_000
FILTER_HELP = ("Expression QGIS de filtre, ex. \"commune\" = 'Saint-Paul' ou $area > 10000. "
               "Pour cibler des entités précises : $id IN (12, 45).")


def _geometry_repr(geom: QgsGeometry, fmt: str, precision: int) -> tuple[Any, bool]:
    if geom.isNull() or geom.isEmpty():
        return None, False
    if fmt == "wkt":
        text = geom.asWkt(precision)
        return (text[:MAX_WKT_CHARS] + "…", True) if len(text) > MAX_WKT_CHARS else (text, False)
    if fmt == "bbox":
        return rect_to_list(geom.boundingBox(), precision), False
    point = geom.centroid().asPoint()
    return [round(point.x(), precision), round(point.y(), precision)], False


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "filter_expression": Param("string", FILTER_HELP, required=False),
    "fields": Param("array", "Champs à renvoyer (défaut : tous).", required=False, items="string"),
    "geometry_format": Param("string", "Géométrie renvoyée : none, wkt (complète, volumineuse), "
                             "bbox (emprise) ou centroid.", required=False, default="none",
                             enum=("none", "wkt", "bbox", "centroid")),
    "limit": Param("integer", "Nombre max d'entités.", required=False, default=50,
                   minimum=1, maximum=500),
    "offset": Param("integer", "Entités à sauter (pagination).", required=False, default=0,
                    minimum=0),
})
def get_features(layer_id: str, filter_expression: str | None, fields: list[str] | None,
                 geometry_format: str, limit: int, offset: int) -> ToolResult:
    """Lit les entités d'une couche vecteur : fid, attributs et éventuellement la géométrie
    (dans le SCR de la couche). Paginé : si has_more est vrai, rappelle avec offset + limit.
    Pour des totaux ou des moyennes, préfère measure ou descriptive_stats."""
    layer = get_vector_layer(layer_id)
    names = [require_field(layer, n) for n in fields] if fields else layer.fields().names()
    request = feature_request(layer, filter_expression, names, geometry_format != "none")
    request.setLimit(offset + limit + 1)
    precision = 7 if layer.crs().isGeographic() else 2
    features: list[dict[str, Any]] = []
    has_more = wkt_truncated = False
    for i, feature in enumerate(layer.getFeatures(request)):
        if i < offset:
            continue
        if len(features) == limit:
            has_more = True
            break
        item: dict[str, Any] = {"fid": feature.id(),
                                "attributes": {n: to_json_value(feature[n]) for n in names}}
        if geometry_format != "none":
            item["geometry"], truncated = _geometry_repr(feature.geometry(), geometry_format,
                                                         precision)
            wkt_truncated |= truncated
        features.append(item)
    warnings = ["Certaines géométries WKT ont été tronquées : utilise bbox ou centroid."] \
        if wkt_truncated else []
    return ToolResult({"crs": layer.crs().authid(), "offset": offset, "count": len(features),
                       "has_more": has_more, "features": features}, warnings)


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "field": Param("string", "Nom du champ."),
    "filter_expression": Param("string", FILTER_HELP, required=False),
    "limit": Param("integer", "Nombre max de valeurs distinctes renvoyées.", required=False,
                   default=50, minimum=1, maximum=500),
})
def get_field_values(layer_id: str, field: str, filter_expression: str | None,
                     limit: int) -> dict:
    """Valeurs distinctes d'un champ avec leurs effectifs (les plus fréquentes d'abord) et le
    nombre de valeurs nulles. Utile pour découvrir les catégories (types de paysage, communes…)
    avant de filtrer, de regrouper ou de styliser."""
    layer = get_vector_layer(layer_id)
    name = require_field(layer, field)
    counter: Counter[Any] = Counter()
    for feature in layer.getFeatures(feature_request(layer, filter_expression, [name], False)):
        counter[group_key(feature[name])] += 1
    nulls = counter.pop(None, 0)
    return {
        "field": name, "type": layer.fields().field(name).typeName(),
        "total": sum(counter.values()) + nulls, "null_count": nulls,
        "distinct_count": len(counter),
        "values": [{"value": v, "count": c} for v, c in counter.most_common(limit)],
        "truncated": len(counter) > limit,
    }


def _error_kind(message: str) -> str:
    return message.split("[")[0].strip() or "Géométrie invalide"


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "filter_expression": Param("string", FILTER_HELP, required=False),
    "sample_size": Param("integer", "Nombre max d'entités fautives détaillées.", required=False,
                         default=20, minimum=1, maximum=200),
})
def check_geometries(layer_id: str, filter_expression: str | None,
                     sample_size: int) -> ToolResult:
    """Contrôle qualité des géométries (moteur GEOS) : nulles ou vides, invalides (auto-
    intersection, anneau mal fermé…), multi-parties. Renvoie les types d'erreurs, et le fid et la
    localisation d'un échantillon. À lancer avant toute superposition ou mesure de surface."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) in ("none", "unknown"):
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'a pas de géométrie.")
    checked = empty = invalid = multipart = 0
    error_types: Counter[str] = Counter()
    samples: list[dict[str, Any]] = []
    for feature in layer.getFeatures(feature_request(layer, filter_expression, [], True)):
        checked += 1
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            empty += 1
            if len(samples) < sample_size:
                samples.append({"fid": feature.id(), "error": "Géométrie nulle ou vide"})
            continue
        if geom.isMultipart():
            multipart += 1
        if geom.isGeosValid():
            continue
        invalid += 1
        errors = geom.validateGeometry(Qgis.GeometryValidationEngine.Geos)
        kind = _error_kind(errors[0].what()) if errors else "Géométrie invalide"
        error_types[kind] += 1
        if len(samples) < sample_size:
            sample: dict[str, Any] = {"fid": feature.id(), "error": kind}
            if errors and errors[0].hasWhere():
                where = errors[0].where()
                sample["location"] = [round(where.x(), 2), round(where.y(), 2)]
            samples.append(sample)
    warnings = []
    if invalid or empty:
        warnings.append(f"{invalid} géométrie(s) invalide(s) et {empty} nulle(s) ou vide(s) : "
                        "à corriger avant toute superposition (intersection, union…).")
    return ToolResult({"checked": checked, "valid": checked - invalid - empty,
                       "invalid": invalid, "null_or_empty": empty, "multipart": multipart,
                       "error_types": dict(error_types.most_common()), "samples": samples},
                      warnings)
