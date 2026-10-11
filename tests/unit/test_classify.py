import pytest

from cynogis.core.classify import (
    compute_breaks,
    equal_interval,
    format_number,
    natural_breaks,
    pretty_breaks,
    quantile_breaks,
    range_labels,
    standard_deviation_breaks,
)


def valeurs():
    return [1, 2, 3, 10, 11, 12, 50, 51, 52]


def test_equal_interval_amplitude_constante():
    seuils = equal_interval([0, 100], 4)
    assert seuils == [0.0, 25.0, 50.0, 75.0, 100.0]


def test_quantile_repartition():
    seuils = quantile_breaks(valeurs(), 3)
    assert len(seuils) == 4
    assert seuils[0] == 1 and seuils[-1] == 52


def test_natural_breaks_trouve_les_groupes():
    seuils = natural_breaks(valeurs(), 3)
    assert len(seuils) == 4
    # Les ruptures doivent séparer les trois paquets 1-3, 10-12 et 50-52.
    assert 3 <= seuils[1] <= 10
    assert 12 <= seuils[2] <= 50


def test_natural_breaks_grand_volume():
    seuils = natural_breaks(list(range(5000)), 5)
    assert len(seuils) == 6
    assert seuils[0] == 0 and seuils[-1] == 4999


def test_standard_deviation():
    seuils = standard_deviation_breaks([10, 20, 30, 40, 50], 4)
    assert seuils[0] <= 10 and seuils[-1] >= 50


def test_pretty_breaks_bornes_rondes():
    seuils = pretty_breaks([3, 97], 5)
    assert all(float(valeur).is_integer() for valeur in seuils)


def test_compute_breaks_methode_inconnue():
    with pytest.raises(ValueError):
        compute_breaks(valeurs(), "au_pif", 5)


def test_compute_breaks_sans_valeurs():
    with pytest.raises(ValueError):
        compute_breaks([None, "texte"], "quantile", 5)


def test_compute_breaks_ignore_les_non_numeriques():
    resultat = compute_breaks([1, "2", None, 3.5, "abc"], "equal_interval", 2)
    assert resultat["value_count"] == 3


def test_compute_breaks_reduit_les_classes():
    resultat = compute_breaks([5, 5, 5, 7], "quantile", 10)
    assert resultat["class_count"] < 10
    assert resultat["warnings"]


def test_compute_breaks_classes_hors_bornes():
    with pytest.raises(ValueError):
        compute_breaks(valeurs(), "quantile", 1)


def test_format_number_francais():
    assert format_number(1234.5678, 2) == "1 234,57"
    assert format_number(1234, 0) == "1 234"


def test_range_labels():
    libelles = range_labels([0, 10, 20], 1, "ha")
    assert libelles == ["0,0 à 10,0 ha", "10,0 à 20,0 ha"]
