"""Délimitation et classification des unités de paysage."""
from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsExpression,
    QgsFeature,
    QgsFields,
    QgsMemoryProviderUtils,
    QgsProperty,
    QgsVectorLayer,
)

from ..core import landscape as nomenclature
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.territory import detect_territory
from .common import (
    area_m2,
    distance_area,
    extent_wgs84,
    feature_request,
    geometry_kind,
    get_vector_layer,
    make_field,
    prepare_expression,
    rect_to_list,
    require_field,
    to_json_value,
)
from .geoprocessing import OUTPUT_NAME
from .outputs import run_in_memory, run_to_project, save_to_project

TERRITORY = Param("string", "Territoire, pour restreindre la nomenclature. Défaut : détecté "
                  "depuis l'emprise de la couche.", required=False, enum=("reunion", "mayotte"))
# Champs ajoutés par classify_landscape (10 caractères max : compatibles Shapefile).
CLASS_FIELDS = (("pays_code", "string", 10), ("pays_lib", "string", 80),
                ("pays_grp", "string", 40), ("pays_surf", "real", 0),
                ("pays_resid", "integer", 1))


def _territory(territory: str | None, layer: QgsVectorLayer) -> str | None:
    if territory:
        return territory
    found = detect_territory(rect_to_list(extent_wgs84(layer)))
    return found.code if found else None


