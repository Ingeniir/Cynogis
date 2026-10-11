"""Calcul des seuils de classification pour les cartes en aplats de couleur.

Les méthodes reprennent celles de QGIS, mais implémentées ici pour rester
vérifiables par les tests et indépendantes de l'interface.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

METHODS = ("equal_interval", "quantile", "natural_breaks", "standard_deviation", "pretty")

METHOD_LABELS = {
    "equal_interval": "Intervalles égaux : classes de même amplitude.",
    "quantile": "Quantiles : classes contenant le même nombre d'entités.",
    "natural_breaks": "Seuils naturels (Jenks) : ruptures là où les données se regroupent.",
    "standard_deviation": "Écart-type : classes centrées sur la moyenne.",
    "pretty": "Seuils arrondis : bornes lisibles pour une légende.",
}

MAX_JENKS_SAMPLE = 1500


def clean_values(values: Sequence) -> list[float]:
    """Ne conserve que les nombres finis, triés par ordre croissant."""
    cleaned: list[float] = []
    for value in values:
        if value is None or isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            cleaned.append(number)
    cleaned.sort()
    return cleaned


def _dedupe(breaks: Sequence[float]) -> list[float]:
    """Supprime les bornes confondues, qui produiraient des classes vides."""
    result: list[float] = []
    for value in breaks:
        if not result or value > result[-1]:
            result.append(value)
    return result


def equal_interval(values: Sequence[float], classes: int) -> list[float]:
    """Seuils à amplitude constante entre le minimum et le maximum."""
    data = clean_values(values)
    if not data:
        return []
    low, high = data[0], data[-1]
    if low == high:
        return [low, high]
    step = (high - low) / classes
    return [low + step * index for index in range(classes + 1)]


def quantile_breaks(values: Sequence[float], classes: int) -> list[float]:
    """Seuils plaçant le même nombre d'entités dans chaque classe."""
    data = clean_values(values)
    if not data:
        return []
    size = len(data)
    breaks = [data[0]]
    for index in range(1, classes):
        position = index * size / classes
        low = math.floor(position)
        if low >= size - 1:
            breaks.append(data[-1])
            continue
        fraction = position - low
        breaks.append(data[low] + (data[low + 1] - data[low]) * fraction)
    breaks.append(data[-1])
    return _dedupe(breaks) or [data[0], data[-1]]


def natural_breaks(values: Sequence[float], classes: int) -> list[float]:
    """Seuils naturels de Jenks : minimise la variance à l'intérieur des classes.

    Au-delà de 1500 valeurs, un échantillon régulier est utilisé : le résultat
    reste représentatif et le calcul ne bloque pas l'interface de QGIS.
    """
    data = clean_values(values)
    if not data:
        return []
    if len(set(data)) <= classes:
        unique = sorted(set(data))
        return [unique[0], *unique[1:]] if len(unique) > 1 else [unique[0], unique[0]]
    if len(data) > MAX_JENKS_SAMPLE:
        step = len(data) / MAX_JENKS_SAMPLE
        sample = [data[int(index * step)] for index in range(MAX_JENKS_SAMPLE)]
        sample[0], sample[-1] = data[0], data[-1]
        data = sample

    size = len(data)
    limits = [[0] * (classes + 1) for _ in range(size + 1)]
    variances = [[float("inf")] * (classes + 1) for _ in range(size + 1)]
    for index in range(1, classes + 1):
        limits[1][index] = 1
        variances[1][index] = 0.0

    for row in range(2, size + 1):
        total = 0.0
        squares = 0.0
        count = 0.0
        variance = 0.0
        for offset in range(1, row + 1):
            start = row - offset + 1
            value = data[start - 1]
            squares += value * value
            total += value
            count += 1
            variance = squares - (total * total) / count
            previous = start - 1
            if previous:
                for index in range(2, classes + 1):
                    candidate = variance + variances[previous][index - 1]
                    if variances[row][index] >= candidate:
                        limits[row][index] = start
                        variances[row][index] = candidate
        limits[row][1] = 1
        variances[row][1] = variance

    breaks = [0.0] * (classes + 1)
    breaks[classes] = data[-1]
    breaks[0] = data[0]
    cursor = size
    for index in range(classes, 1, -1):
        position = int(limits[cursor][index]) - 2
        breaks[index - 1] = data[max(position, 0)]
        cursor = int(limits[cursor][index]) - 1
    return _dedupe(breaks)


