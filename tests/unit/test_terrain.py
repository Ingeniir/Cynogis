import pytest

from cynogis.core.terrain import (
    SLOPE_CLASSES,
    altitude_band,
    aspect_sector,
    degrees_to_percent,
    distribution,
    parse_bands,
    percent_to_degrees,
    reclass_table,
    slope_class,
)


@pytest.mark.parametrize(
    "pourcent,code", [(0, 1), (4.9, 1), (5, 2), (14.9, 2), (15, 3), (30, 4), (75, 5)]
)
def test_slope_class(pourcent, code):
    assert slope_class(pourcent).code == code


def test_slope_class_negative():
    assert slope_class(-1) is None


def test_conversion_pente_aller_retour():
    assert percent_to_degrees(degrees_to_percent(30.0)) == pytest.approx(30.0)


def test_pente_45_degres_vaut_cent_pourcent():
    assert degrees_to_percent(45.0) == pytest.approx(100.0)


def test_reclass_table_pourcentage():
    table = reclass_table("percent")
    assert len(table) == len(SLOPE_CLASSES)
    assert table[0][:2] == [0.0, 5.0]
    assert table[-1][1] == 10_000.0      # borne haute finie pour QGIS


def test_reclass_table_degres():
    table = reclass_table("degrees")
    assert table[0][1] == pytest.approx(percent_to_degrees(5.0))
    assert table[-1][1] == 90.0


@pytest.mark.parametrize(
    "degres,secteur", [(0, "N"), (10, "N"), (350, "N"), (90, "E"), (180, "S"), (270, "O")]
)
def test_aspect_sector(degres, secteur):
    assert aspect_sector(degres) == secteur


def test_aspect_sector_plat():
    assert aspect_sector(-1) is None


def test_distribution():
    bilan = distribution([2.0, 3.0, 20.0, 60.0])
    assert bilan["total"] == 4
    classe_1 = next(c for c in bilan["classes"] if c["code"] == 1)
    assert classe_1["count"] == 2
    assert classe_1["percent"] == pytest.approx(50.0)


def test_tranches_altitude():
    bands = parse_bands([{"max": 800, "label": "bas"}, {"max": 1800, "label": "moyen"},
                         {"label": "haut"}])
    values = (0, 799.9, 800, 2500, None)
    assert [altitude_band(a, bands) for a in values] == ["bas", "bas", "moyen", "haut", None]
    assert altitude_band(900, parse_bands([{"max": 800, "label": "bas"}])) is None
    with pytest.raises(ValueError):
        parse_bands([{"max": 1800, "label": "a"}, {"max": 800, "label": "b"}])
    with pytest.raises(ValueError):
        parse_bands([{"max": 800}])

