"""Mise en page de l'atlas : formats et zones de la page, en millimètres. Python pur."""
from __future__ import annotations

from dataclasses import dataclass

# Format → (largeur, hauteur) en paysage, mm.
PAGE_SIZES = {"A4": (297.0, 210.0), "A3": (420.0, 297.0)}
ORIENTATIONS = ("landscape", "portrait")
MARGIN = 10.0
HEADER = 16.0
FOOTER = 10.0
GAP = 4.0
LEGEND_WIDTH = 62.0    # paysage : légende à droite de la carte
LEGEND_HEIGHT = 50.0   # portrait : légende sous la carte
OVERVIEW_SIZE = 50.0   # carte de localisation : hauteur en paysage, largeur en portrait


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    width: float
    height: float


def page_size(size: str, orientation: str) -> tuple[float, float]:
    if size not in PAGE_SIZES:
        raise ValueError(f"Format inconnu : {size} ({', '.join(PAGE_SIZES)}).")
    if orientation not in ORIENTATIONS:
        raise ValueError(f"Orientation inconnue : {orientation}.")
    width, height = PAGE_SIZES[size]
    return (width, height) if orientation == "landscape" else (height, width)


def layout_boxes(size: str, orientation: str, legend: bool,
                 overview: bool = False) -> dict[str, Box]:
    """Zones de la page (origine en haut à gauche) : title, map, legend et overview (carte
    de localisation) si demandées, footer. Paysage : colonne à droite de la carte,
    localisation en haut ; portrait : bandeau sous la carte, localisation à gauche."""
    width, height = page_size(size, orientation)
    inner_w = width - 2 * MARGIN
    top = MARGIN + HEADER + GAP
    bottom = height - MARGIN - FOOTER - GAP
    boxes = {"title": Box(MARGIN, MARGIN, inner_w, HEADER),
             "footer": Box(MARGIN, height - MARGIN - FOOTER, inner_w, FOOTER)}
    if not (legend or overview):
        boxes["map"] = Box(MARGIN, top, inner_w, bottom - top)
        return boxes
    if orientation == "landscape":
        map_w = inner_w - LEGEND_WIDTH - GAP
        boxes["map"] = Box(MARGIN, top, map_w, bottom - top)
        x, y = MARGIN + map_w + GAP, top
        if overview:
            boxes["overview"] = Box(x, y, LEGEND_WIDTH, OVERVIEW_SIZE)
            y += OVERVIEW_SIZE + GAP
        if legend:
            boxes["legend"] = Box(x, y, LEGEND_WIDTH, bottom - y)
    else:
        map_h = bottom - top - LEGEND_HEIGHT - GAP
        boxes["map"] = Box(MARGIN, top, inner_w, map_h)
        x, y = MARGIN, top + map_h + GAP
        if overview:
            boxes["overview"] = Box(x, y, OVERVIEW_SIZE, LEGEND_HEIGHT)
            x += OVERVIEW_SIZE + GAP
        if legend:
            boxes["legend"] = Box(x, y, MARGIN + inner_w - x, LEGEND_HEIGHT)
    return boxes
