"""Métriques paysagères calculées à partir de surfaces et de périmètres.

Les formules reprennent celles de FRAGSTATS dans leur version vectorielle.
Chaque fonction prend des nombres et renvoie des nombres : la géométrie est
mesurée ailleurs, ce qui rend ces indices vérifiables à la main.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

M2_PER_HA = 10_000.0


def shape_index(area: float, perimeter: float) -> float | None:
    """Indice de forme : 1 pour un disque, augmente avec la complexité.

    Égal au rapport entre le périmètre observé et celui d'un disque de même
    surface (identique à la compacité de Gravelius des bassins versants). Un
    bosquet découpé et une tache compacte de même surface se distinguent par
    cet indice.
    """
    if area is None or perimeter is None or area <= 0 or perimeter <= 0:
        return None
    return perimeter / (2.0 * math.sqrt(math.pi * area))


def fractal_dimension(area: float, perimeter: float) -> float | None:
    """Dimension fractale du contour, entre 1 (simple) et 2 (très découpé)."""
    if not area or not perimeter or area <= 1 or perimeter <= 0:
        return None
    return (2.0 * math.log(perimeter / 4.0)) / math.log(area)


def elongation(width: float, height: float) -> float | None:
    """Allongement entre 0 et 1 : petit côté / grand côté du rectangle orienté minimal.

    1 pour un carré ou un disque, proche de 0 pour une bande étroite (haie, ripisylve).
    """
    if not width or not height or width <= 0 or height <= 0:
        return None
    return min(width, height) / max(width, height)


def circularity(area: float, perimeter: float) -> float | None:
    """Indice de circularité entre 0 et 1 : 1 pour un disque parfait."""
    if not area or not perimeter or perimeter <= 0:
        return None
    return (4.0 * math.pi * area) / (perimeter ** 2)


def shannon_index(areas_by_class: Mapping[str, float]) -> float | None:
    """Diversité de Shannon : 0 si une seule classe, croît avec la variété."""
    total = sum(max(float(value), 0.0) for value in areas_by_class.values())
    if total <= 0:
        return None
    index = 0.0
    for value in areas_by_class.values():
        proportion = max(float(value), 0.0) / total
        if proportion > 0:
            index -= proportion * math.log(proportion)
    return index


def shannon_evenness(areas_by_class: Mapping[str, float]) -> float | None:
    """Équitabilité de Piélou : diversité rapportée au maximum possible (0 à 1)."""
    classes = [value for value in areas_by_class.values() if float(value) > 0]
    if len(classes) < 2:
        return None
    index = shannon_index(areas_by_class)
    return None if index is None else index / math.log(len(classes))


def simpson_index(areas_by_class: Mapping[str, float]) -> float | None:
    """Diversité de Simpson : probabilité que deux points tirés diffèrent."""
    total = sum(max(float(value), 0.0) for value in areas_by_class.values())
    if total <= 0:
        return None
    return 1.0 - sum((max(float(v), 0.0) / total) ** 2 for v in areas_by_class.values())


def dominance(areas_by_class: Mapping[str, float]) -> float | None:
    """Dominance : écart à la diversité maximale, forte si une classe écrase."""
    classes = [value for value in areas_by_class.values() if float(value) > 0]
    if len(classes) < 2:
        return None
    index = shannon_index(areas_by_class)
    return None if index is None else math.log(len(classes)) - index


def largest_patch_index(areas: Sequence[float], total_area: float | None = None) -> float | None:
    """Part de la plus grande tache dans le paysage, en pourcentage."""
    values = [float(value) for value in areas if value and float(value) > 0]
    if not values:
        return None
    reference = float(total_area) if total_area else sum(values)
    if reference <= 0:
        return None
    return (max(values) / reference) * 100.0


def patch_density(count: int, total_area_m2: float) -> float | None:
    """Densité de taches, en nombre pour 100 hectares."""
    if not total_area_m2 or total_area_m2 <= 0:
        return None
    return count / (total_area_m2 / M2_PER_HA) * 100.0


def edge_density(total_edge_m: float, total_area_m2: float) -> float | None:
    """Densité de lisière en mètres par hectare : indicateur de fragmentation."""
    if not total_area_m2 or total_area_m2 <= 0:
        return None
    return total_edge_m / (total_area_m2 / M2_PER_HA)


def mean_patch_size(areas: Sequence[float]) -> float | None:
    """Taille moyenne des taches, en mètres carrés."""
    values = [float(value) for value in areas if value and float(value) > 0]
    return sum(values) / len(values) if values else None


def effective_mesh_size(areas: Sequence[float], total_area: float | None = None) -> float | None:
    """Maille effective : surface d'une tache « moyenne » perçue par une espèce.

    Indicateur de fragmentation retenu par les observatoires français. Plus le
    territoire est coupé par des routes ou de l'urbanisation, plus elle chute.
    """
    values = [float(value) for value in areas if value and float(value) > 0]
    if not values:
        return None
    reference = float(total_area) if total_area else sum(values)
    if reference <= 0:
        return None
    return sum(value ** 2 for value in values) / reference


def division_index(areas: Sequence[float], total_area: float | None = None) -> float | None:
    """Indice de division entre 0 et 1 : probabilité que deux points soient séparés."""
    values = [float(value) for value in areas if value and float(value) > 0]
    if not values:
        return None
    reference = float(total_area) if total_area else sum(values)
    if reference <= 0:
        return None
    return 1.0 - sum((value / reference) ** 2 for value in values)


def summarize_patches(patches: Sequence[Mapping],
                      landscape_perimeter: float | None = None) -> dict:
    """Bilan complet d'un ensemble de taches.

    Chaque tache est un dict ``{"class", "area", "perimeter"}``. Les surfaces
    sont attendues en mètres carrés et les périmètres en mètres.

    La somme des périmètres compte deux fois chaque lisière entre taches
    voisines. Avec `landscape_perimeter` (contour de l'union des taches), la
    lisière totale suit FRAGSTATS : lisières internes comptées une fois, bord
    du paysage exclu.
    """
    areas = [float(patch.get("area") or 0.0) for patch in patches]
    total_area = sum(areas)
    total_edge = sum(float(patch.get("perimeter") or 0.0) for patch in patches)
    if landscape_perimeter is not None:
        total_edge = max((total_edge - float(landscape_perimeter)) / 2.0, 0.0)
    by_class: dict[str, float] = {}
    count_by_class: dict[str, int] = {}
    for patch in patches:
        key = str(patch.get("class") or "(non classé)")
        by_class[key] = by_class.get(key, 0.0) + float(patch.get("area") or 0.0)
        count_by_class[key] = count_by_class.get(key, 0) + 1

    shapes = [
        value
        for value in (
            shape_index(float(p.get("area") or 0.0), float(p.get("perimeter") or 0.0))
            for p in patches
        )
        if value is not None
    ]
    return {
        "patch_count": len(patches),
        "class_count": len(by_class),
        "total_area_m2": total_area,
        "total_area_ha": total_area / M2_PER_HA,
        "total_edge_m": total_edge,
        "mean_patch_size_m2": mean_patch_size(areas),
        "largest_patch_index_percent": largest_patch_index(areas),
        "patch_density_per_100ha": patch_density(len(patches), total_area),
        "edge_density_m_per_ha": edge_density(total_edge, total_area),
        "mean_shape_index": sum(shapes) / len(shapes) if shapes else None,
        "shannon_index": shannon_index(by_class),
        "shannon_evenness": shannon_evenness(by_class),
        "simpson_index": simpson_index(by_class),
        "dominance": dominance(by_class),
        "division_index": division_index(areas),
        "effective_mesh_size_m2": effective_mesh_size(areas),
        "classes": [
            {
                "class": name,
                "area_m2": area,
                "area_ha": area / M2_PER_HA,
                "percent": (area / total_area * 100.0) if total_area else None,
                "patch_count": count_by_class[name],
            }
            for name, area in sorted(by_class.items(), key=lambda item: (-item[1], item[0]))
        ],
    }


def interpret_metrics(summary: Mapping) -> list[str]:
    """Phrases d'interprétation pour le rapport d'étude."""
    lines: list[str] = []
    evenness = summary.get("shannon_evenness")
    if evenness is not None:
        if evenness >= 0.8:
            lines.append("Paysage très équilibré : aucune occupation ne domine.")
        elif evenness >= 0.5:
            lines.append("Paysage modérément diversifié.")
        else:
            lines.append("Paysage dominé par une occupation du sol principale.")
    lpi = summary.get("largest_patch_index_percent")
    if lpi is not None and lpi >= 50:
        lines.append(f"Une seule tache occupe {lpi:.0f} % du territoire étudié.")
    density = summary.get("edge_density_m_per_ha")
    if density is not None:
        if density >= 300:
            lines.append("Densité de lisière élevée : paysage morcelé.")
        elif density <= 50:
            lines.append("Densité de lisière faible : grandes unités homogènes.")
    return lines
