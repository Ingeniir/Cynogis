"""Caractéristiques RGB et voisinages OBIA (landcover_processing/object_features.py).

Nécessite NumPy seulement : ni QGIS, ni GDAL, ni SciPy, ni scikit-image. Sous pytest sans
NumPy, la suite est ignorée explicitement. Exécution :

    .venv/Scripts/python -m pytest tests/integration/test_object_features.py
    .venv/Scripts/python scripts/run_qgis_integration.py -- -q TEST
    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" TEST

(TEST = tests/integration/test_object_features.py)

Valeurs attendues : calculées à la main (test_hand_*) ou par un oracle indépendant en
listes Python, avec visite droite/bas des frontières (test_oracle_*). La fonction testée
n'est jamais utilisée pour produire une valeur attendue. Aucun seuil de durée.
Ces essais vérifient un contrat numérique, pas la qualité des paysages.
"""
from __future__ import annotations

import contextlib
import dataclasses
import math
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[2] / "plugin"

if __name__ == "__main__":
    sys.path.insert(0, str(PLUGIN_DIR))
else:
    import pytest

    pytest.importorskip("numpy", reason="NumPy absent : suite des caractéristiques OBIA ignorée")

import numpy as np  # noqa: E402

from cynogis.landcover_processing.object_features import (  # noqa: E402
    MAX_PIXELS,
    ObjectFeatures,
    extract_object_features,
)

UINT32_MAX = 4_294_967_295
SEED = 20261124


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


def uniform_rgb(height, width, value=(10, 20, 30)):
    rgb = np.empty((height, width, 3), np.uint8)
    rgb[...] = value
    return rgb


def labels_of(rows):
    return np.array(rows, dtype=np.uint32)


def oracle(rgb, labels, mask, resolution):
    """Calcul indépendant en listes Python : objets puis arêtes (visite droite/bas)."""
    height, width = len(labels), len(labels[0])
    pixels: dict[int, list[tuple[int, int]]] = {}
    for r in range(height):
        for c in range(width):
            if mask[r][c]:
                pixels.setdefault(int(labels[r][c]), []).append((r, c))
    objects = []
    for segment in sorted(pixels):
        cells = pixels[segment]
        n = len(cells)
        means, stds = [], []
        for band in range(3):
            values = [float(rgb[r][c][band]) for r, c in cells]
            mean = math.fsum(values) / n
            means.append(mean)
            stds.append(math.sqrt(math.fsum((v - mean) ** 2 for v in values) / n))
        objects.append({
            "segment_id": segment,
            "pixel_count": n,
            "area_m2": n * resolution * resolution,
            "center_row": math.fsum(r for r, _ in cells) / n + 0.5,
            "center_col": math.fsum(c for _, c in cells) / n + 0.5,
            "bbox": (min(r for r, _ in cells), max(r for r, _ in cells) + 1,
                     min(c for _, c in cells), max(c for _, c in cells) + 1),
            "rgb_mean": means,
            "rgb_std": stds,
        })
    sides: dict[tuple[int, int], int] = {}
    for r in range(height):
        for c in range(width):
            here = int(labels[r][c])
            for nr, nc in ((r, c + 1), (r + 1, c)):          # droite et bas seulement
                if nr < height and nc < width:
                    there = int(labels[nr][nc])
                    if here > 0 and there > 0 and here != there:
                        key = (min(here, there), max(here, there))
                        sides[key] = sides.get(key, 0) + 1
    edges = [(a, b, n, n * resolution) for (a, b), n in sorted(sides.items())]
    return objects, edges


