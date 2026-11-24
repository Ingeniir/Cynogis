"""Noyau de segmentation OBIA (landcover_processing/segment.py), en mémoire.

Nécessite NumPy, SciPy et scikit-image (obia-requirements.txt), pas QGIS. Sous pytest
sans ces dépendances (venv du dépôt), la suite est ignorée explicitement. Le Python de
QGIS n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" \
        tests/integration/test_landcover_segment.py

Deux familles d'essais, distinguées par leur préfixe :
- test_real_* : vraie fonction slic de scikit-image (éventuellement espionnée : l'espion
  appelle la vraie fonction et ne fait que compter les appels) ;
- test_double_* : slic remplacée par un double ciblé qui renvoie des étiquettes choisies,
  pour exercer les contrôles du contrat que le vrai moteur ne déclenche pas.
- test_config_*, test_invalid_* : validations levées avant toute segmentation.

Ces essais synthétiques vérifient le contrat technique (masque, connexité, types,
entrées intactes). Ils ne valident pas la qualité du découpage des paysages et
n'imposent ni nombre exact de segments ni surface minimale.
"""
from __future__ import annotations

import contextlib
import re
import sys
import traceback
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plugin"))
else:
    import pytest

    pytest.importorskip("numpy", reason="NumPy absent : suite de segmentation ignorée")
    pytest.importorskip("scipy.ndimage", reason="SciPy absent : suite de segmentation ignorée")
    pytest.importorskip("skimage", reason="scikit-image absent : suite de segmentation ignorée")

import numpy as np
import skimage.segmentation
from scipy import ndimage

from cynogis.landcover_processing import segment
from cynogis.landcover_processing.segment import (
    MAX_PIXELS,
    MAX_REQUESTED_SEGMENTS,
    SlicConfig,
    segment_rgb,
)

FOUR_NEIGHBOURS = ndimage.generate_binary_structure(2, 1)
RNG_SEED = 20261115


# --- Outils --------------------------------------------------------------------------------
@contextlib.contextmanager
def raises(exc_type, match: str):
    """Équivalent minimal de pytest.raises, utilisable sans pytest."""
    try:
        yield
    except exc_type as exc:
        assert re.search(match, str(exc)), f"message inattendu : {exc}"
    else:
        raise AssertionError(f"{exc_type.__name__} attendue ({match})")


@contextlib.contextmanager
def slic_replaced(replacement):
    """segment_rgb importe slic à l'appel : remplacer l'attribut du module suffit."""
    original = skimage.segmentation.slic
    skimage.segmentation.slic = replacement
    try:
        yield
    finally:
        skimage.segmentation.slic = original


class SlicSpy:
    """Espion : appelle la vraie fonction slic et compte les appels."""

    def __init__(self):
        self.calls = []
        self.real = skimage.segmentation.slic

    def __call__(self, image, **kwargs):
        self.calls.append(kwargs)
        return self.real(image, **kwargs)


def forbidden_slic(*_args, **_kwargs):
    raise AssertionError("slic ne doit pas être appelée")


def rng():
    return np.random.default_rng(RNG_SEED)


def random_rgb(height, width):
    return rng().integers(0, 256, (height, width, 3), dtype=np.uint8)


def irregular_mask_with_hole(height=40, width=40):
    """Masque en L avec un trou intérieur."""
    mask = np.zeros((height, width), bool)
    mask[2:38, 2:18] = True
    mask[24:38, 2:38] = True
    mask[8:14, 7:13] = False                 # trou
    hole = np.zeros_like(mask)
    hole[8:14, 7:13] = True
    return mask, hole


def assert_contract(output, mask):
    """Contrat de sortie, vérifié indépendamment du module."""
    assert output.dtype == np.uint32
    assert output.shape == mask.shape
    assert not np.any(output[~mask]), "valeur non nulle hors masque"
    assert np.all(output[mask] > 0), "pixel du masque sans segment"
    for identifier in np.unique(output[mask]):
        _, count = ndimage.label(output == identifier, structure=FOUR_NEIGHBOURS)
        assert count == 1, f"l'identifiant {identifier} couvre {count} composantes"


# --- Configuration -------------------------------------------------------------------------
def test_config_defaults_are_normalised_floats():
    config = SlicConfig()
    assert config == SlicConfig(100.0, 10.0, 10, 2.0)
    assert isinstance(SlicConfig(target_segment_area_m2=4).target_segment_area_m2, float)


