import math

import pytest

from cynogis.core.resolve import half_plane_corners, rank_records, summarize_resolution


def records():
    return [
        {"id": 1, "order": 0, "area": 10.0, "value": 3},
        {"id": 2, "order": 1, "area": 50.0, "value": 1},
        {"id": 3, "order": 2, "area": 20.0, "value": None},
    ]

def test_keep_largest():
    rangs = rank_records(records(), "keep_largest")
    assert rangs[2] < rangs[3] < rangs[1]


def test_priority_field_asc():
    rangs = rank_records(records(), "priority_field")
    assert rangs[2] == 0 and rangs[1] == 1
    assert rangs[3] == 2  # valeur absente : toujours en dernier


def test_priority_field_desc():
    rangs = rank_records(records(), "priority_field", "desc")
    assert rangs[1] == 0 and rangs[2] == 1 and rangs[3] == 2


def test_egalite_stable():
    plats = [
        {"id": 7, "order": 0, "area": 5.0, "value": 1},
        {"id": 8, "order": 1, "area": 5.0, "value": 1},
    ]
    assert rank_records(plats, "keep_largest") == {7: 0, 8: 1}


def test_strategie_inconnue():
    with pytest.raises(ValueError):
        rank_records(records(), "n_importe_quoi")


def test_half_plane_contient_le_milieu_cote_a():
    coins = half_plane_corners(0.0, 0.0, 10.0, 0.0, 100.0)
    xs = [x for x, _ in coins]
    assert max(xs) == pytest.approx(5.0)   # la frontière est la médiatrice
    assert min(xs) < 0                      # le rectangle couvre le côté de A


def test_half_plane_centres_confondus():
    with pytest.raises(ValueError):
        half_plane_corners(1.0, 1.0, 1.0, 1.0, 10.0)


def test_half_plane_diagonale():
    coins = half_plane_corners(0.0, 0.0, 10.0, 10.0, 50.0)
    assert all(math.isfinite(x) and math.isfinite(y) for x, y in coins)


def test_summarize():
    bilan = summarize_resolution(
        [
            {"id": 1, "status": "unchanged", "area_before": 10.0, "area_after": 10.0},
            {"id": 2, "status": "clipped", "area_before": 20.0, "area_after": 15.0},
            {"id": 3, "status": "removed", "area_before": 5.0, "area_after": 0.0},
        ]
    )
    assert bilan["features_out"] == 2
    assert bilan["features_removed"] == 1
    assert bilan["area_removed"] == pytest.approx(10.0)