def assert_matches_oracle(result, expected_objects, expected_edges):
    objects = result.objects
    assert objects["segment_id"].tolist() == [o["segment_id"] for o in expected_objects]
    assert objects["pixel_count"].tolist() == [o["pixel_count"] for o in expected_objects]
    bbox = objects[["row_min", "row_max_exclusive", "col_min", "col_max_exclusive"]]
    assert bbox.tolist() == [o["bbox"] for o in expected_objects]
    for name in ("area_m2", "center_row", "center_col"):
        assert np.allclose(objects[name], [o[name] for o in expected_objects],
                           rtol=1e-12, atol=1e-12), name
    for name in ("rgb_mean", "rgb_std"):
        assert np.allclose(objects[name], [o[name] for o in expected_objects],
                           rtol=1e-9, atol=1e-9), name
    got = result.edges
    assert [(int(e["segment_a"]), int(e["segment_b"]), int(e["shared_pixel_sides"]))
            for e in got] == [(a, b, n) for a, b, n, _ in expected_edges]
    assert np.allclose(got["shared_boundary_m"], [m for *_, m in expected_edges],
                       rtol=1e-12, atol=0)


def assert_invariants(result, mask, resolution):
    objects, edges = result.objects, result.edges
    analysed = int(np.count_nonzero(mask))
    assert int(objects["pixel_count"].sum()) == analysed
    assert np.allclose(objects["area_m2"], objects["pixel_count"] * resolution ** 2)
    assert math.isclose(float(objects["area_m2"].sum()), analysed * resolution ** 2)
    assert np.all(np.diff(objects["segment_id"].astype(np.int64)) > 0)   # trié, unique
    assert np.all(objects["segment_id"] > 0)
    assert np.all(edges["segment_a"] < edges["segment_b"])
    pairs = list(zip(edges["segment_a"].tolist(), edges["segment_b"].tolist(), strict=True))
    assert pairs == sorted(set(pairs))                                   # trié, unique
    assert np.all(edges["shared_pixel_sides"] > 0)
    assert np.allclose(edges["shared_boundary_m"],
                       edges["shared_pixel_sides"] * resolution, rtol=1e-12, atol=0)
    known = set(objects["segment_id"].tolist())
    assert set(edges["segment_a"].tolist()) <= known
    assert set(edges["segment_b"].tolist()) <= known


# --- Exemples calculés à la main -----------------------------------------------------------
TWO_RGB = np.array([[[0, 10, 20], [2, 12, 22]],
                    [[10, 20, 30], [14, 24, 34]]], dtype=np.uint8)
FULL_2X2 = np.ones((2, 2), dtype=bool)


