from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from qgis.core import QgsExpression, QgsFeature, QgsFeatureRequest, QgsGeometry

from ..core import landscape as nomenclature
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.metrics import elongation, shape_index
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
    iter_geometries,
    length_m,
    perimeter_m,
    prepare_expression,
    require_field,
    territory_info,
    to_json_value,
)
from .export import SEPARATORS, TABLE_FORMATS, write_table
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


def _r4(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche de polygones (layer_id)."),
    "indices": Param("array", "Indices : gravelius (compacité, 1 = disque, augmente avec le "
                     "découpage), elongation (0 à 1, 1 = trapu, proche de 0 = bande étroite), "
                     "coverage_rate (% de la référence couvert), density (entités par ha de la "
                     "référence), cv (variabilité des surfaces).",
                     items="string",
                     items_enum=("gravelius", "elongation", "coverage_rate", "density", "cv")),
    "reference_layer_id": Param("string", "Couche de référence (layer_id), ex. aire d'étude ou "
                                "parcelle : requise pour coverage_rate et density.",
                                required=False),
    "id_field": Param("string", "Champ identifiant renvoyé avec chaque entité.", required=False),
    "filter_expression": Param("string", FILTER_HELP, required=False),
    "limit": Param("integer", "Nombre d'entités renvoyées.", required=False, default=50,
                   minimum=0, maximum=500),
    "offset": Param("integer", "Décalage de pagination.", required=False, default=0, minimum=0),
})
def shape_indices(layer_id: str, indices: list[str], reference_layer_id: str | None,
                  id_field: str | None, filter_expression: str | None, limit: int,
                  offset: int) -> ToolResult:
    """Indices de forme de polygones : compacité de Gravelius et allongement par entité (avec
    surface et périmètre ellipsoïdaux), statistiques globales de chaque indice, CV des surfaces,
    taux de couverture et densité par rapport à une couche de référence. Ex. : repérer les
    parcelles en lanière, comparer la compacité des bosquets. Paginé : has_more, offset."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"{layer.name()} n'est pas une couche de polygones.")
    indices = list(dict.fromkeys(indices))
    if not indices:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique au moins un indice.")
    needs_ref = sorted({"coverage_rate", "density"} & set(indices))
    if needs_ref and not reference_layer_id:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"{', '.join(needs_ref)} demandent reference_layer_id.")
    id_name = require_field(layer, id_field) if id_field else None
    da = distance_area(layer.crs())

    rows: list[dict[str, Any]] = []
    geoms: list[QgsGeometry] = []
    request = feature_request(layer, filter_expression, [id_name] if id_name else [])
    for feature, geom in iter_geometries(layer, request):
        area, perimeter = area_m2(da, geom), perimeter_m(da, geom)
        row: dict[str, Any] = {"fid": feature.id()}
        if id_name:
            row[id_name] = to_json_value(feature[id_name])
        row.update(area_m2=round(area, 2), perimeter_m=round(perimeter, 2))
        if "gravelius" in indices:
            row["gravelius"] = _r4(shape_index(area, perimeter))
        if "elongation" in indices:
            _, _, _, width, height = geom.orientedMinimumBoundingBox()
            row["elongation"] = _r4(elongation(width, height))
        rows.append(row)
        if needs_ref:
            geoms.append(geom)

    summary: dict[str, Any] = {}
    for key in ("gravelius", "elongation"):
        if key in indices:
            summary[key] = describe([r[key] for r in rows if r[key] is not None])
    if "cv" in indices:
        summary["cv_area"] = describe([r["area_m2"] for r in rows])["cv"]
    warnings: list[str] = []
    if needs_ref:
        ref = get_vector_layer(reference_layer_id)
        ref_geoms = [g for _, g in iter_geometries(ref, feature_request(ref, attributes=[]),
                                                   layer.crs())]
        if not ref_geoms:
            raise ToolError(ErrorCode.INVALID_PARAMS,
                            f"{ref.name()} : aucune géométrie de référence.")
        # ponytail: union en mémoire de toute la couche, découper par tuiles si très grosse couche
        ref_union = QgsGeometry.unaryUnion(ref_geoms)
        ref_area = area_m2(da, ref_union)
        summary["reference_area_ha"] = round(ref_area / 10_000, 4)
        if "coverage_rate" in indices:
            covered = QgsGeometry.unaryUnion(geoms).intersection(ref_union) if geoms else None
            if geoms and (covered is None or covered.isNull()):
                warnings.append("Union des géométries impossible : lance check_geometries.")
            covered_m2 = area_m2(da, covered) if covered and not covered.isNull() else 0.0
            summary["coverage_rate_pct"] = (round(100 * covered_m2 / ref_area, 2)
                                            if ref_area else None)
        if "density" in indices:
            inside = sum(1 for g in geoms if g.intersects(ref_union))
            summary["density_per_ha"] = _r4(inside * 10_000 / ref_area) if ref_area else None
            summary["features_in_reference"] = inside
    if "elongation" in indices and layer.crs().isGeographic():
        warnings.append("Allongement calculé en SCR géographique (degrés) : valeurs déformées, "
                        "reprojette la couche (EPSG:2975 / EPSG:4471).")
    return ToolResult({
        "feature_count": len(rows), "summary": summary,
        "features": rows[offset:offset + limit], "has_more": offset + limit < len(rows),
    }, warnings)


HABITAT_HEADERS = ["Habitat", "Libellé", "Nb de polygones", "Surface (ha)",
                   "Part de l'aire d'étude (%)", "Part de la surface cartographiée (%)",
                   "Surface moyenne (ha)", "Périmètre cumulé (m)"]


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche des habitats (layer_id), polygones."),
    "class_field": Param("string", "Champ du type d'habitat (code ou libellé)."),
    "study_area_layer_id": Param("string", "Aire d'étude (layer_id) : habitats découpés par "
                                 "elle, parts rapportées à sa surface, ligne « Non "
                                 "cartographié ». Défaut : toute la couche.", required=False),
    "export_format": Param("string", "Fichier du tableau dans mcp_outputs/, ou none.",
                           required=False, default="xlsx",
                           enum=(*TABLE_FORMATS, "none")),
    "separator": Param("string", "Séparateur CSV.", required=False, default=";",
                       enum=tuple(SEPARATORS)),
    "output_name": Param("string", "Nom du fichier (nettoyé, jamais écrasé).", required=False),
})
def habitat_area_stats(layer_id: str, class_field: str, study_area_layer_id: str | None,
                       export_format: str, separator: str,
                       output_name: str | None) -> ToolResult:
    """Tableau des habitats de l'aire d'étude : nombre de polygones, surface (ha), part de
    l'aire d'étude et de la surface cartographiée (%), surface moyenne, périmètre cumulé
    (limites de l'aire d'étude comprises). Surfaces ellipsoïdales. Libellé ajouté si les
    codes sont ceux de la nomenclature des paysages. Exporté en tableur (xlsx par défaut)."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    class_field = require_field(layer, class_field)
    da = distance_area(layer.crs())
    aoi = None
    if study_area_layer_id:
        zone = get_vector_layer(study_area_layer_id)
        parts = [g for _, g in iter_geometries(zone, feature_request(zone, None, []),
                                               layer.crs())]
        if geometry_kind(zone) != "polygon" or not parts:
            raise ToolError(ErrorCode.INVALID_PARAMS, f"{zone.name()} doit contenir le "
                            "polygone de l'aire d'étude.")
        aoi = QgsGeometry.unaryUnion(parts).makeValid()
        engine = QgsGeometry.createGeometryEngine(aoi.constGet())
        engine.prepareGeometry()

    groups: dict[Any, list[float]] = defaultdict(lambda: [0, 0.0, 0.0])
    pieces = []
    for feature, geometry in iter_geometries(layer, feature_request(layer, None, [class_field])):
        if aoi is not None:
            if not engine.intersects(geometry.constGet()):
                continue
            geometry = geometry.intersection(aoi)
        area = area_m2(da, geometry)
        if area <= 0:
            continue
        group = groups[group_key(feature[class_field])]
        group[0] += 1
        group[1] += area
        group[2] += perimeter_m(da, geometry)
        pieces.append(geometry)
    if not groups:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucun habitat dans l'aire d'étude.")

    mapped = sum(g[1] for g in groups.values())
    covered = area_m2(da, QgsGeometry.unaryUnion(pieces))
    study = area_m2(da, aoi) if aoi is not None else covered
    rows = []
    for key, (count, area, perimeter) in sorted(groups.items(), key=lambda kv: -kv[1][1]):
        item = nomenclature.get_class(str(key)) if key is not None else None
        rows.append([key, item.label if item else None, count, round(area / 10_000, 4),
                     round(area / study * 100, 2), round(area / mapped * 100, 2),
                     round(area / count / 10_000, 4), round(perimeter, 1)])
    if aoi is not None and study - covered > study * 0.0001:
        rows.append(["Non cartographié", None, None, round((study - covered) / 10_000, 4),
                     round((study - covered) / study * 100, 2), None, None, None])
    rows.append(["Total", None, sum(g[0] for g in groups.values()), round(study / 10_000, 4),
                 100.0, 100.0 if covered else None, None, None])

    warnings: list[str] = []
    if mapped - covered > mapped * 0.001:
        warnings.append(f"Polygones d'habitat qui se chevauchent : "
                        f"{(mapped - covered) / 10_000:.2f} ha comptés plusieurs fois (parts "
                        "faussées) ; check_geometries ou resolve_overlaps.")
    data: dict[str, Any] = {"layer": layer.name(), "class_field": class_field,
                            "study_area_ha": round(study / 10_000, 4),
                            "mapped_ha": round(covered / 10_000, 4),
                            "headers": HABITAT_HEADERS, "rows": rows}
    outputs = []
    if export_format != "none":
        path, more = write_table(output_name or f"habitats_{layer.name()}", HABITAT_HEADERS,
                                 [[None if v is None else v for v in r] for r in rows],
                                 export_format, separator)
        warnings.extend(more)
        data["path"] = str(path)
        outputs.append(str(path))
    return ToolResult(data, warnings, outputs)
