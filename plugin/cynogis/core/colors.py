"""Analyse, validation et manipulation des couleurs.

L'IA choisit librement ses couleurs, mais elles transitent par ce module :
une valeur refusée ici n'atteindra jamais QGIS. Aucune dépendance externe.
"""

from __future__ import annotations

import colorsys
import re
from collections.abc import Iterable, Sequence

HEX_PATTERN = re.compile(r"^#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGB_PATTERN = re.compile(
    r"^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([01](?:\.\d+)?)\s*)?\)$",
    re.IGNORECASE,
)

# Couleurs nommées acceptées, en français et en anglais : l'IA écrit souvent
# « vert foncé » plutôt qu'un code hexadécimal.
NAMED_COLORS: dict[str, str] = {
    "blanc": "#ffffff", "white": "#ffffff",
    "noir": "#000000", "black": "#000000",
    "gris": "#808080", "grey": "#808080", "gray": "#808080",
    "gris_clair": "#d9d9d9", "gris_fonce": "#4d4d4d",
    "rouge": "#d7191c", "red": "#d7191c",
    "orange": "#fc8d59",
    "jaune": "#ffd92f", "yellow": "#ffd92f",
    "vert": "#1a9641", "green": "#1a9641",
    "vert_clair": "#a6d96a", "vert_fonce": "#006837",
    "bleu": "#2166ac", "blue": "#2166ac",
    "bleu_clair": "#92c5de", "bleu_fonce": "#1f4e79",
    "violet": "#762a83", "purple": "#762a83",
    "rose": "#f4a6c0", "pink": "#f4a6c0",
    "marron": "#8c510a", "brown": "#8c510a",
    "beige": "#e6d8a0", "turquoise": "#35978f",
    "transparent": "#00000000",
}

def parse_color(value) -> tuple[int, int, int, int]:
    """Convertit une couleur libre en quadruplet (r, v, b, alpha).

    Accepte « #1a9641 », « 1a9641 », « #fff », « rgb(26,150,65) »,
    « rgba(26,150,65,0.5) », un nom français ou anglais, ou un triplet.
    """
    if value is None:
        raise ValueError("Couleur absente.")
    if isinstance(value, (list, tuple)):
        parts = list(value)
        if len(parts) not in (3, 4):
            raise ValueError(f"Couleur invalide : {value!r} (3 ou 4 composantes attendues).")
        channels = [round(float(part)) for part in parts[:3]]
        alpha = round(float(parts[3])) if len(parts) == 4 else 255
        if any(not 0 <= channel <= 255 for channel in [*channels, alpha]):
            raise ValueError(f"Composantes hors de l'intervalle 0-255 : {value!r}")
        return channels[0], channels[1], channels[2], alpha

    text = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if text in NAMED_COLORS:
        text = NAMED_COLORS[text]
    match = RGB_PATTERN.match(str(value).strip())
    if match:
        channels = [int(match.group(index)) for index in (1, 2, 3)]
        alpha = float(match.group(4)) if match.group(4) else 1.0
        if any(not 0 <= channel <= 255 for channel in channels):
            raise ValueError(f"Composantes hors de l'intervalle 0-255 : {value!r}")
        return channels[0], channels[1], channels[2], round(alpha * 255)
    if not HEX_PATTERN.match(text):
        raise ValueError(
            f"Couleur invalide : {value!r}. Utilisez un code hexadécimal "
            "(#1a9641), un triplet rgb() ou un nom reconnu."
        )
    digits = text.lstrip("#")
    if len(digits) == 3:
        digits = "".join(digit * 2 for digit in digits)
    red = int(digits[0:2], 16)
    green = int(digits[2:4], 16)
    blue = int(digits[4:6], 16)
    alpha = int(digits[6:8], 16) if len(digits) == 8 else 255
    return red, green, blue, alpha

def to_hex(color, with_alpha: bool = False) -> str:
    """Forme hexadécimale normalisée d'une couleur."""
    red, green, blue, alpha = parse_color(color)
    if with_alpha or alpha != 255:
        return f"#{red:02x}{green:02x}{blue:02x}{alpha:02x}"
    return f"#{red:02x}{green:02x}{blue:02x}"