def test_hand_two_objects():
    result = extract_object_features(TWO_RGB, labels_of([[2, 2], [9, 9]]), FULL_2X2,
                                     pixel_size_m=0.5)
    assert isinstance(result, ObjectFeatures)
    objects = result.objects
    assert objects["segment_id"].tolist() == [2, 9]
    assert objects["pixel_count"].tolist() == [2, 2]
    assert objects["area_m2"].tolist() == [0.5, 0.5]                     # 2 x 0,25 m²
    assert objects["center_row"].tolist() == [0.5, 1.5]
    assert objects["center_col"].tolist() == [1.0, 1.0]
    assert objects[["row_min", "row_max_exclusive", "col_min",
                    "col_max_exclusive"]].tolist() == [(0, 1, 0, 2), (1, 2, 0, 2)]
    assert objects["rgb_mean"].tolist() == [[1.0, 11.0, 21.0], [12.0, 22.0, 32.0]]
    assert objects["rgb_std"].tolist() == [[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]
    # Deux côtés verticaux partagés : 2 x 0,5 m.
    assert result.edges.tolist() == [(2, 9, 2, 1.0)]


def test_hand_checker_counts_both_directions_once():
    result = extract_object_features(TWO_RGB, labels_of([[1, 2], [2, 1]]), FULL_2X2,
                                     pixel_size_m=0.5)
    # 2 côtés horizontaux + 2 verticaux ; les diagonales 1-1 et 2-2 n'en sont pas.
    assert result.edges.tolist() == [(1, 2, 4, 2.0)]


def test_hand_sparse_ids_diagonal_and_uint32_max():
    sparse = labels_of([[1, 0], [0, UINT32_MAX]])
    result = extract_object_features(TWO_RGB, sparse, sparse > 0, pixel_size_m=1)
    assert result.objects["segment_id"].tolist() == [1, UINT32_MAX]
    assert result.objects["rgb_mean"].tolist() == [[0.0, 10.0, 20.0], [14.0, 24.0, 34.0]]
    assert result.objects["rgb_std"].tolist() == [[0.0] * 3, [0.0] * 3]
    assert result.edges.size == 0                                         # contact diagonal


def test_hand_ring_with_hole():
    ring = np.ones((3, 3), dtype=np.uint32)
    ring[1, 1] = 0
    result = extract_object_features(uniform_rgb(3, 3, (255, 255, 255)), ring, ring > 0,
                                     pixel_size_m=2)
    assert result.objects["pixel_count"].tolist() == [8]
    assert result.objects["area_m2"].tolist() == [32.0]                  # 8 x 4 m²
    assert result.objects["center_row"].tolist() == [1.5]                 # (0x3+1x2+2x3)/8
    assert result.objects["center_col"].tolist() == [1.5]
    assert result.objects["rgb_mean"].tolist() == [[255.0] * 3]
    assert result.edges.size == 0                                         # trou = fond


def test_hand_single_pixel_grid():
    result = extract_object_features(uniform_rgb(1, 1, (7, 8, 9)), labels_of([[42]]),
                                     np.ones((1, 1), bool), pixel_size_m=3)
    scalars = ("segment_id", "pixel_count", "area_m2", "center_row", "center_col",
               "row_min", "row_max_exclusive", "col_min", "col_max_exclusive")
    assert result.objects[list(scalars)].tolist() == [(42, 1, 9.0, 0.5, 0.5, 0, 1, 0, 1)]
    assert result.objects["rgb_mean"].tolist() == [[7.0, 8.0, 9.0]]
    assert result.objects["rgb_std"].tolist() == [[0.0, 0.0, 0.0]]
    assert result.edges.size == 0


def test_hand_row_and_column_strips():
    row = labels_of([[1, 1, 2, 3, 3]])
    result = extract_object_features(uniform_rgb(1, 5), row, row > 0, pixel_size_m=0.5)
    assert result.objects["center_col"].tolist() == [1.0, 2.5, 4.0]
    assert result.objects["center_row"].tolist() == [0.5, 0.5, 0.5]
    assert result.edges.tolist() == [(1, 2, 1, 0.5), (2, 3, 1, 0.5)]

    column = row.T.copy()
    result = extract_object_features(uniform_rgb(5, 1), column, column > 0,
                                     pixel_size_m=0.5)
    assert result.objects["center_row"].tolist() == [1.0, 2.5, 4.0]
    assert result.objects["center_col"].tolist() == [0.5, 0.5, 0.5]
    assert result.objects[["row_min", "row_max_exclusive"]].tolist() == [
        (0, 2), (2, 3), (3, 5)]
    assert result.edges.tolist() == [(1, 2, 1, 0.5), (2, 3, 1, 0.5)]


def test_hand_background_between_objects_is_not_an_edge():
    labels = labels_of([[1, 0, 2], [1, 0, 2]])
    result = extract_object_features(uniform_rgb(2, 3), labels, labels > 0, pixel_size_m=1)
    assert result.objects["segment_id"].tolist() == [1, 2]
    assert result.edges.size == 0


def test_hand_disjoint_parts_of_one_label_stay_one_row():
    # Connexité non revérifiée : une ligne regroupe tous les pixels du label (contrat).
    labels = labels_of([[5, 6, 5]])
    result = extract_object_features(uniform_rgb(1, 3), labels, labels > 0, pixel_size_m=1)
    assert result.objects["segment_id"].tolist() == [5, 6]
    assert result.objects["pixel_count"].tolist() == [2, 1]
    assert result.objects["center_col"].tolist() == [1.5, 1.5]
    assert result.edges.tolist() == [(5, 6, 2, 2.0)]


def test_constant_rgb_has_exact_mean_and_zero_std():
    rng = np.random.default_rng(SEED)
    labels = rng.integers(1, 6, (7, 9)).astype(np.uint32)
    result = extract_object_features(uniform_rgb(7, 9, (0, 128, 255)), labels,
                                     np.ones((7, 9), bool), pixel_size_m=1)
    assert np.all(result.objects["rgb_mean"] == [0.0, 128.0, 255.0])
    assert np.all(result.objects["rgb_std"] == 0.0)


def test_colors_outside_mask_have_no_effect():
    rng = np.random.default_rng(SEED)
    labels = rng.integers(1, 4, (6, 6)).astype(np.uint32)
    labels[:, 0] = 0
    labels[2, 3] = 0
    mask = labels > 0
    rgb = rng.integers(0, 256, (6, 6, 3)).astype(np.uint8)
    altered = rgb.copy()
    altered[~mask] = 255 - altered[~mask]                 # 255 - x ≠ x : tout change dehors
    assert np.all(altered[~mask] != rgb[~mask])
    assert np.array_equal(altered[mask], rgb[mask])
    first = extract_object_features(rgb, labels, mask, pixel_size_m=1)
    second = extract_object_features(altered, labels, mask, pixel_size_m=1)
    assert np.array_equal(first.objects, second.objects)
    assert np.array_equal(first.edges, second.edges)


# --- Refus ---------------------------------------------------------------------------------
def test_invalid_labels_against_mask_are_refused():
    message = "positifs dans le masque et nuls à l'extérieur"
    with raises(ValueError, message):                                     # zéro dedans
        extract_object_features(uniform_rgb(2, 2), labels_of([[1, 0], [1, 1]]),
                                FULL_2X2, pixel_size_m=1)
    mask = np.array([[True, False], [True, True]])
    with raises(ValueError, message):                                     # positif dehors
        extract_object_features(uniform_rgb(2, 2), labels_of([[1, 1], [1, 1]]), mask,
                                pixel_size_m=1)


def test_refused_shapes_and_types():
    rgb, labels, mask = uniform_rgb(2, 2), labels_of([[1, 1], [2, 2]]), FULL_2X2
    for bad_rgb in (rgb.tolist(), rgb.astype(np.uint16), rgb.astype(np.float64)):
        with raises(ValueError, "rgb doit être un tableau NumPy uint8"):
            extract_object_features(bad_rgb, labels, mask, pixel_size_m=1)
    for bad_rgb in (rgb[:, :, 0], np.zeros((2, 2, 4), np.uint8), rgb[np.newaxis]):
        with raises(ValueError, r"rgb doit avoir la forme \(hauteur, largeur, 3\)"):
            extract_object_features(bad_rgb, labels, mask, pixel_size_m=1)
    for bad_labels in (labels.tolist(), labels.astype(np.int32), labels.astype(np.int64),
                       labels.astype(np.uint64), labels.astype(np.float64),
                       labels[:, :1], labels[np.newaxis]):
        with raises(ValueError, "labels doit être un tableau uint32 de la même grille"):
            extract_object_features(rgb, bad_labels, mask, pixel_size_m=1)
    for bad_mask in (mask.tolist(), mask.astype(np.uint8), mask[:1], mask[np.newaxis]):
        with raises(ValueError, "analysis_mask doit être un tableau booléen"):
            extract_object_features(rgb, labels, bad_mask, pixel_size_m=1)


def test_refused_resolutions():
    rgb, labels = uniform_rgb(2, 2), labels_of([[1, 1], [2, 2]])
    message = "pixel_size_m doit être un nombre Python fini et strictement positif"
    for bad in (0, 0.0, -1, -0.5, True, False, float("nan"), float("inf"),
                float("-inf"), 10**400, "1", None, np.float32(1.0)):
        with raises(ValueError, message):
            extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=bad)
    with raises(ValueError, "surface d'un pixel est hors limites"):        # sous-débordement
        extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=1e-200)
    with raises(ValueError, "surface d'un pixel est hors limites"):        # débordement
        extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=1e200)
    with raises(ValueError, "surface totale d'analyse est hors limites"):
        extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=1e154)


