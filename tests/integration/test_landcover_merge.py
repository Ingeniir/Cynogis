"""Fusion des objets OBIA (landcover_processing/merge.py) : NumPy seulement.

Valeurs attendues calculées à la main ; la fonction testée ne produit aucune valeur
attendue. Sans NumPy, la suite est ignorée.
"""
import random

import pytest

np = pytest.importorskip("numpy")

from cynogis.landcover_processing.merge import merge_segments  # noqa: E402
from cynogis.landcover_processing.persist_features import _schema  # noqa: E402

OBJECTS, EDGES = _schema()


def _tables(objects, edges):
    """objects : (id, pixels, (r, g, b)) ; edges : (a, b, côtés communs)."""
    table = np.zeros(len(objects), dtype=OBJECTS)
    for row, (segment, pixels, rgb) in zip(table, objects, strict=True):
        row["segment_id"], row["pixel_count"], row["rgb_mean"] = segment, pixels, rgb
    links = np.array([(a, b, sides, float(sides)) for a, b, sides in edges], dtype=EDGES)
    return table, links


def _merge(objects, edges, *, distance=0.0, area=0.0):
    table, links = _tables(objects, edges)
    return merge_segments(table, links, pixel_area_m2=1.0, color_distance_max=distance,
                          min_mapping_area_m2=area)


ROW = [(1, 10, (100, 100, 100)), (2, 10, (100, 100, 100)), (3, 10, (200, 0, 0))]
ROW_EDGES = [(1, 2, 3), (2, 3, 3)]


def test_similarite_seule():
    result = _merge(ROW, ROW_EDGES, distance=5)
    assert result.roots == [1, 1, 3]
    assert (result.merged_by_similarity, result.merged_by_area) == (1, 0)


def test_sans_fusion():
    assert _merge(ROW, ROW_EDGES).roots == [1, 2, 3]


def test_surface_minimale_en_cascade():
    # 1+2 = 20 px >= 15 ; 3 (10 px) rejoint ensuite son unique voisine.
    result = _merge(ROW, ROW_EDGES, area=15)
    assert result.roots == [1, 1, 1]
    assert (result.merged_by_area, result.isolated_small_units) == (2, 0)


def test_ilot_isole_conserve():
    result = _merge([(5, 3, (0, 0, 0))], [], area=10)
    assert result.roots == [5] and result.isolated_small_units == 1


def test_egalite_de_couleur_frontiere_la_plus_longue():
    objects = [(1, 100, (0, 0, 0)), (2, 1, (50, 50, 50)), (3, 100, (100, 100, 100))]
    result = _merge(objects, [(1, 2, 1), (2, 3, 3)], area=50)
    assert result.roots == [1, 2, 2]  # 2 rejoint 3 ; représentant = plus petit id


def test_moyenne_ponderee_apres_fusion():
    # 1 (90 px, 0) + 2 (10 px, 10) → moyenne pondérée 1 : 3 (à 20) reste à 19 > 16,
    # alors qu'une moyenne non pondérée (5) le placerait à 15 <= 16 et le fusionnerait.
    objects = [(1, 90, (0, 0, 0)), (2, 10, (10, 0, 0)), (3, 10, (20, 0, 0))]
    result = _merge(objects, [(1, 2, 1), (2, 3, 1)], distance=16)
    assert result.roots == [1, 1, 3]


def test_independance_de_l_ordre():
    rng = random.Random(20261124)
    objects = [(i, rng.randint(1, 40), tuple(rng.randint(0, 255) for _ in range(3)))
               for i in range(1, 60)]
    edges = sorted({(i, j, rng.randint(1, 5)) for i in range(1, 60) for j in range(i + 1, 60)
                    if rng.random() < 0.08})
    reference = dict(zip([o[0] for o in objects], _merge(objects, edges, distance=60,
                                                         area=30).roots, strict=True))
    shuffled = objects[:]
    rng.shuffle(shuffled)
    result = _merge(shuffled, edges, distance=60, area=30)
    assert dict(zip([o[0] for o in shuffled], result.roots, strict=True)) == reference


def test_arete_inconnue_refusee():
    with pytest.raises(ValueError, match="inconnu"):
        _merge(ROW, [(1, 9, 1)])
