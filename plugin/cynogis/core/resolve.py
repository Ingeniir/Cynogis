"""Décisions de résolution des chevauchements de polygones.

Module pur : il décide *qui garde quoi*, sans manipuler de géométrie QGIS.
Le calcul géométrique correspondant vit dans `tools/overlaps.py`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

STRATEGIES = ("priority_field", "keep_largest", "keep_oldest", "split_equally")
ORDERS = ("asc", "desc")

def needs_priority_field(strategy: str) -> bool:
    """Vrai si la stratégie exige qu'un champ de priorité soit fourni."""
    return strategy == "priority_field"

def _comparable(value: Any) -> tuple[int, float, str]:
    """Clé de tri homogène pour des valeurs de types mélangés."""
    if isinstance(value, bool):
        return 0, float(int(value)), ""
    if isinstance(value, (int, float)):
        return 0, float(value), ""
    return 1, 0.0, str(value)

def rank_records(
        records: Sequence[dict],
        strategy: str,
        priority_order: str = "asc",
) -> dict[Any, int]:
    """Classe les entités de la plus prioritaire (rang 0) à la moins prioritaire.

    Chaque enregistrement est un dict ``{"id", "order", "area", "value"}`` où
    ``order`` est l'ordre de lecture dans la couche et ``value`` la valeur du
    champ de priorité (ou None). En cas d'égalité, l'ordre de lecture tranche,
    ce qui rend le résultat reproductible d'une exécution à l'autre.
    """
    if strategy not in STRATEGIES:
        raise ValueError(f"Stratégie inconnue : {strategy}")
    if priority_order not in ORDERS:
        raise ValueError(f"Ordre inconnu : {priority_order}")

    ordered = sorted(records, key=lambda record: record.get("order", 0))

    if strategy == "keep_largest":
        ordered.sort(key=lambda record: float(record.get("area") or 0.0), reverse=True)
    elif strategy in ("priority_field", "keep_oldest"):
        known = [r for r in ordered if r.get("value") is not None]
        unknown = [r for r in ordered if r.get("value") is None]
        reverse = strategy == "priority_field" and priority_order == "desc"
        known.sort(key=lambda record: _comparable(record.get("value")), reverse=reverse)
        ordered = known + unknown

    return {record["id"]: rank for rank, record in enumerate(ordered)}

def half_plane_corners(
    ax: float, ay: float, bx: float, by: float, size: float
) -> list[tuple[float, float]]:
    """Coins du demi-plan des points plus proches de A que de B.

    Utilisé par la stratégie `split_equally` : l'intersection des demi-plans
    construits face à chaque voisin est exactement la cellule de Voronoï de A.
    Le rectangle renvoyé est volontairement surdimensionné (`size`) pour couvrir
    toute l'emprise de travail.
    """
    dx, dy = bx - ax, by - ay
    norm = (dx * dx + dy * dy) ** 0.5
    if norm == 0.0:
        raise ValueError("Les deux centres sont confondus : partage impossible.")
    ux, uy = dx / norm, dy / norm          # direction A -> B
    px, py = -uy, ux                        # perpendiculaire
    mx, my = (ax + bx) / 2.0, (ay + by) / 2.0  # point milieu (sur la médiatrice)
    return [
        (mx + px * size, my + py * size),
        (mx - px * size, my - py * size),
        (mx - px * size - ux * size, my - py * size - uy * size),
        (mx + px * size - ux * size, my + py * size - uy * size),
    ]


def summarize_resolution(entries: Sequence[dict]) -> dict:
    """Agrège le journal de résolution en quelques indicateurs lisibles."""
    kept = [e for e in entries if e["status"] != "removed"]
    clipped = [e for e in entries if e["status"] == "clipped"]
    removed = [e for e in entries if e["status"] == "removed"]
    area_before = sum(float(e.get("area_before") or 0.0) for e in entries)
    area_after = sum(float(e.get("area_after") or 0.0) for e in entries)
    return {
        "features_in": len(entries),
        "features_out": len(kept),
        "features_clipped": len(clipped),
        "features_removed": len(removed),
        "area_before": area_before,
        "area_after": area_after,
        "area_removed": max(area_before - area_after, 0.0),
    }
