from cynogis.core.algorithms import (
    ALGORITHMS,
    CATEGORIES,
    get_spec,
    is_allowed,
    search_algorithms,
)


def test_identifiants_uniques():
    identifiants = [spec.algorithm_id for spec in ALGORITHMS]
    assert len(identifiants) == len(set(identifiants))


def test_categories_connues():
    assert all(spec.category in CATEGORIES for spec in ALGORITHMS)


def test_liste_blanche():
    assert is_allowed("native:buffer")
    assert not is_allowed("qgis:executepython")
    assert get_spec("inconnu") is None


def test_recherche_sans_accent():
    resultats = search_algorithms("reprojeter")
    assert any(spec.algorithm_id == "native:reprojectlayer" for spec in resultats)


def test_recherche_par_categorie():
    resultats = search_algorithms(category="tampon")
    assert resultats and all(spec.category == "tampon" for spec in resultats)


def test_recherche_multi_termes():
    assert search_algorithms("tampon unilateral")
