"""Palettes de couleurs nommées et palettes enregistrées par l'utilisateur.

Les palettes fournies sont des suites de couleurs usuelles en cartographie
thématique. L'IA reste libre d'en proposer d'autres : elles ne sont qu'un
point de départ commode.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from .colors import distinct_colors, interpolate_ramp, validate_colors
from .naming import clean_name

PALETTES_FILE = Path.home() / ".cynogis" / "palettes.json"

SEQUENTIAL = {
    "vert": ["#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"],
    "bleu": ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"],
    "orange": ["#feedde", "#fdbe85", "#fd8d3c", "#e6550d", "#a63603"],
    "rouge": ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
    "violet": ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"],
    "gris": ["#f7f7f7", "#cccccc", "#969696", "#636363", "#252525"],
    "chaleur": ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
    "terre": ["#f6e8c3", "#dfc27d", "#bf812d", "#8c510a", "#543005"],
}

DIVERGING = {
    "rouge_vert": ["#d73027", "#fc8d59", "#fee08b", "#d9ef8b", "#91cf60", "#1a9850"],
    "vert_rouge": ["#1a9850", "#91cf60", "#d9ef8b", "#fee08b", "#fc8d59", "#d73027"],
    "bleu_rouge": ["#2166ac", "#67a9cf", "#d1e5f0", "#fddbc7", "#ef8a62", "#b2182b"],
    "brun_turquoise": ["#8c510a", "#d8b365", "#f6e8c3", "#c7eae5", "#5ab4ac", "#01665e"],
    "spectral": ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"],
}

QUALITATIVE = {
    "contraste": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
                  "#ffff33", "#a65628", "#f781bf", "#999999"],
    "pastel": ["#b3e2cd", "#fdcdac", "#cbd5e8", "#f4cae4", "#e6f5c9",
               "#fff2ae", "#f1e2cc", "#cccccc"],
    "sobre": ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854",
              "#ffd92f", "#e5c494", "#b3b3b3"],
}

# Palettes maison, pensées pour les restitutions du bureau d'études.
THEMATIC = {
    "pente": ["#1a9850", "#91cf60", "#fee08b", "#fc8d59", "#d73027"],
    "impermeabilisation": ["#1a9850", "#a6d96a", "#fee08b", "#fc8d59", "#d73027"],
    "vegetation": ["#ffffcc", "#c2e699", "#78c679", "#31a354", "#006837"],
    "eau": ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
}

FAMILIES = {
    "sequentielle": SEQUENTIAL,
    "divergente": DIVERGING,
    "qualitative": QUALITATIVE,
    "thematique": THEMATIC,
}

USER_PALETTES: dict[str, list[str]] = {}


def all_palettes() -> dict[str, list[str]]:
    """Toutes les palettes disponibles, utilisateur compris."""
    merged: dict[str, list[str]] = {}
    for family in FAMILIES.values():
        merged.update(family)
    merged.update(USER_PALETTES)
    return merged


def describe_palettes() -> dict:
    """Catalogue des palettes, classées par famille, pour l'IA."""
    catalogue = {
        family: {name: list(colors) for name, colors in palettes.items()}
        for family, palettes in FAMILIES.items()
    }
    if USER_PALETTES:
        catalogue["enregistrees"] = {
            name: list(colors) for name, colors in USER_PALETTES.items()
        }
    return catalogue


def get_palette(name: str, count: int | None = None, reverse: bool = False) -> list[str]:
    """Renvoie une palette nommée, étirée au nombre de classes demandé."""
    palettes = all_palettes()
    key = str(name or "").strip().lower()
    if key not in palettes:
        raise ValueError(
            f"Palette inconnue : {name}. Palettes disponibles : "
            f"{', '.join(sorted(palettes))}."
        )
    colors = list(palettes[key])
    if reverse:
        colors.reverse()
    return interpolate_ramp(colors, count) if count else colors


def resolve_colors(
    count: int,
    palette: str | None = None,
    colors: Sequence | None = None,
    reverse: bool = False,
) -> list[str]:
    """Détermine les couleurs à utiliser pour un nombre de classes donné.

    Priorité aux couleurs explicitement fournies, puis à la palette nommée,
    puis à une génération automatique de teintes bien distinctes.
    """
    if colors:
        validated = validate_colors(colors)
        if reverse:
            validated.reverse()
        if len(validated) < count:
            return interpolate_ramp(validated, count)
        return validated[:count]
    if palette:
        return get_palette(palette, count, reverse)
    generated = distinct_colors(count)
    if reverse:
        generated.reverse()
    return generated


def validate_palette(name: str, colors: Sequence) -> tuple[str, list[str]]:
    """Valide une palette destinée à être enregistrée."""
    key = clean_name(str(name or ""), "palette")
    validated = validate_colors(colors)
    if len(validated) < 2:
        raise ValueError("Une palette doit comporter au moins deux couleurs.")
    if len(validated) > 30:
        raise ValueError("Une palette est limitée à 30 couleurs.")
    return key, validated


def register_palette(name: str, colors: Sequence) -> str:
    """Ajoute une palette à celles de la session."""
    key, validated = validate_palette(name, colors)
    USER_PALETTES[key] = validated
    return key


def load_user_palettes(data: Mapping) -> dict:
    """Charge les palettes enregistrées, en ignorant les entrées fautives.

    Un fichier abîmé ne doit jamais empêcher le plugin de démarrer : les
    palettes illisibles sont écartées et signalées.
    """
    loaded: dict[str, list[str]] = {}
    rejected: list[str] = []
    for name, colors in (data or {}).items():
        try:
            key, validated = validate_palette(name, colors)
            loaded[key] = validated
        except (ValueError, TypeError):
            rejected.append(str(name))
    USER_PALETTES.update(loaded)
    return {"loaded": sorted(loaded), "rejected": rejected}


def landscape_palette(classes) -> dict[str, str]:
    """Couleurs suggérées par la nomenclature des paysages, par code."""
    return {item.code: item.color for item in classes}