def test_config_rejects_invalid_numbers():
    for field in ("target_segment_area_m2", "compactness"):
        for value in (True, False, 0, 0.0, -1, -0.5, float("nan"), float("inf"),
                      float("-inf"), "1", None):
            with raises(ValueError, field):
                SlicConfig(**{field: value})
        with raises(ValueError, "hors limites"):         # entier trop grand pour un float
            SlicConfig(**{field: 10**400})


def test_config_rejects_iterations_out_of_range():
    for value in (0, -1, 101, True, 1.0, 10.5, "10", None):
        with raises(ValueError, "max_num_iter"):
            SlicConfig(max_num_iter=value)
    assert SlicConfig(max_num_iter=1).max_num_iter == 1
    assert SlicConfig(max_num_iter=100).max_num_iter == 100


# --- Entrées refusées ----------------------------------------------------------------------
def test_invalid_config_and_pixel_size():
    rgb, mask = random_rgb(4, 4), np.ones((4, 4), bool)
    with raises(ValueError, "SlicConfig"):
        segment_rgb(rgb, mask, pixel_size_m=1.0, config={"compactness": 10})
    for value in (True, 0, -1.0, float("nan"), float("inf"), "0.5", None):
        with raises(ValueError, "pixel_size_m"):
            segment_rgb(rgb, mask, pixel_size_m=value)
    with raises(ValueError, "hors limites"):              # côté fini, surface infinie
        segment_rgb(rgb, mask, pixel_size_m=1e200)


def test_invalid_rgb_type_and_shape():
    mask = np.ones((4, 4), bool)
    for bad in (random_rgb(4, 4).astype(np.uint16), random_rgb(4, 4).astype(np.float32),
                random_rgb(4, 4).astype(np.int8), random_rgb(4, 4).tolist()):
        with raises(ValueError, "uint8"):
            segment_rgb(bad, mask, pixel_size_m=1.0)
    for bad in (np.zeros((4, 4), np.uint8), np.zeros((4, 4, 4), np.uint8),
                np.zeros((4, 4, 3, 1), np.uint8)):
        with raises(ValueError, "forme"):
            segment_rgb(bad, mask, pixel_size_m=1.0)
    for bad in (np.zeros((0, 4, 3), np.uint8), np.zeros((4, 0, 3), np.uint8)):
        with raises(ValueError, "entre 1 et 1 000 000"):
            segment_rgb(bad, np.ones(bad.shape[:2], bool), pixel_size_m=1.0)


def test_invalid_mask_type_and_grid():
    rgb = random_rgb(4, 4)
    with raises(ValueError, "tableau NumPy"):
        segment_rgb(rgb, [[True] * 4] * 4, pixel_size_m=1.0)
    for bad in (np.ones((4, 4), np.uint8), np.ones((4, 4), np.int64), np.ones((4, 4), float)):
        with raises(ValueError, "booléen"):
            segment_rgb(rgb, bad, pixel_size_m=1.0)
    for bad in (np.ones((4, 5), bool), np.ones((5, 4), bool), np.ones((4, 4, 1), bool)):
        with raises(ValueError, "même grille"):
            segment_rgb(rgb, bad, pixel_size_m=1.0)


def test_invalid_empty_mask():
    with raises(ValueError, "vide"):
        segment_rgb(random_rgb(5, 5), np.zeros((5, 5), bool), pixel_size_m=1.0)


def test_invalid_pixel_limit_before_slic():
    rgb = np.zeros((1001, 1000, 3), np.uint8)
    assert rgb.shape[0] * rgb.shape[1] > MAX_PIXELS
    with slic_replaced(forbidden_slic), raises(ValueError, "1 000 000"):
        segment_rgb(rgb, np.ones(rgb.shape[:2], bool), pixel_size_m=1.0)


def test_invalid_seed_limit_before_slic():
    rgb, mask = np.zeros((110, 100, 3), np.uint8), np.ones((110, 100), bool)
    config = SlicConfig(target_segment_area_m2=1.0)       # 11 000 graines demandées
    assert mask.sum() > MAX_REQUESTED_SEGMENTS
    with slic_replaced(forbidden_slic), raises(ValueError, "10 000 graines"):
        segment_rgb(rgb, mask, pixel_size_m=1.0, config=config)
    # Exactement à la limite : accepté, et SLIC est bien appelée.
    spy = SlicSpy()
    exact = np.zeros((110, 100), bool)
    exact.flat[:MAX_REQUESTED_SEGMENTS] = True
    with slic_replaced(spy):
        output = segment_rgb(rgb, exact, pixel_size_m=1.0, config=config)
    assert len(spy.calls) == 1 and spy.calls[0]["n_segments"] == MAX_REQUESTED_SEGMENTS
    assert_contract(output, exact)


