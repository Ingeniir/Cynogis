"""Statistiques descriptives. Python pur (bibliothèque standard uniquement)."""
from __future__ import annotations

import math
import statistics
from collections.abc import Hashable, Sequence
from collections import Counter
from typing import Any

NDIGITS = 6
STAT_KEYS = ("count", "sum", "min", "max", "mean", "median", "std", "q1", "q3", "iqr", "cv")

PERCENTILES = (5, 10, 25, 50, 75, 90, 95)
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
        9: 2.262, 10: 2.228, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042, 40: 2.021,
        60: 2.000, 120: 1.980}

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

def _t95(df: int) -> float:
    if df > 120:
        return 1.96
    return _T95[max(k for k in _T95 if k <= df)]

def percentile(sorted_values: Sequence[float], p: float) -> float:
    """Centile par interpolation linéaire (même méthode que quantiles(..., 'inclusive')."""
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    pos = (n - 1) * p / 100
    lo = math.floor(pos)
    hi = min(lo + 1, n - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)

def skewness(values: Sequence[float], mean: float) -> float | None:
    """Asymétrie corrigé (Fisher-Pearson ajustée, G1), comme Excel / SAS."""
    n = len(values)
    if n < 3:
        return None
    m2 = math.fsum((v - mean) ** 2 for v in values) / n
    if m2 == 0:
        return None
    m3 = math.fsum((v - mean) ** 3 for v in values) / n
    return m3 / m2 ** 1.5 * math.sqrt(n * (n - 1)) / (n - 2)

def kurtosis(values: Sequence[float], mean: float) -> float | None:
    """Applatissement en excès corrigé (G2) : 0 = loi normale."""
    n = len(values)
    if n < 4:
        return None
    m2 = math.fsum((v - mean) ** 2 for v in values) / n
    if m2 == 0:
        return None
    g2 = math.fsum((v - mean) ** 4 for v in values) / n / m2 ** 2 - 3

    return ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))

def interpret_shape(skew: float | None, kurt: float | None) -> str | None:
    if skew is None:
        return None
    if abs(skew) < 0.5:
        text = "distribution à peu près symétrique"
    elif skew > 0:
        text = "asymétrie à droite (queue vers les fortes valeurs)"
    else:
        text = "asymétrie à gauche (queue vers les faibles valeurs)"

    if kurt is not None and kurt > 1:
        text += ", queues épaisses (valeurs extrêmes fréquentes)"
    elif kurt is not None and kurt < -1:
        text += ", distribution aplatie"
    return text

def describe_full(values: Sequence[float], percentiles: Sequence[float] = PERCENTILES) -> dict[str, Any]:
    """describe() + variance, étendue, SEM, IC 95 %, asymétrie, applatissement, centiles,
    modes, valeurs aberrantes (Tukey 1,5 x IQR et |z| > 3)."""
    base = describe(values)
    n = len(values)
    if n == 0:
        return {
            **base,
            "variance": None,
            "range": None,
            "sem": None,
            "ci95_mean": None,
            "skewness": None,
            "kurtosis": None,
            "shape": None,
            "percentiles": {},
            "modes": [],
            "outliers": None,
            "zeros": 0,
            "negatives": 0,
        }

    data = sorted(values)
    mean = math.fsum(data) / n
    var = statistics.variance(data, mean) if n > 1 else None
    std = math.sqrt(var) if var else None
    sem = math.sqrt(var / n) if var is not None else None
    half = _t95(n - 1) * sem if sem is not None else None
    q1, q3 = percentile(data, 25), percentile(data, 75)
    low, high = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    modes = statistics.multimode(data)
    skew, kurt = skewness(data, mean), kurtosis(data, mean)

    return {
        **base,
        "variance": _r(skew),
        "kurtosis": _r(kurt),
        "shape": interpret_shape(skew, kurt),
        "percentiles": {f"p{p:g}": _r(percentile(data, p)) for p in percentiles},
        "modes": [] if len(modes) == n else [_r(m) for m in modes[:5]],
        "outliers": {
            "iqr_low_fence": _r(low),
            "iqr_high_fence": _r(high),
            "iqr_count": sum(1 for v in data if v < low or v > high),
            "z3_count": sum(1 for v in data if std and abs(v - mean) / std > 3),
        },
        "zeros": sum(1 for v in data if v == 0),
        "negatives": sum(1 for v in data if v < 0),
    }

