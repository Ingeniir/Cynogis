"""Conversion d'unités de surface et de longueur. Python pur."""
from __future__ import annotations

AREA_UNITS: dict[str, float] = {"m2": 1.0, "a": 100.0, "ha": 10_000.0, "km2": 1_000_000.0}
LENGTH_UNITS: dict[str, float] = {"m": 1.0, "km": 1_000.0}


def convert_area(value_m2: float, unit: str) -> float:
    try:
        return value_m2 / AREA_UNITS[unit]
    except KeyError as exc:
        raise ValueError(f"Unité de surface inconnue : {unit}") from exc


def convert_length(value_m: float, unit: str) -> float:
    try:
        return value_m / LENGTH_UNITS[unit]
    except KeyError as exc:
        raise ValueError(f"Unité de longueur inconnue : {unit}") from exc
