"""Coefficients d'occupation du sol et indices paysagers mesurés sur des couches QGIS."""
from __future__ import annotations

from typing import Any

from qgis.core import QgsGeometry, QgsVectorLayer

from ..core import coefficients as formulas
from ..core import metrics as indices
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    area_m2,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    iter_geometries,
    perimeter_m,
    require_field,
    to_json_value,
)

GLOBAL = "__global__"
OUTSIDE = "__hors_zone__"
MAX_RESULTS = 500


def _polygon_layer(layer_id: str) -> QgsVectorLayer:
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    return layer


def _geometries(layer: QgsVectorLayer, attributes: list[str], target: QgsVectorLayer):
    """(entité, géométrie dans le SCR de target) pour chaque entité non vide."""
    return iter_geometries(layer, feature_request(layer, None, attributes), target.crs())


@tool(level=Level.READ, params={})
def list_coefficients() -> dict:
    """Coefficients calculables (CES, COS, CBS, imperméabilisation, espaces verts,
    ruissellement) et catégories de surface reconnues avec leurs pondérations. À consulter
    avant compute_coefficients pour connaître les codes de catégorie (bati, voirie,
    pleine_terre…)."""
    return {
        "coefficients": [spec.to_dict() for spec in formulas.COEFFICIENTS],
        "categories": formulas.list_categories(),
        "note": "Pondérations de référence courantes, pas un texte réglementaire : le PLU "
                "applicable prime.",
    }


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche de polygones des surfaces (layer_id)."),
    "category_field": Param("string", "Champ de nature de surface (bâti, voirie…)."),
    "group_field": Param("string", "Champ de regroupement, ex. n° de parcelle. Absent : un "
                         "résultat global.", required=False),
    "reference_layer_id": Param("string", "Couche des terrains de référence (layer_id). "
                                "Absent : somme des surfaces de layer_id.", required=False),
    "floor_area_field": Param("string", "Champ de surface de plancher (m²), nécessaire au COS.",
                              required=False),
    "aliases": Param("object", 'Libellé terrain → catégorie, ex. {"enrobé": "voirie"}.',
                     required=False),
    "cbs_weights": Param("object", "Pondérations CBS remplaçant celles par défaut, ex. "
                         '{"gravier": 0.3}.', required=False),
})
def compute_coefficients(layer_id: str, category_field: str, group_field: str | None,
                         reference_layer_id: str | None, floor_area_field: str | None,
                         aliases: dict | None, cbs_weights: dict | None) -> ToolResult:
    """Coefficients d'occupation du sol d'une couche de surfaces, globalement ou par groupe
    (parcelle…) : emprise au sol, biotope, imperméabilisation, espaces verts, ruissellement,
    COS si floor_area_field. Surfaces ellipsoïdales en m²."""
    layer = _polygon_layer(layer_id)
    category_field = require_field(layer, category_field)
    group_field = require_field(layer, group_field) if group_field else None
    floor_area_field = require_field(layer, floor_area_field) if floor_area_field else None
    weights = None
    if cbs_weights:
        try:
            weights = {**formulas.CBS_WEIGHTS, **{k: float(v) for k, v in cbs_weights.items()}}
        except (TypeError, ValueError) as exc:
            raise ToolError(ErrorCode.INVALID_PARAMS, "cbs_weights : valeurs numériques "
                            "attendues.") from exc
    da = distance_area(layer.crs())

    groups: dict[Any, dict[str, Any]] = {}
    unknown: dict[str, float] = {}
    attributes = [f for f in (category_field, group_field, floor_area_field) if f]
    for feature, geometry in _geometries(layer, attributes, layer):
        surface = area_m2(da, geometry)
        raw = to_json_value(feature[category_field])
        category = formulas.resolve_category(raw, aliases)
        if category is None:
            label = "(non renseigné)" if raw is None else str(raw)
            unknown[label] = unknown.get(label, 0.0) + surface
        key = group_key(feature[group_field]) if group_field else GLOBAL
        bucket = groups.setdefault(key, {"parts": [], "floor_area": 0.0})
        bucket["parts"].append({"category": category, "area": surface})
        if floor_area_field:
            value = to_json_value(feature[floor_area_field])
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                bucket["floor_area"] += float(value)
    if not groups:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucune "
                        "géométrie exploitable.")

    warnings: list[str] = []
    references = (_reference_areas(reference_layer_id, group_field, warnings)
                  if reference_layer_id else {})
    results = []
    for key, bucket in groups.items():
        total = references.get(key) or sum(p["area"] for p in bucket["parts"])
        computed = formulas.compute_all(
            bucket["parts"], total_area=total,
            floor_area=bucket["floor_area"] if floor_area_field else None, cbs_weights=weights)
        results.append({
            "group": None if key == GLOBAL else key,
            "total_area_m2": round(total, 2),
            "total_area_ha": round(total / formulas.M2_PER_HA, 4),
            "part_count": len(bucket["parts"]),
            "coefficients": {
                code: {**payload, "label": formulas.BY_CODE[code].label,
                       "interpretation": formulas.interpret(code, payload.get("value"))}
                for code, payload in computed.items()},
        })
    if unknown:
        top = sorted(unknown.items(), key=lambda item: -item[1])[:5]
        warnings.append(f"{len(unknown)} valeur(s) de « {category_field} » non reconnue(s) : "
                        + ", ".join(f"{name} ({surface:.0f} m²)" for name, surface in top)
                        + ". Rattache-les avec aliases (voir list_coefficients).")
    if references and group_field:
        missing = [str(k) for k in groups if k not in references][:10]
        if missing:
            warnings.append(f"Groupes sans terrain de référence (surface des parts utilisée) : "
                            f"{', '.join(missing)}.")
    results.sort(key=lambda item: str(item["group"]))
    return ToolResult({"layer": layer.name(), "group_field": group_field,
                       "group_count": len(results), "results": results[:MAX_RESULTS],
                       "truncated": len(results) > MAX_RESULTS}, warnings)