def to_rgba_string(color) -> str:
    """Forme « r,v,b,a » attendue par les propriétés de symbole QGIS."""
    red, green, blue, alpha = parse_color(color)
    return f"{red},{green},{blue},{alpha}"


def with_alpha(color, opacity: float):
    """Applique une opacité (0 à 1) à une couleur."""
    red, green, blue, _ = parse_color(color)
    ratio = max(0.0, min(float(opacity), 1.0))
    return (red, green, blue, round(ratio * 255))


def mix(first, second, ratio: float) -> str:
    """Mélange deux couleurs, ratio 0 pour la première, 1 pour la seconde."""
    r1, g1, b1, a1 = parse_color(first)
    r2, g2, b2, a2 = parse_color(second)
    weight = max(0.0, min(float(ratio), 1.0))

    def blend(start: int, end: int) -> int:
        return round(start + (end - start) * weight)

    return to_hex((blend(r1, r2), blend(g1, g2), blend(b1, b2), blend(a1, a2)), True)


def lighten(color, amount: float = 0.3) -> str:
    """Éclaircit une couleur en la mélangeant à du blanc."""
    return mix(color, "#ffffff", amount)


def darken(color, amount: float = 0.3) -> str:
    """Assombrit une couleur en la mélangeant à du noir."""
    return mix(color, "#000000", amount)


def relative_luminance(color) -> float:
    """Luminance relative selon la recommandation d'accessibilité WCAG."""
    red, green, blue, _ = parse_color(color)

    def channel(value: int) -> float:
        ratio = value / 255.0
        return ratio / 12.92 if ratio <= 0.03928 else ((ratio + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)


def contrast_ratio(first, second) -> float:
    """Rapport de contraste entre deux couleurs, de 1 à 21."""
    light = relative_luminance(first)
    dark = relative_luminance(second)
    high, low = max(light, dark), min(light, dark)
    return (high + 0.05) / (low + 0.05)


def readable_text_color(background) -> str:
    """Noir ou blanc selon ce qui se lit le mieux sur un fond donné.

    Sert à choisir automatiquement la couleur d'une étiquette posée sur un
    aplat : au-delà de 4,5 le texte reste lisible pour tous.
    """
    return "#000000" if contrast_ratio(background, "#000000") >= 4.5 else "#ffffff"


def interpolate_ramp(colors: Sequence, count: int) -> list[str]:
    """Étire une liste de couleurs sur le nombre de classes demandé.

    Deux couleurs et cinq classes donnent un dégradé de cinq teintes ; dix
    couleurs et trois classes en sélectionnent trois réparties régulièrement.
    """
    stops = [to_hex(color, True) for color in colors]
    if not stops:
        raise ValueError("Aucune couleur fournie pour le dégradé.")
    size = int(count)
    if size <= 0:
        raise ValueError("Le nombre de couleurs demandé doit être positif.")
    if size == 1:
        return [stops[0]]
    if len(stops) == 1:
        return [stops[0]] * size
    result: list[str] = []
    for index in range(size):
        position = index / (size - 1) * (len(stops) - 1)
        low = int(position)
        high = min(low + 1, len(stops) - 1)
        result.append(mix(stops[low], stops[high], position - low))
    return result


def distinct_colors(count: int, saturation: float = 0.65, value: float = 0.85) -> list[str]:
    """Couleurs bien séparées pour des catégories sans palette imposée.

    Les teintes sont réparties selon l'angle d'or : deux catégories voisines
    ne risquent pas de se ressembler, même nombreuses.
    """
    size = int(count)
    if size <= 0:
        return []
    golden = 0.618033988749895
    colors: list[str] = []
    hue = 0.1
    for _ in range(size):
        red, green, blue = colorsys.hsv_to_rgb(hue % 1.0, saturation, value)
        colors.append(
            to_hex((int(red * 255), int(green * 255), int(blue * 255), 255))
        )
        hue += golden
    return colors


def validate_colors(values: Iterable) -> list[str]:
    """Valide une liste de couleurs et la renvoie normalisée."""
    normalized: list[str] = []
    for index, value in enumerate(values):
        try:
            normalized.append(to_hex(value, True))
        except ValueError as exc:
            raise ValueError(f"Couleur n°{index + 1} : {exc}") from exc
    return normalized
