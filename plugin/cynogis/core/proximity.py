"""Plus proches voisins, matrices de distances et polygones à partir de points. Python pur."""
from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import Any

from .stats import to_float


def nearest(candidates: Iterable[tuple[Hashable, float]], k: int,
            max_distance: float | None = None) -> list[tuple[Hashable, float]]:
    """Les k candidats (identifiant, distance) les plus proches, au plus à max_distance.

    Égalités départagées par l'identifiant : résultat reproductible d'un appel à l'autre.
    """
    kept = [(ident, d) for ident, d in candidates if max_distance is None or d <= max_distance]
    kept.sort(key=lambda item: (item[1], str(item[0])))
    return kept[:k]


def distance_matrix(rows: Sequence[tuple[Hashable, Any]], columns: Sequence[tuple[Hashable, Any]],
                    distances: Mapping[tuple[Hashable, Hashable], float],
                    ndigits: int = 2) -> dict:
    """Matrice lisible : rows et columns sont des couples (clé, libellé), distances est
    indexé par (clé ligne, clé colonne). Case absente = None."""
    return {
        "columns": [label for _, label in columns],
        "rows": [{"id": label,
                  "distances": [None if (key, col) not in distances
                                else round(distances[(key, col)], ndigits)
                                for col, _ in columns]}
                 for key, label in rows],
    }


def _order_key(value: Any) -> tuple:
    """Ordre numérique si possible (2 avant 10), puis texte ; valeurs absentes en dernier."""
    if value is None:
        return (2, 0.0, "")
    number = to_float(value)
    return (0, number, "") if number is not None else (1, 0.0, str(value))


def ordered_ring(points: Sequence[tuple[Any, float, float]]) -> list[tuple[float, float]]:
    """Anneau fermé à partir de points (ordre, x, y), reliés dans l'ordre croissant.

    Les doublons consécutifs (point levé deux fois) sont retirés ; le premier point est
    répété à la fin pour fermer l'anneau.
    """
    ring: list[tuple[float, float]] = []
    for _, x, y in sorted(points, key=lambda point: _order_key(point[0])):
        if not ring or ring[-1] != (x, y):
            ring.append((x, y))
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring.pop()
    if len(set(ring)) < 3:
        raise ValueError("Au moins 3 points distincts sont nécessaires pour former un polygone.")
    return [*ring, ring[0]]


INSIDE = "dans l'emprise"


def setback_status(distance_m: float, threshold_m: float | None) -> str:
    """Position d'une entité sensible par rapport à l'emprise et à son seuil de recul."""
    if distance_m <= 0:
        return INSIDE
    if threshold_m is None:
        return "hors emprise"
    return "sous le seuil" if distance_m < threshold_m else "au-delà du seuil"