# --- Moteur réel ---------------------------------------------------------------------------
def test_real_single_pixel_accepted_without_slic():
    with slic_replaced(forbidden_slic):
        output = segment_rgb(random_rgb(1, 1), np.ones((1, 1), bool), pixel_size_m=0.5)
    assert output.tolist() == [[1]] and output.dtype == np.uint32


def test_real_one_seed_branch_labels_mask_components():
    """requested == 1 : une région par composante à quatre voisins, sans SLIC."""
    mask = np.zeros((8, 8), bool)
    mask[0:3, 0:3] = True                    # îlot A
    mask[5:8, 5:8] = True                    # îlot B
    mask[3, 3] = True                        # contact uniquement diagonal avec A
    with slic_replaced(forbidden_slic):
        output = segment_rgb(random_rgb(8, 8), mask, pixel_size_m=1.0,
                             config=SlicConfig(target_segment_area_m2=1e6))
    assert_contract(output, mask)
    assert len(np.unique(output[mask])) == 3
    assert output[3, 3] != output[2, 2]      # la diagonale ne relie pas


def test_real_slic_branch_is_called_with_mask():
    mask, hole = irregular_mask_with_hole()
    spy = SlicSpy()
    with slic_replaced(spy):
        output = segment_rgb(random_rgb(40, 40), mask, pixel_size_m=0.5)
    assert len(spy.calls) == 1
    call = spy.calls[0]
    assert call["n_segments"] > 1
    assert np.array_equal(call["mask"], mask)
    assert call["sigma"] == 0 and call["enforce_connectivity"] is True
    assert_contract(output, mask)
    assert not np.any(output[hole])


def test_real_full_mask_uniform_image():
    rgb, mask = np.full((30, 30, 3), 128, np.uint8), np.ones((30, 30), bool)
    spy = SlicSpy()
    with slic_replaced(spy):
        output = segment_rgb(rgb, mask, pixel_size_m=1.0)
    assert len(spy.calls) == 1
    assert_contract(output, mask)


def test_real_separate_islands_and_diagonal_contact_in_slic_branch():
    mask = np.zeros((30, 30), bool)
    mask[1:12, 1:12] = True
    mask[18:29, 18:29] = True
    mask[12, 12] = True                      # touche le premier îlot par un coin
    output = segment_rgb(random_rgb(30, 30), mask, pixel_size_m=1.0,
                         config=SlicConfig(target_segment_area_m2=16.0))
    assert_contract(output, mask)
    first = set(np.unique(output[1:12, 1:12]).tolist())
    second = set(np.unique(output[18:29, 18:29]).tolist())
    assert first.isdisjoint(second)
    assert output[12, 12] not in first       # pixel diagonal isolé : objet propre


def test_real_inputs_unchanged_non_contiguous_and_read_only():
    mask_full, _ = irregular_mask_with_hole(80, 80)
    rgb_full = random_rgb(80, 80)
    rgb = rgb_full[::2, ::2]                 # vues non contiguës
    mask = mask_full[::2, ::2]
    assert not rgb.flags.c_contiguous and not mask.flags.c_contiguous
    rgb.flags.writeable = False
    mask.flags.writeable = False
    rgb_before, mask_before = rgb.copy(), mask.copy()
    output = segment_rgb(rgb, mask, pixel_size_m=0.5)
    assert np.array_equal(rgb, rgb_before) and np.array_equal(mask, mask_before)
    assert np.array_equal(rgb_full[::2, ::2], rgb_before)
    assert_contract(output, mask)


def test_real_rgb_outside_mask_does_not_change_result():
    mask, _ = irregular_mask_with_hole()
    rgb = random_rgb(40, 40)
    other = rgb.copy()
    other[~mask] = np.random.default_rng(1).integers(0, 256, (int((~mask).sum()), 3),
                                                     dtype=np.uint8)
    assert not np.array_equal(rgb, other)
    first = segment_rgb(rgb, mask, pixel_size_m=0.5)
    second = segment_rgb(other, mask, pixel_size_m=0.5)
    assert np.array_equal(first, second)


def test_real_module_import_does_not_load_slic():
    """Le module ne référence ni slic ni label à son chargement."""
    assert not hasattr(segment, "slic") and not hasattr(segment, "label")


