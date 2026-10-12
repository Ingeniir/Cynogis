"""Plans d'échantillonnage : répartition des unités entre strates. Python pur."""
from __future__ import annotations

import math
from collections.abc import Mapping

DESIGNS = ("random", "stratified", "systematic")
ALLOCATIONS = ("proportional", "equal")


def allocate(total: int, areas: Mapping[str, float], mode: str = "proportional",
             minimum: int = 1) -> dict[str, int]:
    """Répartit total unités entre les strates : proportionnellement à leur surface (après
    minimum par strate) ou à parts égales ; le reste va aux plus forts restes, puis aux
    plus grandes strates."""
    strata = [key for key, area in areas.items() if area > 0]
    if not strata:
        raise ValueError("Aucune strate de surface non nulle.")
    if total < minimum * len(strata):
        raise ValueError(f"{total} unité(s) pour {len(strata)} strates : au moins "
                         f"{minimum * len(strata)} nécessaires (minimum {minimum} par strate).")
    if mode not in ALLOCATIONS:
        raise ValueError(f"Répartition inconnue : {mode}.")
    weights = {k: (areas[k] if mode == "proportional" else 1.0) for k in strata}
    remaining = total - minimum * len(strata)
    weight_sum = sum(weights.values())
    shares = {k: remaining * weights[k] / weight_sum for k in strata}
    result = {k: minimum + math.floor(shares[k]) for k in strata}
    left = total - sum(result.values())
    order = sorted(strata, key=lambda k: (-(shares[k] - math.floor(shares[k])), -areas[k], k))
    for key in order[:left]:
        result[key] += 1
    return result


def unit_id(prefix: str, index: int, total: int) -> str:
    """Identifiant lisible et triable : P001, T012…"""
    return f"{prefix}{index:0{max(3, len(str(total)))}d}"
