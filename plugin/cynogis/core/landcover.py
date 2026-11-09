"""Configuration métier de la délimitation OBIA.

Ce module ne dépend ni de QGIS ni du moteur d'imagerie.

Les surfaces et les distances sont exprimées dans les unités terrain.
Le contrôle du SCR et de la résolution réelle appartient à la préparation
des données, pas à ce module.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass


def _validate_number(
        name: str,
        value: object,
        *,
        allow_zero: bool = False,
) -> None:
    """Refuse les valeurs non numériques, infinies ou hors domaine."""
    # bool hérite de int: le rejeter explicitement.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} doit être un nombre.")

    try:
        finite = math.isfinite(value)
    except OverflowError as exc:
        raise ValueError(f"{name} est trop grand.") from exc

    if not finite:
        raise ValueError(f"{name} doit être fini.")

    if allow_zero:
        if value < 0:
            raise ValueError(f"{name} doit être positif ou nul.")
    elif value <= 0:
        raise ValueError(f"{name} doit être strictement positif.")

@dataclass(frozen=True)
class LandcoverConfig:
    """Paramètres communs au pipeline OBIA.

    Les valeurs par défaut sont expérimentales.

    segment_min_area_m2 :
        seuil de taille utilisé pendant la segmentation intermédiaire.

    min_mapping_area_m2 :
        seuil proposé pour la généralisation finale. Ce n'est pas une
        interdiction de conserver de petits objets importants.

    simplification_m :
        paramètre de simplification en unités métriques. Sa signification
        exacte dépendra de l'algorithme retenu ; il ne constitue pas une
        garantie de déplacement maximal des frontières.

    preserve_linear_features :
        demande de protection des éléments étroits. Les règles concrètes
        seront implémentées dans le moteur de généralisation.
    """

    working_resolution_m: float = 0.5
    segment_min_area_m2: float = 5.0
    min_mapping_area_m2: float = 150.0
    simplification_m: float = 0.75
    preserve_linear_features: bool = True

    def __post_init__(self) -> None:
        for name in (
            "working_resolution_m",
            "segment_min_area_m2",
            "min_mapping_area_m2",
        ):
            _validate_number(name, getattr(self, name))

        _validate_number(
            "simplification_m",
            self.simplification_m,
            allow_zero=True,
        )

        if not isinstance(self.preserve_linear_features, bool):
            raise ValueError("preserve_linear_features doit être un booléen.")

        if self.segment_min_area_m2 > self.min_mapping_area_m2:
            raise ValueError(
                "segment_min_area_m2 ne doit pas dépasser "
                "min_mapping_area_m2."
            )

    def to_dict(self) -> dict:
        """Produit les paramètres sérialisables de la configuration."""
        return asdict(self)

def validate_rgb_bands(
        rgb_bands: list[int],
        band_count: int,
) -> tuple[int, int, int]:
    """Valide les indices des bandes dans l'ordre rouge, vert, bleu.

    Cette fonction vérifie uniquement les indices.
    Elle ne prouve pas que ces bandes correspondent réellement au RGB.
    """
    if (
        isinstance(band_count, bool)
        or not isinstance(band_count, int)
        or band_count < 1
    ):
        raise ValueError("band_count doit être un entier strictement positif.")

    if not isinstance(rgb_bands, list) or len(rgb_bands) != 3:
        raise ValueError("rgb_bands doit contenir exactement trois indices.")

    if any(
        isinstance(band, bool) or not isinstance(band, int)
        for band in rgb_bands
    ):
        raise ValueError("Les indices de rgb_bands doivent être des entiers.")

    if len(set(rgb_bands)) != 3:
        raise ValueError("Les trois indices de rgb_bands doivent être distincts.")

    if any(band < 1 or band > band_count for band in rgb_bands):
        raise ValueError(
            f"Les indices de rgb_bands doivent être compris entre 1 et {band_count}."
        )

    return rgb_bands[0], rgb_bands[1], rgb_bands[2]

@dataclass(frozen=True)
class PreparationConfig:
    """Configuration de la préparation native des entrées OBIA.

    La politique de validité est obligatoire.
    Cette première version ne permet pas d'ignorer les masques source.
    """

    validity_policy: str
    max_pixels: int = 1_000_000

    def __post_init__(self) -> None:
        if self.validity_policy != "respect_source_masks":
            raise ValueError(
                "validity_policy doit être 'respect_source_masks'. "
                "Les autres politiques ne sont pas encore implémentées."
            )

        if (
            isinstance(self.max_pixels, bool)
            or not isinstance(self.max_pixels, int)
            or self.max_pixels <= 0
        ):
            raise ValueError("max_pixels doit être un entier strictement positif.")

    def to_dict(self) -> dict:
        return asdict(self)
