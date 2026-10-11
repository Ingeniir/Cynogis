"""Classes de pente et seuils de relief.

À La Réunion comme à Mayotte, la pente conditionne presque tout : accès,
constructibilité, érosion, type de culture. Les seuils ci-dessous sont les
classes d'usage courant en bureau d'études ; ils sont paramétrables.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class SlopeClass:
    """Une classe de pente, bornée en pourcentage."""

    code: int
    label: str
    min_percent: float
    max_percent: float
    color: str
    comment: str

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "label": self.label,
            "min_percent": self.min_percent,
            "max_percent": self.max_percent,
            "suggested_color": self.color,
            "comment": self.comment,
        }


SLOPE_CLASSES: tuple[SlopeClass, ...] = (
    SlopeClass(1, "Plat à faible (0-5 %)", 0.0, 5.0, "#1a9850",
               "Mécanisable, constructible sans contrainte de pente."),
    SlopeClass(2, "Modérée (5-15 %)", 5.0, 15.0, "#91cf60",
               "Aménageable, terrassements limités."),
    SlopeClass(3, "Forte (15-30 %)", 15.0, 30.0, "#fee08b",
               "Terrassements importants, érosion à surveiller."),
    SlopeClass(4, "Très forte (30-50 %)", 30.0, 50.0, "#fc8d59",
               "Aménagement difficile, risque d'érosion marqué."),
    SlopeClass(5, "Escarpée (> 50 %)", 50.0, float("inf"), "#d73027",
               "Remparts et ravines : zone généralement inconstructible."),
)

# Orientations des versants, en degrés depuis le nord.
ASPECT_SECTORS = (
    ("N", 337.5, 22.5), ("NE", 22.5, 67.5), ("E", 67.5, 112.5), ("SE", 112.5, 157.5),
    ("S", 157.5, 202.5), ("SO", 202.5, 247.5), ("O", 247.5, 292.5), ("NO", 292.5, 337.5),
)


def slope_class(percent: float) -> SlopeClass | None:
    """Classe de pente correspondant à une valeur en pourcentage."""
    if percent is None or percent < 0:
        return None
    for item in SLOPE_CLASSES:
        if item.min_percent <= percent < item.max_percent:
            return item
    return SLOPE_CLASSES[-1]


def degrees_to_percent(degrees: float) -> float:
    """Convertit une pente exprimée en degrés vers un pourcentage."""
    return math.tan(math.radians(float(degrees))) * 100.0


def percent_to_degrees(percent: float) -> float:
    """Convertit une pente exprimée en pourcentage vers des degrés."""
    return math.degrees(math.atan(float(percent) / 100.0))


def reclass_table(unit: str = "percent") -> list[list[float]]:
    """Table de reclassement pour l'algorithme de reclassification raster.

    Format attendu par QGIS : [min, max, valeur] à plat, bornes exclusives en
    haut. Le MNT peut produire des pentes en degrés ou en pourcentage selon
    l'algorithme employé : on convertit les bornes en conséquence.
    """
    table: list[list[float]] = []
    for item in SLOPE_CLASSES:
        low = item.min_percent
        high = item.max_percent
        if unit == "degrees":
            low = percent_to_degrees(low)
            high = 90.0 if high == float("inf") else percent_to_degrees(high)
        elif high == float("inf"):
            high = 10_000.0
        table.append([low, high, item.code])
    return table


def aspect_sector(degrees: float) -> str | None:
    """Secteur cardinal d'une exposition en degrés (0 = nord, sens horaire).

    Une valeur négative signale un terrain plat, pour lequel l'exposition n'a
    pas de sens.
    """
    if degrees is None or degrees < 0:
        return None
    value = float(degrees) % 360.0
    for name, start, end in ASPECT_SECTORS:
        if start > end:  # secteur nord, à cheval sur 0°
            if value >= start or value < end:
                return name
        elif start <= value < end:
            return name
    return "N"


def distribution(values: Sequence[float]) -> dict:
    """Répartition d'un échantillon de pentes par classe."""
    counts: dict[int, int] = {}
    for value in values:
        item = slope_class(value)
        if item is not None:
            counts[item.code] = counts.get(item.code, 0) + 1
    total = sum(counts.values())
    return {
        "total": total,
        "classes": [
            {
                "code": item.code,
                "label": item.label,
                "count": counts.get(item.code, 0),
                "percent": (counts.get(item.code, 0) / total * 100.0) if total else None,
            }
            for item in SLOPE_CLASSES
        ],
    }