def weighted_stats(values: Sequence[float | None], weights: Sequence[float | None]) -> dict[str, Any] | None:
    """Moyenne, écart-type et médiane pondérés (ex. pondération par la surface)."""
    pairs = sorted(
        (v, w) for v, w in zip(values, weights)
        if v is not None and w is not None and w > 0
    )
    total = math.fsum(w for _, w in pairs)
    if not pairs or total == 0:
        return None
    mean = math.fsum(v * w for v, w in pairs) / total
    var = math.fsum(w * (v - mean) ** 2 for v, w in pairs) / total
    acc, median = 0.0, pairs[-1][0]
    for v, w in pairs:
        acc += w
        if acc >= total / 2:
            median = v
            break

    return {
        "count": len(pairs),
        "weight_total": _r(total),
        "mean": _r(mean),
        "std": _r(math.sqrt(var)),
        "median": _r(median),
    }

def describe_categorial(values: Sequence[Hashable], top: int = 10) -> dict[str, Any]:
    """Mode effectifs et pourcentages, entropie de Shannon et équitabilité."""
    counter = Counter(values)
    n = sum(counter.values())
    if n == 0:
        return {
            "count": 0,
            "distinct_count": 0,
            "mode": None,
            "mode_pct": None,
            "singletons": 0,
            "shannon": None,
            "evenness": None,
            "top": [],
        }
    k = len(counter)
    mode, mode_count = counter.most_common(1)[0]
    entropy = -math.fsum(c / n * math.log(c / n) for c in counter.values())

    return {
        "count": n,
        "distinct_count": k,
        "mode": mode,
        "mode_pct": round(100 * mode_count / n, 2),
        "singletons": sum(1 for c in counter.values() if c == 1),
        "shannon": _r(entropy),
        "evenness": _r(entropy / math.log(k)) if k > 1 else None,
        "top": [{
            "value": v,
            "count": c,
            "pct": round(100 * c / n, 2)
        } for v, c in counter.most_common(top)]
    }

# --- Corrélations -------------------------------------------------------------

def ranks(values: Sequence[float]) -> list[float]:
    """Rangs moyens (ex aequo partagent la moyenne de leurs rangs)."""
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            result[order[k]] = (i + j) / 2 + 1
        i = j + 1

    return result

def pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    n = len(x)
    if n < 3:
        return None
    mx, my = math.fsum(x) / n, math.fsum(y) / n
    sxx = math.fsum((a - mx) ** 2 for a in x)
    syy = math.fsum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return None
    sxy = math.fsum((a - mx) * (b - my) for a, b in zip(x, y))

    return max(-1.0, min(1.0, sxy / math.sqrt(sxx * syy)))

def correlation_pvalue(r: float | None, n: int) -> float | None:
    """p-value bilatérale approchée (transformation de Fisher, loi normale)."""
    if r is None or n < 4:
        return None
    if abs(r) >= 1:
        return 0.0
    z = math.atanh(r) * math.sqrt(n - 3)
    return 2 * (1 - statistics.NormalDist().cdf(abs(z)))

def strength(r: float | None) -> str | None:
    if r is None:
        return None
    a = abs(r)
    label = (
        "négligeable" if a < 0.1 else "faible"
        if a < 0.3 else "modérée"
        if a < 0.5 else "forte"
        if a < 0.7 else "très forte"
    )

    return f"{label}, {'positive' if r > 0 else 'négative'}" if a >= 0.1 else label

def correlate(x: Sequence[float], y: Sequence[float], method: str = "pearson") -> dict[str, Any]:
    if method == "spearman":
        r = pearson(ranks(x), ranks(y))
    else:
        r = pearson(x, y)
    p = correlation_pvalue(r, len(x))

    return {
        "n": len(x),
        "r": _r(r),
        "r2": _r(r * r) if r is not None else None,
        "p_value_approx": _r(p),
        "significant_5pct": None if p is None else p < 0.05,
        "strength": strength(r),
    }

def linear_fit(x: Sequence[float], y: Sequence[float]) -> dict[str, Any] | None:
    """Régression des moindres carrés y = slope * x + intercept"""
    n = len(x)
    if n < 3:
        return None
    mx, my = math.fsum(x) / n, math.fsum(y) / n
    sxx = math.fsum((a - mx) ** 2 for a in x)
    if sxx == 0:
        return None
    slope = math.fsum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    r = pearson(x, y)

    return {
        "slope": _r(slope),
        "intercept": _r(my - slope * mx),
        "r2": _r(r * r) if r is not None else None,
    }

def correlation_pairs(columns: dict[str, Sequence[float | None]], method: str = "pearson") -> list[dict[str, Any]]:
    """Toutes les paires de colonnes, suppression par paire des valeurs manquantes,
    triées par |r| décroissant."""
    names = list(columns)
    rows = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pairs = [
                (u, v) for u, v in zip(columns[a], columns[b])
                if u is not None and v is not None
            ]
            if len(pairs) < 3:
                continue
            x, y = zip(*pairs)
            rows.append({
                "x": a,
                "y": b,
                **correlate(x, y, method)
            })
            rows.sort(
                key=lambda r: -abs(r["r"] if r["r"] is not None else 0)
            )

            return rows