def _reference_areas(reference_layer_id: str, group_field: str | None,
                     warnings: list[str]) -> dict[Any, float]:
    """Surface des terrains de référence : par groupe (même champ des deux côtés) ou globale."""
    reference = _polygon_layer(reference_layer_id)
    ref_field = None
    if group_field:
        index = reference.fields().lookupField(group_field)
        if index < 0:
            warnings.append(f"Champ « {group_field} » absent de « {reference.name()} » : "
                            "couche de référence ignorée, surface des parts utilisée.")
            return {}
        ref_field = reference.fields().at(index).name()
    da = distance_area(reference.crs())
    areas: dict[Any, float] = {}
    for feature, geometry in _geometries(reference, [ref_field] if ref_field else [], reference):
        key = group_key(feature[ref_field]) if ref_field else GLOBAL
        areas[key] = areas.get(key, 0.0) + area_m2(da, geometry)
    return areas


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche de polygones des taches de paysage (layer_id)."),
    "class_field": Param("string", "Champ du type de paysage. Absent : une seule classe.",
                         required=False),
    "zone_layer_id": Param("string", "Couche de zones d'étude (layer_id) pour un calcul par "
                           "secteur ; une tache appartient à la zone qui contient son point "
                           "intérieur.", required=False),
    "zone_field": Param("string", "Champ identifiant les zones.", required=False),
    "max_features": Param("integer", "Nombre maximal de taches analysées.", required=False,
                          default=20000, minimum=1, maximum=200000),
})
def landscape_metrics(layer_id: str, class_field: str | None, zone_layer_id: str | None,
                      zone_field: str | None, max_features: int) -> ToolResult:
    """Indices de structure paysagère (FRAGSTATS, version vecteur) : Shannon, équitabilité,
    Simpson, dominance, densité de taches et de lisière, taille moyenne, plus grande tache,
    maille effective, indice de forme moyen, avec interprétation. Surfaces ellipsoïdales."""
    layer = _polygon_layer(layer_id)
    class_field = require_field(layer, class_field) if class_field else None
    da = distance_area(layer.crs())
    zones = _load_zones(zone_layer_id, zone_field, layer) if zone_layer_id else None

    buckets: dict[Any, dict[str, list]] = {}
    warnings: list[str] = []
    for count, (feature, geometry) in enumerate(
            _geometries(layer, [class_field] if class_field else [], layer)):
        if count >= max_features:
            warnings.append(f"Analyse limitée à {max_features} taches : résultat partiel.")
            break
        patch = {"class": to_json_value(feature[class_field]) if class_field else "toutes",
                 "area": area_m2(da, geometry), "perimeter": perimeter_m(da, geometry)}
        for key in _zones_of(geometry, zones):
            bucket = buckets.setdefault(key, {"patches": [], "geometries": []})
            bucket["patches"].append(patch)
            bucket["geometries"].append(geometry)
    if not buckets:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucune tache.")

    results = []
    for key, bucket in buckets.items():
        outline = perimeter_m(da, QgsGeometry.unaryUnion(bucket["geometries"]))
        summary = indices.summarize_patches(bucket["patches"], landscape_perimeter=outline)
        summary["zone"] = None if key == GLOBAL else key
        summary["interpretation"] = indices.interpret_metrics(summary)
        results.append(summary)
    if OUTSIDE in buckets:
        warnings.append(f"{len(buckets[OUTSIDE]['patches'])} tache(s) hors des zones d'étude "
                        f"(zone « {OUTSIDE} »).")
    results.sort(key=lambda item: -(item.get("total_area_m2") or 0.0))
    return ToolResult({"layer": layer.name(), "class_field": class_field,
                       "zone_count": len(results), "results": results[:200]}, warnings)


def _load_zones(zone_layer_id: str, zone_field: str | None,
                layer: QgsVectorLayer) -> list[tuple[Any, QgsGeometry]]:
    """(clé, géométrie dans le SCR de layer) de chaque zone d'étude."""
    zones_layer = _polygon_layer(zone_layer_id)
    zone_field = require_field(zones_layer, zone_field) if zone_field else None
    return [(group_key(feature[zone_field]) if zone_field else f"zone_{feature.id()}", geometry)
            for feature, geometry in _geometries(zones_layer,
                                                 [zone_field] if zone_field else [], layer)]


def _zones_of(geometry: QgsGeometry, zones: list | None) -> list:
    if zones is None:
        return [GLOBAL]
    point = geometry.pointOnSurface()
    return [key for key, zone in zones if zone.contains(point)] or [OUTSIDE]
