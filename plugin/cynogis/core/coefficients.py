"""Coefficients d'occupation du sol et de perméabilité.

Toutes les formules sont rassemblées ici, sans dépendance à QGIS : elles sont
vérifiables par les tests et relisibles par un chargé d'études.

Attention : les pondérations fournies sont des valeurs de référence courantes,
pas un texte réglementaire. Le PLU ou le règlement d'urbanisme applicable
prime toujours ; la table doit être validée avant usage sur un dossier réel.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from .metrics import M2_PER_HA
from .naming import normalize


@dataclass(frozen=True)
class CoefficientSpec:
    """Définition d'un coefficient calculable."""

    code: str
    label: str
    formula: str
    unit: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "label": self.label,
            "formula": self.formula,
            "unit": self.unit,
            "description": self.description,
        }

COEFFICIENTS: tuple[CoefficientSpec, ...] = (
    CoefficientSpec(
        "ces", "Coefficient d'emprise au sol",
        "surface bâtie au sol / surface du terrain", "ratio",
        "Part du terrain occupée par l'emprise des constructions.",
    ),
    CoefficientSpec(
        "cos", "Coefficient d'occupation des sols",
        "surface de plancher / surface du terrain", "ratio",
        "Rapport entre la surface de plancher construite et la surface du terrain.",
    ),
    CoefficientSpec(
        "cbs", "Coefficient de biotope par surface",
        "somme(surface x pondération écologique) / surface du terrain", "ratio",
        "Qualité écologique des surfaces : 0 pour l'imperméable, 1 pour la pleine terre.",
    ),
    CoefficientSpec(
        "imperm", "Taux d'imperméabilisation",
        "surface imperméable / surface totale", "pourcentage",
        "Part des surfaces ne laissant pas s'infiltrer l'eau de pluie.",
    ),
    CoefficientSpec(
        "espace_vert", "Part d'espaces verts",
        "surface végétalisée / surface totale", "pourcentage",
        "Part des surfaces végétalisées, pleine terre et toitures comprises.",
    ),
    CoefficientSpec(
        "densite", "Densité",
        "effectif / surface", "unités par hectare",
        "Nombre d'éléments rapporté à la surface, en unités par hectare.",
    ),
    CoefficientSpec(
        "ruissellement", "Coefficient de ruissellement",
        "somme(surface x coefficient de ruissellement) / surface totale", "ratio",
        "Part de la pluie qui ruisselle au lieu de s'infiltrer, pondérée par "
        "nature de surface. Base des calculs de dimensionnement hydraulique.",
    ),
)

BY_CODE: dict[str, CoefficientSpec] = {spec.code: spec for spec in COEFFICIENTS}

# Pondérations écologiques du coefficient de biotope par surface.
# 0 = surface totalement minérale, 1 = pleine terre en lien avec la nappe.
CBS_WEIGHTS: dict[str, float] = {
    "pleine_terre": 1.0,
    "espace_vert": 1.0,
    "boise": 1.0,
    "eau": 1.0,
    "revetement_permeable": 0.5,
    "revetement_semi_permeable": 0.3,
    "gravier": 0.5,
    "dalle_engazonnee": 0.5,
    "toiture_vegetalisee_epaisse": 0.7,
    "toiture_vegetalisee_fine": 0.5,
    "mur_vegetalise": 0.5,
    "impermeable": 0.0,
    "bati": 0.0,
    "voirie": 0.0,
    "parking_impermeable": 0.0,
}

# Coefficients de ruissellement usuels (méthode rationnelle).
# Valeurs hautes volontairement retenues : en climat tropical les averses sont
# intenses et saturent rapidement les sols.
RUNOFF_WEIGHTS: dict[str, float] = {
    "bati": 0.95,
    "toiture": 0.95,
    "voirie": 0.90,
    "parking_impermeable": 0.90,
    "impermeable": 0.90,
    "revetement_semi_permeable": 0.60,
    "revetement_permeable": 0.40,
    "gravier": 0.40,
    "sol_nu": 0.40,
    "culture": 0.30,
    "prairie": 0.25,
    "espace_vert": 0.20,
    "pleine_terre": 0.20,
    "boise": 0.15,
    "foret": 0.10,
    "eau": 1.00,
}

