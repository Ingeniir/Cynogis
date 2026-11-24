"""Caractéristiques RGB et voisinages OBIA en mémoire.

Fichier cible : plugin/cynogis/landcover_processing/object_features.py

Nouveau module autonome, sans QGIS, GDAL, SciPy, scikit-image, fichiers,
classification, fusion ni modification des labels. NumPy est importé uniquement
lors de l'appel de la fonction. Ne pas ajouter d'import dans __init__.py.

Contrat
-------
RGB : ndarray uint8 (H, W, 3), ordre des bandes déclaré par l'appelant.
Labels : ndarray uint32 (H, W), 0 hors masque et > 0 dans le masque.
Masque : ndarray bool (H, W), non vide. Maximum : 1 000 000 pixels entiers.
Résolution : côté du pixel carré en mètres, nombre fini et strictement positif de
type Python exact int ou float ; bool, scalaires NumPy (dont np.float64) et autres
sous-classes sont refusés.

Les identifiants discontinus sont conservés. Une ligne regroupe TOUS les pixels
portant le même identifiant. La connexité n'est PAS vérifiée ici : l'appelant doit
fournir des segments connexes s'il veut interpréter chaque ligne comme un objet
connexe. Les composantes disjointes d'un même label ne sont pas renumérotées.

Résultat : ObjectFeatures avec deux tableaux structurés indépendants des entrées.
- objects : tri par segment_id ; centre en coordonnées de grille depuis le coin
  supérieur gauche (centre du premier pixel = row 0.5, col 0.5) ; emprise à maxima
  exclusifs ; RGB en unités 0..255 ; écart-type de population (ddof=0).
- edges : tri lexicographique (segment_a, segment_b), a < b ; chaque côté partagé
  entre deux labels positifs distincts compte une seule fois. Les diagonales,
  le bord externe du raster et les limites vers le fond ne sont pas des arêtes.

Aucune coordonnée géographique, aucun périmètre complet ni indice spectral.
Aucun contrôle d'annulation ni snapshot contre une mutation concurrente.
Les entrées ne sont jamais écrites. Les tableaux retournés restent modifiables ;
la dataclass figée protège uniquement l'affectation de ses attributs.

Complexité : agrégations sur indices compacts, sans boucle raster par objet ni
allocation indexée par le plus grand label. Les tris de np.unique impliquent un
coût pouvant atteindre O(N log N) ; mémoire O(N + K + E). K objets, E arêtes.
La limite en pixels n'est pas une garantie de budget mémoire pour toute machine.

Tests exécutables
-----------------
Depuis la racine du dépôt, avec le Python QGIS contenant NumPy :
    python-qgis.bat plugin/cynogis/landcover_processing/object_features.py

Ces tests utilisent la bibliothèque standard doctest. Aucun pytest nécessaire.
Ils ne remplacent pas la future suite d'intégration du dépôt.

>>> import numpy as np
>>> labels = np.array([[2, 2], [9, 9]], dtype=np.uint32)
>>> rgb = np.array([[[0, 10, 20], [2, 12, 22]],
...                 [[10, 20, 30], [14, 24, 34]]], dtype=np.uint8)
>>> mask = np.ones((2, 2), dtype=bool)
>>> result = extract_object_features(rgb, labels, mask, pixel_size_m=0.5)
>>> result.objects['segment_id'].tolist()
[2, 9]
>>> result.objects['pixel_count'].tolist()
[2, 2]
>>> result.objects['area_m2'].tolist()
[0.5, 0.5]
>>> result.objects['center_row'].tolist(), result.objects['center_col'].tolist()
([0.5, 1.5], [1.0, 1.0])
>>> result.objects[['row_min', 'row_max_exclusive', 'col_min', 'col_max_exclusive']].tolist()
[(0, 1, 0, 2), (1, 2, 0, 2)]
>>> result.objects['rgb_mean'].tolist()
[[1.0, 11.0, 21.0], [12.0, 22.0, 32.0]]
>>> result.objects['rgb_std'].tolist()
[[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]
>>> result.edges.tolist()
[(2, 9, 2, 1.0)]

Identifiants espacés, zéro ignoré, contact diagonal non compté :
>>> sparse = np.array([[1, 0], [0, 4294967295]], dtype=np.uint32)
>>> diagonal = extract_object_features(rgb, sparse, sparse > 0, pixel_size_m=1)
>>> diagonal.objects['segment_id'].tolist()
[1, 4294967295]
>>> diagonal.edges.size
0
>>> diagonal.objects['rgb_std'].tolist()
[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

Frontières dans les deux directions, chaque côté une fois :
>>> checker = np.array([[1, 2], [2, 1]], dtype=np.uint32)
>>> edges = extract_object_features(rgb, checker, mask, pixel_size_m=0.5).edges
>>> edges.tolist()
[(1, 2, 4, 2.0)]

Trou central, huit pixels d'un seul objet :
>>> ring = np.ones((3, 3), dtype=np.uint32)
>>> ring[1, 1] = 0
>>> ring_rgb = np.full((3, 3, 3), 255, dtype=np.uint8)
>>> hole = extract_object_features(ring_rgb, ring, ring > 0, pixel_size_m=2)
>>> hole.objects['pixel_count'].tolist(), hole.objects['area_m2'].tolist()
([8], [32.0])
>>> hole.objects['center_row'].tolist(), hole.edges.size
([1.5], 0)
>>> hole.objects['rgb_std'].tolist()
[[0.0, 0.0, 0.0]]

Vues non contiguës en lecture seule, aucune mutation :
>>> original = rgb.copy()
>>> rgb_view, labels_view, mask_view = rgb[:, ::-1], labels[:, ::-1], mask[:, ::-1]
>>> rgb_view.flags.writeable = False
>>> labels_view.flags.writeable = False
>>> mask_view.flags.writeable = False
>>> view_result = extract_object_features(rgb_view, labels_view, mask_view, pixel_size_m=0.5)
>>> np.array_equal(rgb, original)
True
>>> np.array_equal(view_result.objects['rgb_mean'], result.objects['rgb_mean'])
True
>>> np.shares_memory(result.objects, rgb), np.shares_memory(result.edges, labels)
(False, False)

Refus d'entrées avant tout résultat :
>>> extract_object_features(rgb, labels, mask, pixel_size_m=True)
Traceback (most recent call last):
...
ValueError: pixel_size_m doit être un nombre Python fini et strictement positif.
>>> extract_object_features(rgb, labels, mask, pixel_size_m=np.float64(0.5))
Traceback (most recent call last):
...
ValueError: pixel_size_m doit être un nombre Python fini et strictement positif.
>>> extract_object_features(rgb, labels, mask.astype(np.uint8), pixel_size_m=1)
Traceback (most recent call last):
...
ValueError: analysis_mask doit être un tableau booléen de la même grille.
>>> extract_object_features(rgb, labels, np.zeros((2, 2), dtype=bool), pixel_size_m=1)
Traceback (most recent call last):
...
ValueError: Le masque d'analyse est vide.
>>> extract_object_features(rgb, np.zeros((2, 2), dtype=np.uint32), mask, pixel_size_m=1)
Traceback (most recent call last):
...
ValueError: Les labels doivent être positifs dans le masque et nuls à l'extérieur.
>>> extract_object_features(rgb, labels.astype(np.int64), mask, pixel_size_m=1)
Traceback (most recent call last):
...
ValueError: labels doit être un tableau uint32 de la même grille.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

MAX_PIXELS = 1_000_000


@dataclass(frozen=True)
class ObjectFeatures:
    """Deux tables NumPy structurées ; aucun fichier ni objet QGIS."""

    objects: np.ndarray
    edges: np.ndarray


def _pixel_area(pixel_size_m: object) -> tuple[float, float]:
    message = "pixel_size_m doit être un nombre Python fini et strictement positif."
    # Types exacts : bool, scalaires NumPy (np.float64 hérite de float) et autres
    # sous-classes sont refusés.
    if type(pixel_size_m) not in (int, float):
        raise ValueError(message)
    try:
        resolution = float(pixel_size_m)
    except (OverflowError, ValueError) as exc:
        raise ValueError(message) from exc
    if not math.isfinite(resolution) or resolution <= 0:
        raise ValueError(message)
    area = resolution * resolution
    if not math.isfinite(area) or area <= 0:
        raise ValueError("La surface d'un pixel est hors limites.")
    return resolution, area


def _adjacency(labels: np.ndarray, resolution: float) -> np.ndarray:
    """Compte droite et bas seulement, sans indexation par le label maximal."""
    import numpy as np

    dtype = np.dtype([
        ("segment_a", np.uint32),
        ("segment_b", np.uint32),
        ("shared_pixel_sides", np.int64),
        ("shared_boundary_m", np.float64),
    ])
    pairs = []
    for left, right in (
        (labels[:, :-1], labels[:, 1:]),
        (labels[:-1, :], labels[1:, :]),
    ):
        contact = (left > 0) & (right > 0) & (left != right)
        if np.any(contact):
            first, second = left[contact], right[contact]
            pairs.append(np.column_stack((
                np.minimum(first, second), np.maximum(first, second),
            )))

    if not pairs:
        return np.empty(0, dtype=dtype)

    unique_pairs, counts = np.unique(
        np.concatenate(pairs, axis=0), axis=0, return_counts=True,
    )
    lengths = counts.astype(np.float64) * resolution
    if not np.all(np.isfinite(lengths)):
        raise ValueError("Une longueur de frontière est hors limites.")
    edges = np.empty(len(counts), dtype=dtype)
    edges["segment_a"] = unique_pairs[:, 0]
    edges["segment_b"] = unique_pairs[:, 1]
    edges["shared_pixel_sides"] = counts
    edges["shared_boundary_m"] = lengths
    return edges


def extract_object_features(
    rgb: np.ndarray,
    labels: np.ndarray,
    analysis_mask: np.ndarray,
    *,
    pixel_size_m: float,
) -> ObjectFeatures:
    """Décrit les labels et leur adjacence, sans les modifier ni les classer.

    ValueError pour une entrée incompatible ; ImportError non masquée si NumPy
    manque. La connexité de chaque label est un prérequis non revérifié ici.
    Les identifiants peuvent atteindre uint32.max sans allocation correspondante.
    La géométrie métrique suppose des pixels carrés et une résolution en mètres.
    """
    import numpy as np

    resolution, pixel_area = _pixel_area(pixel_size_m)
    if not isinstance(rgb, np.ndarray) or rgb.dtype != np.dtype("uint8"):
        raise ValueError("rgb doit être un tableau NumPy uint8.")
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("rgb doit avoir la forme (hauteur, largeur, 3).")
    height, width = rgb.shape[:2]
    if height == 0 or width == 0 or height * width > MAX_PIXELS:
        raise ValueError("La grille doit contenir entre 1 et 1 000 000 pixels.")
    shape = (height, width)
    if (
        not isinstance(labels, np.ndarray)
        or labels.dtype != np.dtype("uint32")
        or labels.shape != shape
    ):
        raise ValueError("labels doit être un tableau uint32 de la même grille.")
    if (
        not isinstance(analysis_mask, np.ndarray)
        or analysis_mask.dtype != np.dtype("bool")
        or analysis_mask.shape != shape
    ):
        raise ValueError("analysis_mask doit être un tableau booléen de la même grille.")
    valid_pixels = int(np.count_nonzero(analysis_mask))
    if valid_pixels == 0:
        raise ValueError("Le masque d'analyse est vide.")
    if not np.array_equal(labels > 0, analysis_mask):
        raise ValueError(
            "Les labels doivent être positifs dans le masque et nuls à l'extérieur."
        )
    if not math.isfinite(valid_pixels * pixel_area):
        raise ValueError("La surface totale d'analyse est hors limites.")

    ids, inverse, counts = np.unique(
        labels[analysis_mask], return_inverse=True, return_counts=True,
    )
    inverse = inverse.reshape(-1)
    count = len(ids)
    counts_float = counts.astype(np.float64)
    rows, cols = np.nonzero(analysis_mask)

    dtype = np.dtype([
        ("segment_id", np.uint32),
        ("pixel_count", np.int64),
        ("area_m2", np.float64),
        ("center_row", np.float64),
        ("center_col", np.float64),
        ("row_min", np.int64),
        ("row_max_exclusive", np.int64),
        ("col_min", np.int64),
        ("col_max_exclusive", np.int64),
        ("rgb_mean", np.float64, (3,)),
        ("rgb_std", np.float64, (3,)),
    ])
    objects = np.empty(count, dtype=dtype)
    objects["segment_id"] = ids
    objects["pixel_count"] = counts
    objects["area_m2"] = counts_float * pixel_area
    objects["center_row"] = (
        np.bincount(inverse, weights=rows, minlength=count) / counts_float + 0.5
    )
    objects["center_col"] = (
        np.bincount(inverse, weights=cols, minlength=count) / counts_float + 0.5
    )

    for coordinates, lower, upper, limit in (
        (rows, "row_min", "row_max_exclusive", height),
        (cols, "col_min", "col_max_exclusive", width),
    ):
        minimum = np.full(count, limit, dtype=np.int64)
        maximum = np.full(count, -1, dtype=np.int64)
        np.minimum.at(minimum, inverse, coordinates)
        np.maximum.at(maximum, inverse, coordinates)
        objects[lower] = minimum
        objects[upper] = maximum + 1

    # Deux passages par bande : variance centrée, sans soustraction E[X²]-E[X]².
    # Aucune boucle sur les objets et aucun accès aux couleurs hors masque.
    for channel in range(3):
        values = rgb[:, :, channel][analysis_mask].astype(np.float64)
        means = np.bincount(inverse, weights=values, minlength=count) / counts_float
        differences = values - means[inverse]
        variance = np.bincount(
            inverse, weights=differences * differences, minlength=count,
        ) / counts_float
        objects["rgb_mean"][:, channel] = means
        objects["rgb_std"][:, channel] = np.sqrt(variance)

    edges = _adjacency(labels, resolution)
    return ObjectFeatures(objects=objects, edges=edges)


if __name__ == "__main__":
    import doctest

    report = doctest.testmod(optionflags=doctest.ELLIPSIS)
    print(f"doctest : {report.attempted} exemples, {report.failed} échecs")
    raise SystemExit(1 if report.failed else 0)
