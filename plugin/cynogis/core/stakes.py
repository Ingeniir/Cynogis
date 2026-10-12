"""Hiérarchisation des enjeux par règles pondérées. Python pur.

Chaque critère est une expression QGIS évaluée sur le polygone (ex. "nb_prot" > 0, ou une
note de rareté de 0 à 4) ramenée entre 0 et 1 par son maximum. Le score est la moyenne
pondérée des critères (0 à 100), traduite en niveau par des seuils. Des règles de
surclassement imposent un niveau minimal (ex. espèce protégée présente → au moins fort),
comme le font les méthodes d'évaluation des bureaux d'études.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

# Niveau → (libellé, couleur de la carte d'enjeux).
LEVELS = {1: ("Faible", "#1a9641"), 2: ("Modéré", "#a6d96a"), 3: ("Fort", "#fdae61"),
          4: ("Très fort", "#d7191c"), 5: ("Majeur", "#7b3294")}
# Score (0-100) à partir duquel on passe aux niveaux 2, 3, 4 et 5.
DEFAULT_THRESHOLDS = (20.0, 40.0, 60.0, 80.0)


@dataclass(frozen=True)
class Criterion:
    name: str
    expression: str
    weight: float
    max: float


@dataclass(frozen=True)
class Override:
    expression: str
    level: int
    label: str


def level_number(value) -> int:
    """Niveau à partir de son numéro (1-5) ou de son libellé (« fort »)."""
    text = str(value).strip().lower()
    if text.isdigit() and int(text) in LEVELS:
        return int(text)
    for number, (label, _) in LEVELS.items():
        if text == label.lower():
            return number
    raise ValueError(f"Niveau inconnu : {value!r} (1-5 ou "
                     f"{', '.join(label for label, _ in LEVELS.values())}).")


def parse_criteria(items: Sequence[Mapping]) -> list[Criterion]:
    if not items:
        raise ValueError("Au moins un critère est requis.")
    criteria = []
    for item in items:
        try:
            criterion = Criterion(str(item["name"]), str(item["expression"]),
                                  float(item.get("weight", 1)), float(item.get("max", 1)))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Critère invalide {dict(item)!r} : name et expression requis, "
                             "weight et max numériques.") from exc
        if criterion.weight <= 0 or criterion.max <= 0:
            raise ValueError(f"Critère {criterion.name} : weight et max doivent être > 0.")
        criteria.append(criterion)
    if len({c.name for c in criteria}) != len(criteria):
        raise ValueError("Noms de critères en double.")
    return criteria


def parse_overrides(items: Sequence[Mapping] | None) -> list[Override]:
    overrides = []
    for item in items or []:
        try:
            overrides.append(Override(str(item["expression"]), level_number(item["level"]),
                                      str(item.get("label") or item["expression"])))
        except KeyError as exc:
            raise ValueError("Règle de surclassement : expression et level requis.") from exc
    return overrides


def parse_thresholds(values: Sequence[float] | None) -> tuple[float, ...]:
    thresholds = tuple(float(v) for v in (values or DEFAULT_THRESHOLDS))
    if len(thresholds) != len(LEVELS) - 1 or list(thresholds) != sorted(set(thresholds)):
        raise ValueError(f"{len(LEVELS) - 1} seuils strictement croissants attendus (score "
                         "0-100), ex. [20, 40, 60, 80].")
    return thresholds


def to_score(value) -> float | None:
    """Valeur d'une expression → nombre (booléen = 0/1), None si nulle ou non numérique."""
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def score(values: Mapping[str, float | None], criteria: Sequence[Criterion]) -> float:
    """Score de 0 à 100 : moyenne pondérée des critères ramenés à 0-1 (valeur absente = 0)."""
    total = sum(c.weight for c in criteria)
    earned = sum(c.weight * min(max((values.get(c.name) or 0.0) / c.max, 0.0), 1.0)
                 for c in criteria)
    return round(earned / total * 100.0, 1)


def level_for(value: float, thresholds: Sequence[float]) -> int:
    return 1 + sum(1 for t in thresholds if value >= t)
