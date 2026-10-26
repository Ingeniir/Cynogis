"""Hiérarchisation des enjeux écologiques : règles pondérées → carte d'enjeux."""
from __future__ import annotations

from collections import Counter

from qgis.core import QgsFeature, QgsFields, QgsMemoryProviderUtils

from ..core import stakes
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.fields import unique_field_name
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    add_to_memory,
    area_m2,
    area_method,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    make_field,
    prepare_expression,
)
from .geoprocessing import OUTPUT_NAME
from .outputs import save_to_project
from .styling import apply_categorized_style

ADDED_FIELDS = (("enj_score", "real"), ("enj_niv", "integer"), ("enj_lib", "string"),
                ("enj_surcl", "string"), ("enj_detail", "string"))


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Polygones à évaluer (layer_id), portant les champs des "
                      "critères, ex. sortie de count_observations, invasive_species_map ou "
                      "habitat_typology_join."),
    "criteria": Param("array", 'Critères pondérés : [{"name": "protection", "expression": '
                      '"\\"nb_prot\\" > 0", "weight": 3}, {"name": "rarete", "expression": '
                      '"\\"rarete\\"", "weight": 2, "max": 4}, {"name": "naturalite", '
                      '"expression": "CASE WHEN \\"eee_rec\\" > 50 THEN 0 ELSE 1 END"}]. '
                      "expression : expression QGIS donnant une note de 0 à max (défaut 1 ; "
                      "vrai = 1) ; weight : poids (défaut 1).", items="object"),
    "overrides": Param("array", 'Surclassements : [{"expression": "\\"nb_prot\\" > 0", '
                       '"level": "fort", "label": "Espèce protégée"}] : niveau minimal imposé '
                       "quand l'expression est vraie.", required=False, items="object"),
    "thresholds": Param("array", "Seuils du score (0-100) des niveaux modéré, fort, très "
                        "fort, majeur. Défaut : [20, 40, 60, 80].", required=False,
                        items="number"),
    "output_name": OUTPUT_NAME,
})
def stake_scoring(layer_id: str, criteria: list, overrides: list | None,
                  thresholds: list | None, output_name: str | None) -> ToolResult:
    """Carte d'enjeux : chaque polygone reçoit un score (0-100, moyenne pondérée des critères
    ramenés entre 0 et 1), un niveau 1 Faible, 2 Modéré, 3 Fort, 4 Très fort, 5 Majeur
    (enj_score, enj_niv, enj_lib), le surclassement appliqué (enj_surcl) et le détail des
    notes (enj_detail). Couche stylée par niveau. Critères, poids, seuils et surclassements
    relèvent de la méthode du bureau d'études : les faire valider par l'utilisateur."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    try:
        parsed = stakes.parse_criteria(criteria)
        rules = stakes.parse_overrides(overrides)
        limits = stakes.parse_thresholds(thresholds)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    compiled = {c.name: prepare_expression(c.expression, layer, f"critère {c.name}")
                for c in parsed}
    compiled_rules = [(rule, *prepare_expression(rule.expression, layer, "surclassement"))
                      for rule in rules]

    fields = QgsFields(layer.fields())
    added = {}
    for name, type_name in ADDED_FIELDS:
        added[name] = unique_field_name(name, fields.names())
        fields.append(make_field(added[name], type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("enjeux", fields, layer.wkbType(),
                                                      layer.crs())
    da = distance_area(layer.crs())
    missing: Counter = Counter()
    raised: Counter = Counter()
    by_level: dict[int, list[float]] = {n: [0, 0.0] for n in stakes.LEVELS}
    out = []
    for feature in layer.getFeatures(feature_request(layer)):
        values = {}
        for criterion in parsed:
            expression, context = compiled[criterion.name]
            context.setFeature(feature)
            values[criterion.name] = stakes.to_score(expression.evaluate(context))
            if values[criterion.name] is None:
                missing[criterion.name] += 1
        total = stakes.score(values, parsed)
        level = stakes.level_for(total, limits)
        forced = None
        for rule, expression, context in compiled_rules:
            context.setFeature(feature)
            if rule.level > level and expression.evaluate(context):
                level, forced = rule.level, rule.label
        if forced:
            raised[forced] += 1
        copy = QgsFeature(fields)
        copy.setGeometry(feature.geometry())
        detail = " ; ".join(
            f"{c.name} {'?' if values[c.name] is None else f'{values[c.name]:g}'}/{c.max:g} "
            f"(poids {c.weight:g})" for c in parsed)
        copy.setAttributes([*feature.attributes(), total, level, stakes.LEVELS[level][0],
                            forced, detail])
        out.append(copy)
        by_level[level][0] += 1
        by_level[level][1] += area_m2(da, feature.geometry()) / 10_000.0
    if not out:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucun polygone.")
    notes = add_to_memory(memory, out)

    result = save_to_project(memory, output_name or f"enjeux_{layer.name()}")
    result.warnings.extend(notes)
    apply_categorized_style(
        result.data["outputs"][0]["layer_id"], added["enj_niv"],
        [{"value": str(n), "color": color, "label": f"{n} - {label}"}
         for n, (label, color) in stakes.LEVELS.items()],
        None, None, False, None, None, 1, True)
    surface = sum(area for _, area in by_level.values())
    result.data.update({
        "fields": added, "thresholds": list(limits),
        "levels": [{"level": n, "label": stakes.LEVELS[n][0], "count": count,
                    "area_ha": round(area, 4),
                    "percent": round(area / surface * 100, 2) if surface else None}
                   for n, (count, area) in by_level.items()],
        "overrides_applied": dict(raised), "area_method": area_method(da),
    })
    for name, count in missing.items():
        result.warnings.append(f"Critère {name} : {count} polygone(s) sans valeur (note 0).")
    return result
