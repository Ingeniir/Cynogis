import math

import pytest

from cynogis.core.metrics import (
    division_index,
    edge_density,
    effective_mesh_size,
    largest_patch_index,
    patch_density,
    shannon_evenness,
    shannon_index,
    shape_index,
    simpson_index,
    summarize_patches,
)


def test_shape_index_disque_vaut_un():
    rayon = 10.0
    aire = math.pi * rayon ** 2
    perimetre = 2 * math.pi * rayon
    assert shape_index(aire, perimetre) == pytest.approx(1.0)


def test_shape_index_carre_superieur_a_un():
    assert shape_index(100.0, 40.0) > 1.0


def test_shape_index_valeurs_nulles():
    assert shape_index(0.0, 10.0) is None


def test_shannon_une_seule_classe():
    assert shannon_index({"foret": 100.0}) == pytest.approx(0.0)


def test_shannon_deux_classes_egales():
    assert shannon_index({"a": 50.0, "b": 50.0}) == pytest.approx(math.log(2))


def test_shannon_evenness_maximale():
    assert shannon_evenness({"a": 50.0, "b": 50.0}) == pytest.approx(1.0)


def test_shannon_evenness_indefinie_si_une_classe():
    assert shannon_evenness({"a": 50.0}) is None


def test_simpson_borne():
    valeur = simpson_index({"a": 25.0, "b": 25.0, "c": 50.0})
    assert 0.0 < valeur < 1.0


def test_largest_patch_index():
    assert largest_patch_index([10.0, 30.0, 60.0]) == pytest.approx(60.0)


def test_patch_density_pour_100ha():
    # 10 taches sur 100 ha = 1 000 000 m²
    assert patch_density(10, 1_000_000.0) == pytest.approx(10.0)


def test_edge_density():
    assert edge_density(5000.0, 100_000.0) == pytest.approx(500.0)


def test_effective_mesh_size_une_seule_tache():
    assert effective_mesh_size([1000.0]) == pytest.approx(1000.0)


def test_effective_mesh_size_fragmentation():
    entier = effective_mesh_size([1000.0])
    morcele = effective_mesh_size([250.0] * 4)
    assert morcele < entier


def test_division_index_croit_avec_la_fragmentation():
    assert division_index([1000.0]) == pytest.approx(0.0)
    assert division_index([250.0] * 4) == pytest.approx(0.75)


def test_summarize_patches_complet():
    taches = [
        {"class": "foret", "area": 10000.0, "perimeter": 400.0},
        {"class": "foret", "area": 5000.0, "perimeter": 300.0},
        {"class": "canne", "area": 15000.0, "perimeter": 500.0},
    ]


    bilan = summarize_patches(taches)
    assert bilan["patch_count"] == 3
    assert bilan["class_count"] == 2
    assert bilan["total_area_ha"] == pytest.approx(3.0)
    assert bilan["classes"][0]["class"] == "canne"
    assert bilan["classes"][0]["percent"] == pytest.approx(50.0)
    assert bilan["shannon_index"] > 0


def test_summarize_patches_vide():
    bilan = summarize_patches([])
    assert bilan["patch_count"] == 0
    assert bilan["shannon_index"] is None


def test_lisiere_interne_comptee_une_fois():
    # deux carrés de 100 m accolés : 1 lisière interne de 100 m, contour du paysage 600 m
    taches = [{"class": "a", "area": 10_000.0, "perimeter": 400.0},
              {"class": "b", "area": 10_000.0, "perimeter": 400.0}]
    assert summarize_patches(taches, landscape_perimeter=600.0)["total_edge_m"] == 100.0
