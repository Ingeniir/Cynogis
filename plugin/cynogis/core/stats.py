"""Statistiques descriptives. Python pur (bibliothèque standard uniquement)."""
from __future__ import annotations

import math
import statistics
from collections.abc import Hashable, Sequence
from typing import Any

NDIGITS = 6
STAT_KEYS = ("count", "sum", "min", "max", "mean", "median", "std", "q1", "q3", "iqr", "cv")


def to_float(value: Any) -> float | None:
    """Convertit en nombre fini, ou None (valeurs nulles, texte non numérique, NaN, booléens)."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(number) or math.isinf(number) else number


def _r(value: float | None) -> float | None:
    return None if value is None else round(value, NDIGITS)


def describe(values: Sequence[float]) -> dict[str, Any]:
    """count, sum, min, max, moyenne, médiane, écart-type (échantillon), quartiles, IQR, CV."""
    n = len(values)
    if n == 0:
        return {key: (0 if key == "count" else None) for key in STAT_KEYS}
    total = math.fsum(values)
    mean = total / n
    std = statistics.stdev(values) if n > 1 else None
    if n > 1:
        q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    else:
        q1 = q3 = values[0]
    cv = std / abs(mean) if std is not None and mean != 0 else None
    return {
        "count": n, "sum": _r(total), "min": _r(min(values)), "max": _r(max(values)),
        "mean": _r(mean), "median": _r(statistics.median(values)), "std": _r(std),
        "q1": _r(q1), "q3": _r(q3), "iqr": _r(q3 - q1), "cv": _r(cv),
    }


def describe_groups(values_by_group: dict[Hashable, list[float]]) -> list[dict[str, Any]]:
    """Statistiques par groupe, triées par somme décroissante."""
    rows = [{"group": key, **describe(values)} for key, values in values_by_group.items()]
    rows.sort(key=lambda r: r["sum"] if r["sum"] is not None else -math.inf, reverse=True)
    return rows