def standard_deviation_breaks(values: Sequence[float], classes: int) -> list[float]:
    """Seuils espacés d'une fraction d'écart-type autour de la moyenne."""
    data = clean_values(values)
    if not data:
        return []
    mean = sum(data) / len(data)
    variance = sum((value - mean) ** 2 for value in data) / len(data)
    deviation = math.sqrt(variance)
    if deviation == 0:
        return [data[0], data[-1]]
    half = classes / 2.0
    breaks = [mean + (index - half) * deviation for index in range(classes + 1)]
    breaks[0] = min(breaks[0], data[0])
    breaks[-1] = max(breaks[-1], data[-1])
    return _dedupe(breaks)


def pretty_breaks(values: Sequence[float], classes: int) -> list[float]:
    """Seuils arrondis sur des valeurs rondes, agréables en légende."""
    data = clean_values(values)
    if not data:
        return []
    low, high = data[0], data[-1]
    if low == high:
        return [low, high]
    raw_step = (high - low) / classes
    magnitude = 10 ** math.floor(math.log10(raw_step))
    for factor in (1, 2, 2.5, 5, 10):
        step = factor * magnitude
        if step >= raw_step:
            break
    start = math.floor(low / step) * step
    breaks = [start]
    while breaks[-1] < high:
        breaks.append(breaks[-1] + step)
        if len(breaks) > classes * 4:  # garde-fou contre une boucle infinie
            break
    return _dedupe([round(value, 10) for value in breaks])


def compute_breaks(values: Sequence[float], method: str = "quantile", classes: int = 5) -> dict:
    """Calcule les seuils selon la méthode demandée et explique le résultat."""
    if method not in METHODS:
        raise ValueError(f"Méthode inconnue : {method} (attendu : {', '.join(METHODS)}).")
    if not 2 <= int(classes) <= 20:
        raise ValueError("Le nombre de classes doit être compris entre 2 et 20.")
    data = clean_values(values)
    warnings: list[str] = []
    if not data:
        raise ValueError("Aucune valeur numérique exploitable pour la classification.")
    if len(data) < int(classes):
        warnings.append(
            f"{len(data)} valeur(s) pour {classes} classes demandées : "
            "le nombre de classes a été réduit."
        )
        classes = max(2, len(data))

    computed = {
        "equal_interval": equal_interval,
        "quantile": quantile_breaks,
        "natural_breaks": natural_breaks,
        "standard_deviation": standard_deviation_breaks,
        "pretty": pretty_breaks,
    }[method](data, int(classes))
    computed = _dedupe(computed)
    if len(computed) < 2:
        computed = [data[0], data[-1] + (1.0 if data[0] == data[-1] else 0.0)]
    if len(computed) - 1 < int(classes):
        warnings.append(
            f"{len(computed) - 1} classe(s) obtenue(s) au lieu de {classes} : "
            "les valeurs sont trop peu variées pour aller plus loin."
        )
    return {
        "method": method,
        "method_label": METHOD_LABELS[method],
        "breaks": computed,
        "class_count": len(computed) - 1,
        "value_count": len(data),
        "min": data[0],
        "max": data[-1],
        "warnings": warnings,
    }


def format_number(value: float, decimals: int = 2) -> str:
    """Nombre formaté à la française : virgule décimale, espace des milliers."""
    rounded = round(float(value), int(decimals))
    if decimals <= 0:
        text = f"{round(rounded):,}".replace(",", " ")
        return text
    text = f"{rounded:,.{int(decimals)}f}"
    return text.replace(",", " ").replace(".", ",")


def range_labels(breaks: Sequence[float], decimals: int = 2, unit: str = "") -> list[str]:
    """Libellés de légende du type « 10,00 à 25,00 ha »."""
    suffix = f" {unit}" if unit else ""
    labels: list[str] = []
    for index in range(len(breaks) - 1):
        low = format_number(breaks[index], decimals)
        high = format_number(breaks[index + 1], decimals)
        labels.append(f"{low} à {high}{suffix}")
    return labels
