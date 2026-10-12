"""Quantification des impacts sur les habitats : catégories et tableau de synthèse. Python pur.

Impact direct : emprise du projet (éventuellement par nature, ex. définitive / temporaire).
Impact indirect : anneaux successifs autour de l'emprise (ex. 0-50 m, 50-200 m), emprise
exclue. Chaque mètre carré n'est compté qu'une fois, dans la catégorie la plus proche.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from .stakes import level_number

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


def stake_weight(stake: str | None, weights: dict[str, float] | None = None) -> float:
    """Poids d'un enjeu : table fournie, sinon valeur numérique (enj_niv 1-5), sinon niveau
    de la grille Cynogis (Faible = 1 … Majeur = 5), sinon 1."""
    if stake is None:
        return 1.0
    if weights and stake in weights:
        return float(weights[stake])
    try:
        return float(stake)
    except ValueError:
        pass
    try:
        return float(level_number(stake))
    except ValueError:
        return 1.0


def compare_variants(results: dict[str, dict], reference: str | None,
                     stakes: Sequence[str]) -> tuple[list[str], list[list]]:
    """Tableau comparatif des variantes : emprise, impacts direct et indirect, direct par
    enjeu, habitats touchés, observations sensibles, score pondéré, gain par rapport à la
    variante de référence (défaut : la plus impactante) et rang (1 = moindre impact)."""
    if not results:
        raise ValueError("Aucune variante à comparer.")
    scores = {name: r["weighted"] for name, r in results.items()}
    if reference is not None and reference not in results:
        raise ValueError(f"Variante de référence inconnue : {reference}.")
    ref = reference or max(scores, key=lambda n: (scores[n], results[n]["direct"]))
    order = sorted(results, key=lambda n: (scores[n], results[n]["direct"], n))
    headers = ["Variante", "Rang", "Emprise (ha)", "Impact direct (ha)",
               "Impact indirect (ha)", *[f"Direct enjeu {s} (ha)" for s in stakes],
               "Habitats touchés", "Observations sensibles (direct)",
               "Observations sensibles (indirect)", "Score pondéré",
               f"Direct évité / {ref} (ha)", f"Score évité / {ref} (%)"]
    rows = []
    for rank, name in enumerate(order, start=1):
        r = results[name]
        ref_r = results[ref]
        rows.append([name, rank, round(r["footprint"] / 10_000, 4),
                     round(r["direct"] / 10_000, 4), round(r["indirect"] / 10_000, 4),
                     *[round(r["by_stake"].get(s, 0.0) / 10_000, 4) for s in stakes],
                     r["habitats"], r.get("points_direct"), r.get("points_indirect"),
                     round(r["weighted"] / 10_000, 4),
                     round((ref_r["direct"] - r["direct"]) / 10_000, 4) + 0.0,  # pas de -0.0
                     round((ref_r["weighted"] - r["weighted"]) / ref_r["weighted"] * 100, 1)
                     if ref_r["weighted"] else None])
    return headers, rows