# --- Double ciblé de slic ------------------------------------------------------------------
def test_double_disjoint_pieces_of_one_label_are_separated():
    mask = np.ones((6, 6), bool)
    labels = np.full((6, 6), 2, np.int64)
    labels[:, 2:4] = 7                       # bande centrale : coupe l'étiquette 2 en deux
    labels[0, 0] = 9
    labels[1, 1] = 9                         # même étiquette, contact diagonal seulement
    with slic_replaced(lambda image, **kwargs: labels.copy()):
        output = segment_rgb(random_rgb(6, 6), mask, pixel_size_m=1.0,
                             config=SlicConfig(target_segment_area_m2=4.0))
    assert_contract(output, mask)
    assert output[0, 0] != output[1, 1]
    assert output[2, 0] != output[2, 5]      # les deux morceaux de l'étiquette 2
    expected = sum(ndimage.label(labels == value, structure=FOUR_NEIGHBOURS)[1]
                   for value in np.unique(labels))
    assert len(np.unique(output)) == expected == 6   # (0, 1) isolé par les 9 et la bande 7


def test_double_label_outside_mask_is_neutralised():
    mask = np.zeros((6, 6), bool)
    mask[1:5, 1:5] = True
    labels = np.full((6, 6), 3, np.int64)    # le moteur déborde du masque
    with slic_replaced(lambda image, **kwargs: labels.copy()):
        output = segment_rgb(random_rgb(6, 6), mask, pixel_size_m=1.0,
                             config=SlicConfig(target_segment_area_m2=4.0))
    assert_contract(output, mask)


def test_double_unlabelled_pixels_inside_mask_are_refused():
    mask = np.ones((6, 6), bool)
    for hole_value in (0, -1):
        labels = np.ones((6, 6), np.int64)
        labels[3, 3] = hole_value
        with slic_replaced(lambda image, labels=labels, **kwargs: labels.copy()), \
                raises(RuntimeError, "sans segment"):
            segment_rgb(random_rgb(6, 6), mask, pixel_size_m=1.0,
                        config=SlicConfig(target_segment_area_m2=4.0))


def test_double_invalid_label_grid_is_refused():
    mask = np.ones((6, 6), bool)
    for bad in (np.ones((6, 5), np.int64), np.ones((6, 6), np.float64)):
        with slic_replaced(lambda image, bad=bad, **kwargs: bad), \
                raises(RuntimeError, "grille d'étiquettes invalide"):
            segment_rgb(random_rgb(6, 6), mask, pixel_size_m=1.0,
                        config=SlicConfig(target_segment_area_m2=4.0))


# --- Lissage préalable (smoothing_m) -------------------------------------------------------
def test_config_smoothing_bounds():
    for value in (True, False, -0.5, float("nan"), float("inf"), 20.5, "2", None):
        with raises(ValueError, "smoothing_m"):
            SlicConfig(smoothing_m=value)
    assert SlicConfig(smoothing_m=0).smoothing_m == 0.0
    assert type(SlicConfig(smoothing_m=0).smoothing_m) is float
    assert SlicConfig(smoothing_m=20).smoothing_m == 20.0


def test_masked_gaussian_ignore_l_exterieur_et_conserve_une_couleur_uniforme():
    mask = np.zeros((20, 20), bool)
    mask[3:17, 3:17] = True
    image = np.full((20, 20, 3), 0.4, np.float32)
    image[~mask] = 0.0
    smoothed = segment._masked_gaussian(image, mask, 3.0)
    # Normalisation par le poids du masque : pas d'assombrissement près du bord.
    assert np.allclose(smoothed[mask], 0.4, atol=1e-6)
    assert not np.any(smoothed[~mask])


def test_real_lissage_insensible_aux_valeurs_hors_masque():
    mask = np.zeros((40, 40), bool)
    mask[5:35, 5:35] = True
    base = random_rgb(40, 40)
    other = base.copy()
    other[~mask] = 255 - other[~mask]
    config = SlicConfig(target_segment_area_m2=16.0, smoothing_m=2.0)
    first = segment_rgb(base, mask, pixel_size_m=0.5, config=config)
    second = segment_rgb(other, mask, pixel_size_m=0.5, config=config)
    assert np.array_equal(first, second)


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in list(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
        else:
            print(f"PASS {name}")
    print(f"{len(tests) - failed} réussis, {failed} échoués")
    sys.exit(1 if failed else 0)
