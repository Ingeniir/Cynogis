import pytest

from cynogis.core.colors import (
    contrast_ratio,
    darken,
    distinct_colors,
    interpolate_ramp,
    lighten,
    mix,
    parse_color,
    readable_text_color,
    to_hex,
    to_rgba_string,
    validate_colors,
)


@pytest.mark.parametrize(
    "valeur,attendu",
    [
        ("#1a9641", (26, 150, 65, 255)),
        ("1a9641", (26, 150, 65, 255)),
        ("#fff", (255, 255, 255, 255)),
        ("rgb(26,150,65)", (26, 150, 65, 255)),
        ("vert_fonce", (0, 104, 55, 255)),
        ((26, 150, 65), (26, 150, 65, 255)),
    ],
)
def test_parse_color(valeur, attendu):
    assert parse_color(valeur) == attendu


def test_parse_color_avec_alpha():
    assert parse_color("rgba(26,150,65,0.5)")[3] == 128


@pytest.mark.parametrize("valeur", ["#12345", "bleu_turquoise_inexistant", "rgb(300,0,0)", None])
def test_parse_color_refuse(valeur):
    with pytest.raises(ValueError):
        parse_color(valeur)


def test_to_hex_et_rgba():
    assert to_hex("rgb(26,150,65)") == "#1a9641"
    assert to_rgba_string("#1a9641") == "26,150,65,255"


def test_mix_milieu():
    assert mix("#000000", "#ffffff", 0.5).startswith("#808080")


def test_lighten_darken():
    assert lighten("#808080") != "#808080"
    assert contrast_ratio(darken("#808080"), "#ffffff") > contrast_ratio("#808080", "#ffffff")


def test_contraste_extremes():
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0, abs=0.1)


def test_readable_text_color():
    assert readable_text_color("#ffffff") == "#000000"
    assert readable_text_color("#1f4e79") == "#ffffff"


def test_interpolate_ramp_longueurs():
    assert len(interpolate_ramp(["#000000", "#ffffff"], 5)) == 5
    assert interpolate_ramp(["#1a9641"], 3) == ["#1a9641ff"] * 3


def test_interpolate_ramp_extremites_conservees():
    rampe = interpolate_ramp(["#000000", "#ffffff"], 4)
    assert rampe[0].startswith("#000000")
    assert rampe[-1].startswith("#ffffff")


def test_distinct_colors_sans_doublon():
    couleurs = distinct_colors(12)
    assert len(couleurs) == 12
    assert len(set(couleurs)) == 12


def test_validate_colors_message_indexe():
    with pytest.raises(ValueError, match="n°2"):
        validate_colors(["#1a9641", "pas_une_couleur"])
