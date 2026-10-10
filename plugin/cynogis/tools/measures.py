from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from qgis.core import QgsExpression, QgsFeature, QgsFeatureRequest

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.stats import describe, describe_groups, to_float
from ..core.units import AREA_UNITS, LENGTH_UNITS, convert_area, convert_length
from .common import (
    area_m2,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    length_m,
    perimeter_m,
    prepare_expression,
    require_field,
    territory_info,
    to_json_value,
)
from .features import FILTER_HELP

_ALLOWED = {"polygon": {"area", "perimeter"}, "line": {"length"}}


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "metrics": Param("array", "Mesures : area et perimeter (polygones), length (lignes).",
                     items="string", items_enum=("area", "perimeter", "length")),
    "area_unit": Param("string", "Unité des surfaces.", required=False, default="ha",
                       enum=tuple(AREA_UNITS)),
    "length_unit": Param("string", "Unité des longueurs et périmètres.", required=False,
                         default="m", enum=tuple(LENGTH_UNITS)),
    "method": Param("string", "ellipsoidal (recommandé, fiable quel que soit le SCR) ou planar "
                    "(dans le SCR projeté de la couche).", required=False,
                    default="ellipsoidal", enum=("ellipsoidal", "planar")),
    "group_by": Param("string", "Champ de regroupement (ex. type de paysage, commune).",
                      required=False),
    "filter_expression": Param("string", FILTER_HELP, required=False),
    "max_groups": Param("integer", "Nombre max de groupes renvoyés.", required=False,
                        default=50, minimum=1, maximum=500),
})
def measure(layer_id: str, metrics: list[str], area_unit: str, length_unit: str, method: str,
            group_by: str | None, filter_expression: str | None, max_groups: int) -> ToolResult:
    """Mesure les surfaces, périmètres ou longueurs d'une couche. Renvoie le total et les
    statistiques de chaque mesure (moyenne, médiane, écart-type, quartiles, CV) et, avec
    group_by, le total et la part (%) de chaque groupe. Ex. : surface de chaque type de paysage."""
    layer = get_vector_layer(layer_id)
    metrics = list(dict.fromkeys(metrics))
    kind = geometry_kind(layer)
    allowed = _ALLOWED.get(kind, set())
    bad = [m for m in metrics if m not in allowed]
    if not metrics or bad:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"Mesures {bad or metrics} impossibles sur une couche {kind} "
                        f"(possibles : {', '.join(sorted(allowed)) or 'aucune'}).")
    group_field = require_field(layer, group_by) if group_by else None
    da = distance_area(layer.crs(), method)
    measurers: dict[str, Callable[[Any], float]] = {
        "area": lambda g: convert_area(area_m2(da, g), area_unit),
        "perimeter": lambda g: convert_length(perimeter_m(da, g), length_unit),
        "length": lambda g: convert_length(length_m(da, g), length_unit),
    }
    request = feature_request(layer, filter_expression, [group_field] if group_field else [])
    values: dict[str, dict[Any, list[float]]] = {m: defaultdict(list) for m in metrics}
    skipped = 0
    for feature in layer.getFeatures(request):
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            skipped += 1
            continue
        key = group_key(feature[group_field]) if group_field else None
        for m in metrics:
            values[m][key].append(measurers[m](geom))

    all_values = {m: [v for vs in values[m].values() for v in vs] for m in metrics}
    totals = {m: math.fsum(all_values[m]) for m in metrics}
    data: dict[str, Any] = {
        "method": method,
        "units": {"area": area_unit, "perimeter": length_unit, "length": length_unit},
        "feature_count": len(all_values[metrics[0]]),
        "totals": {m: round(totals[m], 6) for m in metrics},
        "stats": {m: describe(all_values[m]) for m in metrics},
    }
    warnings: list[str] = []
    if group_field:
        rows = []
        for key, first in values[metrics[0]].items():
            row: dict[str, Any] = {"group": key, "count": len(first)}
            for m in metrics:
                subtotal = math.fsum(values[m][key])
                row[m] = round(subtotal, 6)
                row[f"{m}_share_pct"] = round(100 * subtotal / totals[m], 2) if totals[m] else None
            rows.append(row)
        rows.sort(key=lambda r: r[metrics[0]], reverse=True)
        data["group_by"] = group_field
        data["group_count"] = len(rows)
        data["groups"] = rows[:max_groups]
        if len(rows) > max_groups:
            warnings.append(f"{len(rows)} groupes : seuls les {max_groups} plus grands sont "
                            "renvoyés (les totaux portent sur l'ensemble).")
    if skipped:
        warnings.append(f"{skipped} entité(s) sans géométrie ignorée(s).")
    if method == "planar":
        warnings += territory_info(layer)[1]
    return ToolResult(data, warnings)


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "field": Param("string", "Champ numérique à analyser (ou utiliser expression).",
                   required=False),
    "expression": Param("string", "Expression QGIS numérique à la place d'un champ, ex. "
                        "$area / 10000 ou \"pop\" / \"surface\".", required=False),
    "group_by": Param("string", "Champ de regroupement.", required=False),
    "filter_expression": Param("string", FILTER_HELP, required=False),
    "max_groups": Param("integer", "Nombre max de groupes renvoyés.", required=False,
                        default=50, minimum=1, maximum=500),
})
def descriptive_stats(layer_id: str, field: str | None, expression: str | None,
                      group_by: str | None, filter_expression: str | None,
                      max_groups: int) -> ToolResult:
    """Statistiques descriptives d'un champ numérique ou d'une expression : effectif, somme,
    min, max, moyenne, médiane, écart-type, Q1, Q3, IQR et coefficient de variation (CV),
    globalement et par groupe. Les valeurs nulles ou non numériques sont ignorées et comptées."""
    layer = get_vector_layer(layer_id)
    if (field is None) == (expression is None):
        raise ToolError(ErrorCode.INVALID_PARAMS, "Fournis soit field, soit expression (un seul).")
    group_field = require_field(layer, group_by) if group_by else None
    extra = [group_field] if group_field else []

    if field is not None:
        name = require_field(layer, field)
        qfield = layer.fields().field(name)
        if not qfield.isNumeric():
            raise ToolError(ErrorCode.INVALID_PARAMS,
                            f"Le champ {name} n'est pas numérique ({qfield.typeName()}). "
                            f"Utilise get_field_values, ou expression='to_real(\"{name}\")'.")
        attributes: list[str] | None = [name, *extra]
        needs_geometry = False

        def get_value(feature: QgsFeature) -> Any:
            return feature[name]
    else:
        exp, ctx = prepare_expression(expression, layer)
        columns = exp.referencedColumns()
        attributes = None if QgsFeatureRequest.ALL_ATTRIBUTES in columns \
            else [*columns, *extra]
        needs_geometry = exp.needsGeometry()

        def get_value(feature: QgsFeature, _exp: QgsExpression = exp) -> Any:
            ctx.setFeature(feature)
            return _exp.evaluate(ctx)

    request = feature_request(layer, filter_expression, attributes, needs_geometry)
    by_group: dict[Any, list[float]] = defaultdict(list)
    ignored = 0
    for feature in layer.getFeatures(request):
        value = to_float(to_json_value(get_value(feature)))
        if value is None:
            ignored += 1
            continue
        by_group[group_key(feature[group_field]) if group_field else None].append(value)

    data: dict[str, Any] = {
        "source": field or expression,
        "overall": describe([v for vs in by_group.values() for v in vs]),
        "ignored_values": ignored,
    }
    warnings = [f"{ignored} valeur(s) nulle(s) ou non numérique(s) ignorée(s)."] if ignored else []
    if group_field:
        rows = describe_groups(by_group)
        data.update(group_by=group_field, group_count=len(rows), groups=rows[:max_groups])
        if len(rows) > max_groups:
            warnings.append(f"{len(rows)} groupes : seuls les {max_groups} premiers sont renvoyés.")
    return ToolResult(data, warnings)