class _FloatSubclass(float):
    pass


class _IntSubclass(int):
    pass


def test_resolution_requires_exact_python_int_or_float():
    rgb, labels = uniform_rgb(2, 2), labels_of([[1, 1], [2, 2]])
    message = "pixel_size_m doit être un nombre Python fini et strictement positif"
    # np.float64 hérite de float, np.int64 non : tous deux refusés, comme les sous-classes.
    assert isinstance(np.float64(0.5), float)
    for bad in (np.float64(0.5), np.float32(0.5), np.float16(0.5), np.int64(1),
                np.int32(1), np.uint8(1), _FloatSubclass(0.5), _IntSubclass(1)):
        with raises(ValueError, message):
            extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=bad)
    as_int = extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=2)
    as_float = extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=2.0)
    assert as_int.objects["area_m2"].tolist() == [8.0, 8.0]              # 2 pixels x 4 m²
    assert as_int.objects.tobytes() == as_float.objects.tobytes()
    assert as_int.edges.tolist() == as_float.edges.tolist() == [(1, 2, 2, 4.0)]


def test_refused_empty_or_too_large_grid():
    message = "entre 1 et 1 000 000 pixels"
    for height, width in ((0, 2), (2, 0), (0, 0)):
        empty = np.zeros((height, width), np.uint32)
        with raises(ValueError, message):
            extract_object_features(np.zeros((height, width, 3), np.uint8), empty,
                                    empty > 0, pixel_size_m=1)
    height, width = 1001, 1000
    assert height * width > MAX_PIXELS
    with raises(ValueError, message):            # refus avant tout contrôle des labels
        extract_object_features(np.zeros((height, width, 3), np.uint8), None, None,
                                pixel_size_m=1)


