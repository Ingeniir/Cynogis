"""Quantification des impacts sur les habitats : catégories et tableau de synthèse. Python pur.

Impact direct : emprise du projet (éventuellement par nature, ex. définitive / temporaire).
Impact indirect : anneaux successifs autour de l'emprise (ex. 0-50 m, 50-200 m), emprise
exclue. Chaque mètre carré n'est compté qu'une fois, dans la catégorie la plus proche.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

DIRECT = "direct"


def ring_labels(distances: Sequence[float]) -> list[str]:
    """Libellés des anneaux d'impact indirect, distances croissantes en mètres."""
    values = [float(d) for d in distances]
    if any(d <= 0 for d in values) or values != sorted(set(values)):
        raise ValueError("Distances d'impact indirect strictement croissantes et > 0 attendues, "
                         "ex. [50, 200].")
    bounds = [0.0, *values]
    return [f"indirect {bounds[i]:g}-{bounds[i + 1]:g} m" for i in range(len(values))]


def direct_label(nature: str | None) -> str:
    return f"{DIRECT} - {nature}" if nature else DIRECT


def build_table(pieces: Iterable[tuple[str, str | None, str, float]],
                habitat_totals: dict[tuple[str, str | None], float],
                categories: Sequence[str]) -> tuple[list[str], list[list]]:
    """Tableau par habitat (et enjeu) : surface (ha) par catégorie d'impact, total direct,
    surface de l'habitat dans la couche et part détruite (impact direct / surface)."""
    areas: dict[tuple[str, str | None], dict[str, float]] = {}
    for habitat, stake, category, area_m2 in pieces:
        bucket = areas.setdefault((habitat, stake), {})
        bucket[category] = bucket.get(category, 0.0) + area_m2
    headers = ["Habitat", "Enjeu", *[f"{c} (ha)" for c in categories],
               "Impact direct total (ha)", "Surface de l'habitat (ha)", "Part détruite (%)"]
    rows = []
    for key, bucket in areas.items():
        direct = sum(v for c, v in bucket.items() if c.startswith(DIRECT))
        total = habitat_totals.get(key, 0.0)
        rows.append([key[0], key[1], *[round(bucket.get(c, 0.0) / 10_000, 4)
                                       for c in categories],
                     round(direct / 10_000, 4), round(total / 10_000, 4),
                     round(direct / total * 100, 2) if total else None])
    width = len(categories)
    rows.sort(key=lambda r: (-r[2 + width], -sum(r[2:2 + width]), str(r[0])))
    sums = [round(sum(r[2 + i] for r in rows), 4) for i in range(width + 1)]
    rows.append(["Total", None, *sums, None, None])
    return headers, rows