# Surfaces considérées comme imperméables par défaut.
IMPERVIOUS = frozenset(
    {"bati", "toiture", "voirie", "parking_impermeable", "impermeable"}
)
VEGETATED = frozenset(
    {
        "espace_vert", "pleine_terre", "boise", "foret", "prairie", "culture",
        "toiture_vegetalisee_epaisse", "toiture_vegetalisee_fine", "mur_vegetalise",
    }
)

def list_categories() -> dict:
    """Catégories de surface reconnues et leurs pondérations."""
    codes = sorted(set(CBS_WEIGHTS) | set(RUNOFF_WEIGHTS))
    return {
        code: {
            "cbs": CBS_WEIGHTS.get(code),
            "runoff": RUNOFF_WEIGHTS.get(code),
            "impervious": code in IMPERVIOUS,
            "vegetated": code in VEGETATED,
        } for code in codes
    }

def _key(text: object) -> str:
    return normalize(str(text)).replace(" ", "_").replace("-", "_")


def resolve_category(value: str | None, aliases: Mapping[str, str] | None = None) -> str | None:
    """Rattache une valeur de terrain à une catégorie de surface connue.

    La comparaison ignore la casse et les accents. `aliases` permet au chargé
    d'études de déclarer ses propres libellés ("enrobé" -> "voirie").
    """
    if value is None:
        return None
    key = _key(value)
    if aliases:
        normalized_aliases = {_key(k): v for k, v in aliases.items()}
        if key in normalized_aliases:
            key = _key(normalized_aliases[key])
    if key in CBS_WEIGHTS or key in RUNOFF_WEIGHTS:
        return key
    return None


def _ratio(numerator: float, denominator: float) -> float | None:
    """Division protégée : None plutôt qu'une exception sur surface nulle."""
    if denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def weighted_ratio(
    parts: Sequence[Mapping],
    weights: Mapping[str, float],
    total_area: float,
    default_weight: float = 0.0,
) -> dict:
    """Moyenne des surfaces pondérée par catégorie (base du CBS et du ruissellement).

    Chaque part est un dict ``{"category": str, "area": float}``. Les parts de
    catégorie inconnue reçoivent `default_weight` et sont signalées, jamais
    ignorées en silence : un oubli de correspondance doit se voir.
    """
    weighted = 0.0
    covered = 0.0
    unknown: dict[str, float] = {}
    for part in parts:
        area = float(part.get("area") or 0.0)
        if area <= 0:
            continue
        category = part.get("category")
        covered += area
        if category in weights:
            weighted += area * float(weights[category])
        else:
            weighted += area * float(default_weight)
            label = str(category) if category is not None else "(non renseigné)"
            unknown[label] = unknown.get(label, 0.0) + area
    reference = float(total_area) if total_area and total_area > 0 else covered
    return {
        "value": _ratio(weighted, reference),
        "weighted_area": weighted,
        "covered_area": covered,
        "reference_area": reference,
        "uncovered_area": max(reference - covered, 0.0),
        "unknown_categories": {k: round(v, 2) for k, v in sorted(unknown.items())},
    }


def coverage_ratio(parts: Sequence[Mapping], categories: Iterable[str], total_area: float) -> dict:
    """Part de la surface occupée par un ensemble de catégories."""
    wanted = set(categories)
    selected = sum(
        float(part.get("area") or 0.0)
        for part in parts
        if part.get("category") in wanted
    )
    ratio = _ratio(selected, total_area)
    return {
        "value": ratio,
        "percent": None if ratio is None else ratio * 100.0,
        "area": selected,
        "total_area": float(total_area or 0.0),
    }


