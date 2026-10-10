import pytest

from cynogis.core.units import convert_area, convert_length


def test_conversions():
    assert convert_area(10_000, "ha") == 1.0
    assert convert_area(2_500_000, "km2") == 2.5
    assert convert_length(1_500, "km") == 1.5


def test_unknown_unit():
    with pytest.raises(ValueError):
        convert_area(1, "acre")
