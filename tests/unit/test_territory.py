import pytest

from cynogis.core.territory import detect_territory


@pytest.mark.parametrize("bbox, expected", [
    ((55.44, -20.89, 55.46, -20.87), "reunion"),   # Saint-Denis
    ((55.20, -21.40, 55.85, -20.85), "reunion"),   # île entière
    ((45.22, -12.79, 45.24, -12.77), "mayotte"),   # Mamoudzou
    ((2.30, 48.80, 2.40, 48.90), None),            # Paris
    (None, None),
])
def test_detect(bbox, expected):
    terr = detect_territory(bbox)
    assert (terr.code if terr else None) == expected