def test_refused_empty_mask():
    with raises(ValueError, "Le masque d'analyse est vide"):
        extract_object_features(uniform_rgb(2, 2), np.zeros((2, 2), np.uint32),
                                np.zeros((2, 2), bool), pixel_size_m=1)


# --- Entrées préservées, vues, résultat indépendant ----------------------------------------
def test_readonly_strided_views_give_same_result_without_mutation():
    rng = np.random.default_rng(SEED)
    base_rgb = rng.integers(0, 256, (12, 10, 3)).astype(np.uint8)
    base_labels = rng.integers(0, 5, (12, 10)).astype(np.uint32)
    views = (base_rgb[::2, ::-1], base_labels[::2, ::-1], (base_labels > 0)[::2, ::-1])
    for view in views:
        view.flags.writeable = False
    before = [view.copy() for view in views]
    from_views = extract_object_features(*views, pixel_size_m=0.5)
    copies = extract_object_features(*(np.ascontiguousarray(v) for v in views),
                                     pixel_size_m=0.5)
    assert all(np.array_equal(view, saved) for view, saved in zip(views, before, strict=True))
    assert np.array_equal(from_views.objects, copies.objects)
    assert np.array_equal(from_views.edges, copies.edges)
    for table in (from_views.objects, from_views.edges):
        assert all(not np.shares_memory(table, source)
                   for source in (base_rgb, base_labels))


def test_result_is_frozen_but_arrays_are_independent_copies():
    rgb, labels = TWO_RGB.copy(), labels_of([[2, 2], [9, 9]])
    result = extract_object_features(rgb, labels, FULL_2X2, pixel_size_m=1)
    try:
        result.objects = None
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("ObjectFeatures doit être figée")
    result.objects["segment_id"][:] = 0                   # tables modifiables (contrat)
    result.edges["shared_pixel_sides"][:] = 0
    assert labels.tolist() == [[2, 2], [9, 9]] and np.array_equal(rgb, TWO_RGB)


# --- Oracle indépendant et invariants --------------------------------------------------------
_SPREAD_IDS = np.array([0, 3, 17, 1000, 65_536, 2_000_000_000, UINT32_MAX], np.uint32)


