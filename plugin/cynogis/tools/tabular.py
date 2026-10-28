"""Profil statistique complet de la table attributaire et corrélations."""
from __future__ import annotations

from typing import Any

from ..core import stats
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.jobs import Pacer, Steps
from ..core.privacy import is_sensitive_field
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    area_m2,
    area_method,
    distance_area,
    feature_request,
    field_type_name,
    geometry_kind,
    get_vector_layer,
    length_m,
    require_field,
    to_json_value,
)
from .features import FILTER_HELP

MAX_PAIRS = 30
_KINDS = {"date": "date", "datetime": "date", "boolean": "boolean"}

def _field_kind(qfield) -> str:
    return "numeric" if qfield.isNumeric() else _KINDS.get(field_type_name(qfield), "text")


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "fields": Param("array", "Champs à profiler (défaut : tous).", required=False,
                    items="string"),
    "filter_expression": Param("string", FILTER_HELP, required=False),
    "include_geometry": Param("boolean", "Ajoute la surface (ha, polygones) ou la longueur "
                              "(m, lignes) ellipsoïdale comme variable.", required=False,
                              default=True),
    "area_weighted": Param("boolean", "Polygones : moyenne, écart-type et médiane de chaque "
                           "champ numérique pondérés par la surface.", required=False,
                           default=False),
    "correlations": Param("string", "Coefficients de corrélation entre variables numériques "
                          "(pearson : linéaire ; spearman : monotone, robuste).",
                          required=False, default="pearson",
                          enum=("none", "pearson", "spearman")),
    "top_n": Param("integer", "Modalités les plus fréquentes renvoyées par champ texte.",
                   required=False, default=10, minimum=1, maximum=50),
    "max_features": Param("integer", "Nombre max d'entités analysées.", required=False,
                          default=100000, minimum=1, maximum=1000000),
})
def profile_table(layer_id: str, fields: list[str] | None, filter_expression: str | None,
                  include_geometry: bool, area_weighted: bool, correlations: str,
                  top_n: int, max_features: int) -> Steps:
    """Statistique descriptive complète de la table attributaire, tous les champs en un seul
    appel. Champs numériques : effectif, valeurs nulles, somme, min, max, étendue, moyenne,
    IC 95 %, médiane, mode, variance, écart-type, CV, centiles, asymétrie, aplatissement,
    valeurs aberrantes. Champs texte, date ou booléen : mode, effectifs, pourcentages,
    entropie. Corrélations entre variables numériques (paires les plus fortes) et option de
    pondération par la surface. Les champs nominatifs ou sensibles sont masqués."""
    layer = get_vector_layer(layer_id)
    names = [require_field(layer, n) for n in fields] if fields else layer.fields().names()
    if not names:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'a aucun champ.")
    warnings: list[str] = []
    kind = geometry_kind(layer)
    geo_name = {"polygon": "$area_ha", "line": "$length_m"}.get(kind) if include_geometry else None
    if kind == "polygon" and layer.crs().isGeographic():
        if area_weighted:
            raise ToolError(ErrorCode.CRS_GEOGRAPHIC,
                            f"Pondération par la surface impossible en SCR géographique "
                            f"({layer.crs().authid()}) : reprojette en EPSG:2975 ou EPSG:4471.")
        geo_name = None
        warnings.append(f"SRC géographique ({layer.crs().authid()}) : surface non calculée.")
    needs_geometry = bool(geo_name) or area_weighted
    da = distance_area(layer.crs()) if needs_geometry else None

    qfields = layer.fields()
    kinds = {n: _field_kind(qfields.field(n)) for n in names}
    columns: dict[str, list[Any]] = {n: [] for n in names}
    geo_values: list[float | None] = []
    weights: list[float | None] = []
    request = feature_request(layer, filter_expression, names, needs_geometry)
    pace = Pacer("profil de la table", min(layer.featureCount(), max_features))
    truncated = False
    for i, feature in enumerate(layer.getFeatures(request)):
        if i >= max_features:
            truncated = True
            break
        yield from pace(i)
        for n in names:
            columns[n].append(to_json_value(feature[n]))
        if needs_geometry:
            geom = feature.geometry()
            if geom.isNull() or geom.isEmpty():
                geo_values.append(None)
                weights.append(None)
                continue
            if kind == "polygon":
                a = area_m2(da, geom)
                weights.append(a)
                geo_values.append(a / 10_000)
            else:
                weights.append(None)
                geo_values.append(length_m(da, geom))

    total = len(next(iter(columns.values())))
    profiles: list[dict[str, Any]] = []
    numeric: dict[str, list[float | None]] = {}
    masked: list[str] = []
    for n in names:
        raw = columns[n]
        nulls = sum(1 for v in raw if _is_empty(v))
        entry: dict[str, Any] = {
            "field": n, "type": qfields.field(n).typeName(), "kind": kinds[n],
            "null_count": nulls, "null_pct": round(100 * nulls / total, 2) if total else None,
        }
        present = [v for v in raw if not _is_empty(v)]
        if is_sensitive_field(n):
            entry.update(masked=True, distinct_count=len({str(v) for v in present}))
            masked.append(n)
        elif kinds[n] == "numeric":
            nums = [stats.to_float(v) for v in raw]
            valid = [v for v in nums if v is not None]
            entry["non_numeric"] = len(present) - len(valid)
            entry["distinct_count"] = len(set(valid))
            entry["stats"] = stats.describe_full(valid)
            if area_weighted:
                entry["area_weighted"] = stats.weighted_stats(nums, weights)
            numeric[n] = nums
        else:
            text = [str(v) for v in present]
            entry["stats"] = stats.describe_categorical(text, top_n)
            if kinds[n] == "date" and text:
                entry["date_range"] = [min(text), max(text)]  # ISO : tri lexical = tri temporel
        profiles.append(entry)

    data: dict[str, Any] = {"layer": layer.name(), "feature_count": total,
                            "field_count": len(names), "fields": profiles}
    if geo_name:
        data["geometry"] = {"variable": geo_name, "area_method": area_method(da),
                            "stats": stats.describe_full(
                                [v for v in geo_values if v is not None])}
        numeric[geo_name] = geo_values
        warnings.append("Statistiques géométriques par entité (sans fusion) : pour des totaux "
                        "sans double compte des chevauchements, utiliser measure.")
    if correlations != "none" and len(numeric) >= 2:
        pairs = stats.correlation_pairs(numeric, correlations)
        data["correlations"] = {"method": correlations, "pair_count": len(pairs),
                                "strongest": pairs[:MAX_PAIRS]}
    if truncated:
        warnings.append(f"Analyse limitée aux {max_features} premières entités.")
    if masked:
        warnings.append(f"Champs sensibles masqués (valeurs non transmises) : "
                        f"{', '.join(masked)}.")
    if correlations != "none":
        warnings.append("Corrélation ≠ causalité ; p-values approchées (Fisher), à prendre "
                        "avec prudence si n < 30 ou en cas d'autocorrélation spatiale.")
    return ToolResult(data, warnings)


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "fields": Param("array", "Champs numériques à croiser (2 à 15).", items="string"),
    "method": Param("string", "pearson (linéaire) ou spearman (rangs, monotone).",
                    required=False, default="pearson", enum=("pearson", "spearman")),
    "filter_expression": Param("string", FILTER_HELP, required=False),
})
def correlation_matrix(layer_id: str, fields: list[str], method: str,
                       filter_expression: str | None) -> Steps:
    """Matrice de corrélation entre champs numériques : r, R², n, p-value approchée et force
    de la liaison, pour chaque paire (valeurs manquantes exclues paire par paire). Avec deux
    champs, ajoute la régression linéaire y = pente · x + ordonnée et son R²."""
    layer = get_vector_layer(layer_id)
    names = list(dict.fromkeys(require_field(layer, f) for f in fields))
    if not 2 <= len(names) <= 15:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique entre 2 et 15 champs.")
    not_numeric = [n for n in names if not layer.fields().field(n).isNumeric()]
    if not_numeric:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"Champs non numériques : {', '.join(not_numeric)}.")
    sensitive = [n for n in names if is_sensitive_field(n)]
    if sensitive:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"Champs sensibles exclus : {', '.join(sensitive)}.")
    columns: dict[str, list[float | None]] = {n: [] for n in names}
    pace = Pacer("corrélations", layer.featureCount())
    request = feature_request(layer, filter_expression, names, False)
    for i, feature in enumerate(layer.getFeatures(request)):
        yield from pace(i)
        for n in names:
            columns[n].append(stats.to_float(to_json_value(feature[n])))

    pairs = stats.correlation_pairs(columns, method)
    matrix = {a: {b: (1.0 if a == b else None) for b in names} for a in names}
    for p in pairs:
        matrix[p["x"]][p["y"]] = matrix[p["y"]][p["x"]] = p["r"]
    data: dict[str, Any] = {"method": method, "fields": names, "matrix": matrix,
                            "pairs": pairs}
    if len(names) == 2:
        both = [(x, y) for x, y in zip(columns[names[0]], columns[names[1]], strict=True)
                if x is not None and y is not None]
        if both:
            xs, ys = zip(*both, strict=True)
            data["regression"] = {"x": names[0], "y": names[1], **(stats.linear_fit(xs, ys)
                                                                   or {})}
    return ToolResult(data, ["Corrélation ≠ causalité ; p-values approchées (Fisher)."])