def footprint_ratio(built_area: float, plot_area: float) -> dict:
    """Coefficient d'emprise au sol."""
    value = _ratio(float(built_area or 0.0), float(plot_area or 0.0))
    return {
        "value": value,
        "percent": None if value is None else value * 100.0,
        "built_area": float(built_area or 0.0),
        "plot_area": float(plot_area or 0.0),
    }


def floor_area_ratio(floor_area: float, plot_area: float) -> dict:
    """Coefficient d'occupation des sols (surface de plancher / terrain)."""
    value = _ratio(float(floor_area or 0.0), float(plot_area or 0.0))
    return {
        "value": value,
        "floor_area": float(floor_area or 0.0),
        "plot_area": float(plot_area or 0.0),
    }


def density(count: float, area_m2: float) -> dict:
    """Densité en unités par hectare."""
    hectares = float(area_m2 or 0.0) / M2_PER_HA
    value = _ratio(float(count or 0.0), hectares)
    return {
        "value": value,
        "count": float(count or 0.0),
        "area_ha": hectares,
        "unit": "unités/ha",
    }


def compute_all(
    parts: Sequence[Mapping],
    total_area: float,
    built_area: float | None = None,
    floor_area: float | None = None,
    count: float | None = None,
    cbs_weights: Mapping[str, float] | None = None,
    runoff_weights: Mapping[str, float] | None = None,
) -> dict:
    """Calcule d'un coup les coefficients possibles à partir des données fournies.

    Un coefficient absent des résultats signifie que les données nécessaires
    n'ont pas été transmises : c'est volontaire, mieux vaut un trou qu'un
    chiffre inventé.
    """
    results: dict = {}
    impervious_area = sum(
        float(part.get("area") or 0.0)
        for part in parts
        if part.get("category") in IMPERVIOUS
    )
    if parts:
        results["cbs"] = weighted_ratio(parts, cbs_weights or CBS_WEIGHTS, total_area)
        results["ruissellement"] = weighted_ratio(
            parts, runoff_weights or RUNOFF_WEIGHTS, total_area, default_weight=0.5
        )
        results["imperm"] = coverage_ratio(parts, IMPERVIOUS, total_area)
        results["espace_vert"] = coverage_ratio(parts, VEGETATED, total_area)
    if built_area is not None:
        results["ces"] = footprint_ratio(built_area, total_area)
    elif parts and impervious_area:
        results["ces"] = footprint_ratio(
            sum(
                float(part.get("area") or 0.0)
                for part in parts
                if part.get("category") in ("bati", "toiture")
            ),
            total_area,
        )
    if floor_area is not None:
        results["cos"] = floor_area_ratio(floor_area, total_area)
    if count is not None:
        results["densite"] = density(count, total_area)
    return results


def interpret(code: str, value: float | None) -> str:
    """Phrase d'interprétation à destination du rapport d'étude."""
    if value is None:
        return "Valeur non calculable (surface de référence nulle)."
    if code == "imperm":
        percent = value * 100 if value <= 1 else value
        if percent >= 80:
            return "Imperméabilisation très forte : ruissellement important à gérer."
        if percent >= 50:
            return "Imperméabilisation élevée, typique d'un tissu urbain dense."
        if percent >= 20:
            return "Imperméabilisation modérée, tissu mixte."
        return "Imperméabilisation faible : sols majoritairement perméables."
    if code == "cbs":
        if value >= 0.6:
            return "Qualité écologique élevée des surfaces."
        if value >= 0.3:
            return "Qualité écologique moyenne."
        return "Qualité écologique faible : surfaces très minérales."
    if code == "ces":
        percent = value * 100 if value <= 1 else value
        if percent >= 60:
            return "Emprise au sol très dense."
        if percent >= 30:
            return "Emprise au sol intermédiaire."
        return "Emprise au sol faible : terrain largement libre."
    if code == "ruissellement":
        if value >= 0.8:
            return "Ruissellement quasi total : ouvrages de rétention indispensables."
        if value >= 0.5:
            return "Ruissellement important : rétention à prévoir."
        return "Ruissellement limité : infiltration encore possible."
    return ""