@tool(level=Level.READ, params={
    "territory": Param("string", "Restreindre à un territoire (classes communes incluses).",
                       required=False, enum=("reunion", "mayotte")),
    "group": Param("string", "Grand poste : 1 artificialisé, 2 agricole, 3 naturel, 4 zones "
                   "humides, 5 eau.", required=False, enum=tuple(nomenclature.GROUPS)),
})
def list_landscape_classes(territory: str | None, group: str | None) -> dict:
    """Nomenclature fermée des types de paysage (logique Corine Land Cover) : seuls ces codes
    peuvent être affectés. Certains sont propres à un territoire (tamarinaie à La Réunion,
    padza et mangrove à Mayotte)."""
    items = [item for item in nomenclature.classes_for(territory)
             if group is None or item.group == group]
    return {"territory": territory, "groups": nomenclature.GROUPS, "count": len(items),
            "classes": [item.to_dict() for item in items]}


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche à analyser (layer_id)."),
    "field": Param("string", "Champ des libellés d'occupation du sol."),
    "territory": TERRITORY,
    "max_values": Param("integer", "Nombre maximal de valeurs distinctes examinées.",
                        required=False, default=200, minimum=1, maximum=2000),
})
def suggest_landscape_mapping(layer_id: str, field: str, territory: str | None,
                              max_values: int) -> ToolResult:
    """Propose une correspondance valeurs du champ → codes de nomenclature, sans rien
    appliquer. Vérifie les correspondances peu sûres (review_required) et tranche les valeurs
    sans correspondance (unmatched) avec l'utilisateur, puis appelle classify_landscape."""
    layer = get_vector_layer(layer_id)
    field = require_field(layer, field)
    territory = _territory(territory, layer)
    counts: dict[str, int] = {}
    truncated = False
    for feature in layer.getFeatures(feature_request(layer, None, [field], False)):
        raw = to_json_value(feature[field])
        key = "" if raw is None else str(raw)
        if key not in counts and len(counts) >= max_values:
            truncated = True
            continue
        counts[key] = counts.get(key, 0) + 1

    proposal = nomenclature.suggest_mapping(list(counts), territory)
    warnings = []
    if truncated:
        warnings.append(f"Plus de {max_values} valeurs distinctes : seules les {max_values} "
                        "premières sont proposées.")
    if proposal["unmatched"]:
        warnings.append(f"{len(proposal['unmatched'])} valeur(s) sans correspondance : à "
                        "trancher avant de classer.")
    if proposal["review_required"]:
        warnings.append(f"{len(proposal['review_required'])} correspondance(s) peu sûre(s) "
                        "à vérifier.")
    return ToolResult({"layer": layer.name(), "field": field, "territory": territory,
                       "distinct_values": len(counts),
                       "value_counts": dict(sorted(counts.items(), key=lambda kv: -kv[1])[:50]),
                       **proposal}, warnings)


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche de polygones à classer (layer_id)."),
    "source_field": Param("string", "Champ des libellés d'occupation du sol."),
    "mapping": Param("object", 'Libellé → code de nomenclature, ex. {"canne": "2.1.1", '
                     '"ravine": "5.1.1"}. Accents et casse ignorés.'),
    "default_code": Param("string", "Code des valeurs absentes de mapping. Absent : ces "
                          "entités restent sans classe.", required=False),
    "territory": TERRITORY,
    "merge_adjacent": Param("boolean", "Fusionner d'abord les taches voisines de même libellé.",
                            required=False, default=False),
    "min_area_m2": Param("number", "Surface minimale d'une unité ; en deçà, pays_resid = 1.",
                         required=False, default=0, minimum=0),
    "output_name": OUTPUT_NAME,
})
def classify_landscape(layer_id: str, source_field: str, mapping: dict,
                       default_code: str | None, territory: str | None, merge_adjacent: bool,
                       min_area_m2: float, output_name: str | None) -> ToolResult:
    """Crée une couche de paysages classés selon la nomenclature Cynogis, champs ajoutés :
    pays_code, pays_lib, pays_grp, pays_surf (m², ellipsoïdal) et pays_resid. Un code hors
    nomenclature fait échouer l'appel. Prépare mapping avec suggest_landscape_mapping."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    source_field = require_field(layer, source_field)
    territory = _territory(territory, layer)
    mapping = {str(k): str(v) for k, v in (mapping or {}).items()}
    invalid = nomenclature.validate_codes(
        set(mapping.values()) | ({str(default_code)} if default_code else set()), territory)
    if invalid:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"Codes hors nomenclature{f' ({territory})' if territory else ''} : "
                        f"{', '.join(sorted(invalid))}. Voir list_landscape_classes.")

    warnings: list[str] = []
    working = layer
    if merge_adjacent:
        working = run_in_memory("native:dissolve", {"INPUT": layer, "FIELD": [source_field],
                                                    "SEPARATE_DISJOINT": True})
        warnings.append("Taches voisines de même libellé fusionnées avant classement.")

    fields = QgsFields(working.fields())
    for name, type_name, length in CLASS_FIELDS:
        if fields.lookupField(name) < 0:
            fields.append(make_field(name, type_name, length))
    extra = [None] * (fields.count() - working.fields().count())
    memory = QgsMemoryProviderUtils.createMemoryLayer("classify_landscape", fields,
                                                      working.wkbType(), working.crs())
    da = distance_area(working.crs())
    out: list[QgsFeature] = []
    summary: dict[str, dict[str, Any]] = {}
    unmatched: dict[str, int] = {}
    small = 0
    for feature in working.getFeatures():
        geometry = feature.geometry()
        if geometry.isNull() or geometry.isEmpty():
            continue
        raw = to_json_value(feature[source_field])
        code = nomenclature.apply_mapping(raw, mapping, default_code)
        item = nomenclature.get_class(code) if code else None
        surface = area_m2(da, geometry)
        is_small = bool(min_area_m2) and surface < min_area_m2
        small += is_small
        new = QgsFeature(fields)
        new.setAttributes(feature.attributes() + extra)
        new.setGeometry(geometry)
        new["pays_code"] = item.code if item else None
        new["pays_lib"] = item.label if item else None
        new["pays_grp"] = nomenclature.GROUPS[item.group] if item else None
        new["pays_surf"] = round(surface, 2)
        new["pays_resid"] = int(is_small)
        out.append(new)
        if item:
            bucket = summary.setdefault(item.code, {"code": item.code, "label": item.label,
                                                    "count": 0, "area_m2": 0.0})
            bucket["count"] += 1
            bucket["area_m2"] += surface
        else:
            label = "(vide)" if raw is None else str(raw)
            unmatched[label] = unmatched.get(label, 0) + 1
    if not memory.dataProvider().addFeatures(out):
        raise ToolError(ErrorCode.INTERNAL_ERROR, "Copie des entités impossible.",
                        {"error": memory.dataProvider().lastError()})

    result = save_to_project(memory, output_name or f"paysages_{layer.name()}")
    total = sum(bucket["area_m2"] for bucket in summary.values())
    for bucket in summary.values():
        bucket["area_ha"] = round(bucket["area_m2"] / 10_000.0, 4)
        bucket["percent"] = round(bucket["area_m2"] / total * 100.0, 2) if total else None
        bucket["area_m2"] = round(bucket["area_m2"], 2)
    classified = sum(bucket["count"] for bucket in summary.values())
    result.data.update({
        "territory": territory, "classified": classified,
        "unclassified": len(out) - classified,
        "class_summary": sorted(summary.values(), key=lambda b: -b["area_m2"]),
        "next_step": "landscape_metrics sur la couche produite (class_field=pays_code).",
    })
    if unmatched:
        top = sorted(unmatched.items(), key=lambda kv: -kv[1])[:5]
        result.warnings.append(f"{len(unmatched)} valeur(s) sans correspondance, entités sans "
                               "classe : " + ", ".join(f"{k} ({n})" for k, n in top) + ".")
    if small:
        result.warnings.append(f"{small} unité(s) sous {min_area_m2:g} m² (pays_resid = 1) : à "
                               "fusionner ou écarter.")
    result.warnings[:0] = warnings
    return result


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche linéaire du réseau hydrographique (layer_id), en SCR "
                      "projeté."),
    "width_field": Param("string", "Champ de largeur de la ravine (m). Valeur NULL : "
                         "default_width_m.", required=False),
    "default_width_m": Param("number", "Largeur à défaut de champ (m).", required=False,
                             default=10, minimum=0.5, maximum=500),
    "protection_buffer_m": Param("number", "Bande de protection ajoutée de chaque côté (m).",
                                 required=False, default=0, minimum=0, maximum=500),
    "filter_expression": Param("string", "Ne retenir que les tronçons vérifiant cette "
                               "expression.", required=False),
    "dissolve": Param("boolean", "Fusionner les emprises (évite de compter deux fois les "
                      "confluences dans les surfaces).", required=False, default=True),
    "output_name": OUTPUT_NAME,
})
def extract_ravines(layer_id: str, width_field: str | None, default_width_m: float,
                    protection_buffer_m: float, filter_expression: str | None, dissolve: bool,
                    output_name: str | None) -> ToolResult:
    """Emprise surfacique des ravines à partir d'un réseau de lignes : chaque tronçon est
    élargi de sa demi-largeur plus la bande de protection. Résultat à croiser avec les
    parcelles (overlay) pour mesurer les surfaces contraintes."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "line":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche "
                        "linéaire. Pour des polygones, utilise buffer.")
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC,
                        f"{layer.name()} est en degrés ({layer.crs().authid()}) : reprojette-la "
                        "d'abord avec reproject_layer (EPSG:2975 ou EPSG:4471).")
    source: Any = layer
    if filter_expression:
        prepare_expression(filter_expression, layer, "filter_expression")
        source = run_in_memory("native:extractbyexpression",
                               {"INPUT": layer, "EXPRESSION": filter_expression})
    half_default = float(default_width_m) / 2.0 + float(protection_buffer_m)
    if width_field:
        column = QgsExpression.quotedColumnRef(require_field(layer, width_field))
        distance: Any = QgsProperty.fromExpression(
            f"coalesce({column}, {float(default_width_m)}) / 2 + {float(protection_buffer_m)}")
    else:
        distance = half_default
    result = run_to_project("native:buffer", {
        "INPUT": source, "DISTANCE": distance, "SEGMENTS": 8,
        "END_CAP_STYLE": 0, "JOIN_STYLE": 0,  # arrondis : pas d'encoche entre tronçons
        "MITER_LIMIT": 2, "DISSOLVE": bool(dissolve),
    }, output_name or f"ravines_{layer.name()}")
    result.data.update({"default_width_m": float(default_width_m),
                        "protection_buffer_m": float(protection_buffer_m),
                        "width_field": width_field, "dissolved": bool(dissolve)})
    if not width_field:
        result.warnings.append(f"Largeur uniforme de {default_width_m:g} m appliquée.")
    return result
