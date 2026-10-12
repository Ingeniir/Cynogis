import pytest

from cynogis.core.sampling import allocate, unit_id


def test_allocation_proportionnelle():
    result = allocate(20, {"foret": 60.0, "savane": 30.0, "ravine": 10.0})
    assert sum(result.values()) == 20
    # 1 par strate, puis 17 répartis 60/30/10 : 10,2 / 5,1 / 1,7 → restes au plus fort
    assert result == {"foret": 11, "savane": 6, "ravine": 3}


def test_allocation_egale_et_strate_vide():
    result = allocate(10, {"a": 5.0, "b": 1.0, "c": 1.0, "vide": 0.0}, "equal")
    assert result == {"a": 4, "b": 3, "c": 3}


def test_allocation_impossible():
    with pytest.raises(ValueError):
        allocate(2, {"a": 1.0, "b": 1.0, "c": 1.0})
    with pytest.raises(ValueError):
        allocate(5, {"a": 0.0})


def test_unit_id():
    assert unit_id("P", 7, 50) == "P007" and unit_id("T", 12, 1500) == "T0012"
