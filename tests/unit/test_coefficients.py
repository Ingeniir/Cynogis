import pytest

from cynogis.core.coefficients import (
    CBS_WEIGHTS,
    compute_all,
    coverage_ratio,
    density,
    footprint_ratio,
    interpret,
    resolve_category,
    weighted_ratio,
)


def parcelle():
    return [
        {"category": "bati", "area": 300.0},
        {"category": "voirie", "area": 200.0},
        {"category": "pleine_terre", "area": 400.0},
        {"category": "revetement_permeable", "area": 100.0},
    ]


def test_resolve_category_accents_et_casse():
    assert resolve_category("Pleine Terre") == "pleine_terre"
    assert resolve_category("BÂTI") == "bati"


def test_resolve_category_alias():
    assert resolve_category("enrobé", {"enrobé": "voirie"}) == "voirie"


def test_resolve_category_inconnue():
    assert resolve_category("hangar en tôle") is None


def test_weighted_ratio_cbs():
    resultat = weighted_ratio(parcelle(), CBS_WEIGHTS, 1000.0)
    # 400 x 1.0 + 100 x 0.5 = 450 sur 1000
    assert resultat["value"] == pytest.approx(0.45)
    assert resultat["unknown_categories"] == {}


def test_weighted_ratio_categorie_inconnue_signalee():
    parts = [{"category": "inconnue", "area": 500.0}]
    resultat = weighted_ratio(parts, CBS_WEIGHTS, 500.0)
    assert resultat["unknown_categories"] == {"inconnue": 500.0}
    assert resultat["value"] == pytest.approx(0.0)


def test_weighted_ratio_surface_non_couverte():
    resultat = weighted_ratio(parcelle(), CBS_WEIGHTS, 2000.0)
    assert resultat["uncovered_area"] == pytest.approx(1000.0)


def test_coverage_ratio_impermeable():
    resultat = coverage_ratio(parcelle(), {"bati", "voirie"}, 1000.0)
    assert resultat["percent"] == pytest.approx(50.0)


def test_footprint_ratio():
    assert footprint_ratio(300.0, 1000.0)["percent"] == pytest.approx(30.0)


def test_surface_nulle_donne_none():
    assert footprint_ratio(300.0, 0.0)["value"] is None
    assert weighted_ratio([], CBS_WEIGHTS, 0.0)["value"] is None


def test_density_par_hectare():
    resultat = density(25, 50_000.0)
    assert resultat["value"] == pytest.approx(5.0)


def test_compute_all_contenu():
    resultats = compute_all(parcelle(), total_area=1000.0, floor_area=600.0, count=4)
    assert set(resultats) >= {"cbs", "imperm", "espace_vert", "ces", "cos", "ruissellement"}
    assert resultats["cos"]["value"] == pytest.approx(0.6)


def test_compute_all_sans_donnees_optionnelles():
    resultats = compute_all(parcelle(), total_area=1000.0)
    assert "cos" not in resultats
    assert "densite" not in resultats


def test_interpret_phrases():
    assert "forte" in interpret("imperm", 0.9).lower()
    assert interpret("imperm", None).startswith("Valeur non calculable")
