"""Segmentation OBIA en mémoire, sans QGIS, GDAL, fichiers ni classification.

Ne pas importer ce module dans le __init__.py du paquet pour le moment.

Entrées : RGB uint8 (hauteur, largeur, 3), masque booléen (hauteur, largeur).
Sortie : tableau uint32, 0 hors masque, identifiants positifs dans le masque.
Chaque identifiant désigne une composante connexe à quatre voisins.

Prototype limité à 1 000 000 pixels et 10 000 graines demandées.
La surface cible n'est PAS une surface minimale garantie.
Aucun lissage, fusion cartographique ou classement sémantique ici.
Aucune annulation en cours d'appel SLIC n'est implémentée dans ce module.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

MAX_PIXELS = 1_000_000
MAX_REQUESTED_SEGMENTS = 10_000


def _positive_float(value: object, name: str) -> float:
    """Accepte uniquement les nombres Python finis, strictement positifs."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} doit être un nombre strictement positif.")
    try:
        converted = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} est hors limites.") from exc
    if not math.isfinite(converted) or converted <= 0:
        raise ValueError(f"{name} doit être fini et strictement positif.")
    return converted


@dataclass(frozen=True)
class SlicConfig:
    """Paramètres du prototype, indépendants de la généralisation finale.

    Les valeurs par défaut sont des points de départ expérimentaux,
    pas des réglages validés pour les paysages de La Réunion.
    """

    target_segment_area_m2: float = 25.0
    compactness: float = 10.0
    max_num_iter: int = 10

    def __post_init__(self) -> None:
        for name in ("target_segment_area_m2", "compactness"):
            object.__setattr__(self, name, _positive_float(getattr(self, name), name))
        if (
            isinstance(self.max_num_iter, bool)
            or not isinstance(self.max_num_iter, int)
            or not 1 <= self.max_num_iter <= 100
        ):
            raise ValueError("max_num_iter doit être un entier entre 1 et 100.")


def segment_rgb(
    rgb: np.ndarray,
    analysis_mask: np.ndarray,
    *,
    pixel_size_m: float,
    config: SlicConfig | None = None,
) -> np.ndarray:
    """Produit des objets connexes sur une grille à pixels carrés.

    pixel_size_m est la longueur du côté d'un pixel, en mètres.
    Ce noyau ne connaît pas le SCR : l'appelant est responsable de cette valeur.

    Les tableaux d'entrée ne sont pas modifiés. Le masque doit être booléen :
    les futurs lecteurs de raster devront valider les valeurs 0/1 avant
    conversion, plutôt que convertir silencieusement des valeurs quelconques.

    ValueError : entrée ou paramètre refusé.
    RuntimeError : résultat du moteur incompatible avec le contrat.
    ImportError : dépendance manquante ou impossible à charger, non dissimulée.

    Cas particuliers : masque vide refusé ; un seul pixel accepté ; une seule
    graine demandée produit une région par composante du masque, sans SLIC.
    Le nombre final d'objets peut différer du nombre de graines demandé.
    """
    # Imports tardifs : le chargement du module n'importe pas scikit-image.
    import numpy as np

    if config is None:
        config = SlicConfig()
    if not isinstance(config, SlicConfig):
        raise ValueError("config doit être une SlicConfig.")

    resolution = _positive_float(pixel_size_m, "pixel_size_m")
    pixel_area = resolution * resolution
    if not math.isfinite(pixel_area) or pixel_area <= 0:
        raise ValueError("La surface du pixel est hors limites.")

    if not isinstance(rgb, np.ndarray) or rgb.dtype != np.dtype("uint8"):
        raise ValueError("rgb doit être un tableau NumPy uint8.")
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("rgb doit avoir la forme (hauteur, largeur, 3).")
    height, width = rgb.shape[:2]
    if height == 0 or width == 0 or height * width > MAX_PIXELS:
        raise ValueError("La grille doit contenir entre 1 et 1 000 000 pixels.")

    if not isinstance(analysis_mask, np.ndarray):
        raise ValueError("analysis_mask doit être un tableau NumPy.")
    if analysis_mask.dtype != np.dtype("bool"):
        raise ValueError("analysis_mask doit être booléen.")
    if analysis_mask.shape != (height, width):
        raise ValueError("Le masque et l'image doivent partager la même grille.")

    valid_pixels = int(np.count_nonzero(analysis_mask))
    if valid_pixels == 0:
        raise ValueError("Le masque d'analyse est vide.")

    analysis_area = valid_pixels * pixel_area
    if not math.isfinite(analysis_area):
        raise ValueError("La surface d'analyse est hors limites.")
    estimate = analysis_area / config.target_segment_area_m2
    if not math.isfinite(estimate):
        raise ValueError("Le nombre théorique de segments est hors limites.")
    requested = max(1, min(valid_pixels, math.ceil(estimate)))
    if requested > MAX_REQUESTED_SEGMENTS:
        raise ValueError(
            "Plus de 10 000 graines demandées : augmenter la surface cible."
        )

    from skimage.measure import label

    # Copies propres : aucun accès en écriture aux données de l'appelant.
    mask = np.array(analysis_mask, dtype=bool, order="C", copy=True)

    if requested == 1:
        raw = mask.astype(np.int32)
    else:
        from skimage.segmentation import slic

        image = rgb.astype(np.float32, copy=True) / np.float32(255.0)
        # Sans lissage, les valeurs extérieures ne doivent pas apporter
        # de données radiométriques utiles au calcul masqué.
        image[~mask] = 0.0
        raw = slic(
            image,
            n_segments=requested,
            compactness=config.compactness,
            max_num_iter=config.max_num_iter,
            sigma=0,
            convert2lab=True,
            enforce_connectivity=True,
            min_size_factor=0.5,
            max_size_factor=3.0,
            slic_zero=False,
            start_label=1,
            mask=mask,
            channel_axis=-1,
        )

    if raw.shape != mask.shape or not np.issubdtype(raw.dtype, np.integer):
        raise RuntimeError("Le moteur a renvoyé une grille d'étiquettes invalide.")
    if np.any(raw[mask] <= 0):
        raise RuntimeError("Le moteur a laissé des pixels analysables sans segment.")

    # Neutraliser explicitement l'extérieur, puis séparer les composantes
    # d'une même étiquette. label compare les valeurs : ne PAS lui passer
    # raw > 0, ce qui ferait disparaître les frontières entre segments.
    raw = np.array(raw, copy=True)
    raw[~mask] = 0
    connected = label(raw, background=0, connectivity=1)
    output = connected.astype(np.uint32, copy=False)

    if np.any(output[~mask] != 0) or np.any(output[mask] == 0):
        raise RuntimeError("La segmentation finale ne respecte pas le masque.")
    return output
