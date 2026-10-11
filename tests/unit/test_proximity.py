import pytest

from cynogis.core.proximity import distance_matrix, nearest, ordered_ring


def test_nearest_k_et_distance_max():
    candidats = [("c", 30.0), ("a", 10.0), ("b", 20.0)]
    assert nearest(candidats, 2) == [("a", 10.0), ("b", 20.0)]
    assert nearest(candidats, 5, max_distance=15.0) == [("a", 10.0)]


def test_nearest_egalite_reproductible():
    assert nearest([(2, 5.0), (1, 5.0)], 1) == [(1, 5.0)]


def test_distance_matrix_cases_absentes():
    matrice = distance_matrix([(1, "P1")], [(1, "P1"), (2, "P2")], {(1, 2): 12.3456})
    assert matrice["columns"] == ["P1", "P2"]
    assert matrice["rows"][0] == {"id": "P1", "distances": [None, 12.35]}


def test_ordered_ring_ordre_numerique_et_fermeture():
    points = [(10, 0.0, 10.0), (2, 10.0, 0.0), (1, 0.0, 0.0), (3, 10.0, 10.0)]
    # 2 avant 10 : tri numérique et non alphabétique
    assert ordered_ring(points) == [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0),
                                    (0.0, 0.0)]


def test_ordered_ring_doublons_et_anneau_deja_ferme():
    points = [(1, 0.0, 0.0), (2, 5.0, 0.0), (3, 5.0, 0.0), (4, 5.0, 5.0), (5, 0.0, 0.0)]
    assert ordered_ring(points) == [(0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 0.0)]


def test_ordered_ring_trop_peu_de_points():
    with pytest.raises(ValueError, match="3 points"):
        ordered_ring([(1, 0.0, 0.0), (2, 1.0, 1.0), (3, 1.0, 1.0)])