def _random_case(rng, height, width, max_label, background):
    raw = rng.integers(1, max_label + 1, (height, width))
    raw[rng.random((height, width)) < background] = 0
    if not raw.any():
        raw[0, 0] = 1
    labels = _SPREAD_IDS[raw]                     # identifiants espacés, dont uint32.max
    rgb = rng.integers(0, 256, (height, width, 3)).astype(np.uint8)
    return rgb, labels, labels > 0


def test_oracle_on_several_small_grids():
    rng = np.random.default_rng(SEED)
    shapes = [(1, 1), (1, 7), (7, 1), (2, 2), (3, 5), (8, 8), (11, 6), (16, 13)]
    cases = 0
    for height, width in shapes:
        for max_label, background in ((1, 0.0), (3, 0.2), (6, 0.5)):
            rgb, labels, mask = _random_case(rng, height, width, max_label, background)
            resolution = float(rng.choice([0.2, 0.5, 1.0, 2.5]))
            result = extract_object_features(rgb, labels, mask, pixel_size_m=resolution)
            expected_objects, expected_edges = oracle(
                rgb.tolist(), labels.tolist(), mask.tolist(), resolution)
            assert_matches_oracle(result, expected_objects, expected_edges)
            assert_invariants(result, mask, resolution)
            cases += 1
    assert cases == len(shapes) * 3


def test_oracle_on_blocky_labels_resembling_segments():
    rng = np.random.default_rng(SEED + 1)
    blocks = rng.integers(1, 50, (6, 5)).astype(np.uint32)
    labels = np.kron(blocks, np.ones((4, 3), np.uint32))                 # 24 x 15
    labels[rng.random(labels.shape) < 0.05] = 0
    mask = labels > 0
    rgb = rng.integers(0, 256, (*labels.shape, 3)).astype(np.uint8)
    result = extract_object_features(rgb, labels, mask, pixel_size_m=0.5)
    expected_objects, expected_edges = oracle(rgb.tolist(), labels.tolist(),
                                              mask.tolist(), 0.5)
    assert_matches_oracle(result, expected_objects, expected_edges)
    assert_invariants(result, mask, 0.5)


def test_output_is_deterministic():
    rng = np.random.default_rng(SEED + 2)
    rgb, labels, mask = _random_case(rng, 20, 17, 6, 0.3)
    first = extract_object_features(rgb, labels, mask, pixel_size_m=0.5)
    second = extract_object_features(rgb.copy(), labels.copy(), mask.copy(),
                                     pixel_size_m=0.5)
    assert first.objects.tobytes() == second.objects.tobytes()
    assert first.edges.tobytes() == second.edges.tobytes()


def test_python_oracle_itself_on_hand_case():
    # Garde-fou de l'oracle : il doit retrouver le cas calculé à la main.
    objects, edges = oracle(TWO_RGB.tolist(), [[2, 2], [9, 9]], FULL_2X2.tolist(), 0.5)
    assert [o["segment_id"] for o in objects] == [2, 9]
    assert objects[1]["rgb_std"] == [2.0, 2.0, 2.0]
    assert edges == [(2, 9, 2, 1.0)]
    assert oracle([[[1, 2, 3]]], [[0]], [[False]], 1.0) == ([], [])


# --- Processus frais : import sans dépendance de calcul --------------------------------------
_IMPORT_SCRIPT = r"""
import sys
sys.path.insert(0, sys.argv[1])
watched = ("numpy", "scipy", "skimage", "qgis", "osgeo")
before = {m for m in watched if m in sys.modules}
import cynogis.landcover_processing.object_features as module
assert callable(module.extract_object_features)
loaded = sorted(m for m in watched if m in sys.modules and m not in before)
print("charges", loaded)
"""


def test_fresh_process_import_loads_no_computation_dependency():
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_SCRIPT, str(PLUGIN_DIR)], capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=120, check=False, env=env)
    assert result.returncode == 0, result.stderr[-2000:]
    assert "charges []" in result.stdout, result.stdout


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
