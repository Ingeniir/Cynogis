import pytest

from cynogis.core.referentials import (
    BY_KEY,
    check_rules,
    find_source_file,
    is_agricultural,
    map_cirad,
    map_feature,
    map_ocsge,
    sources_for,
)


def test_tables_coherentes_avec_la_nomenclature():
    assert check_rules() == []


@pytest.mark.parametrize(
    "cs,us,attendu",
    [
        ("CS1.1.1.1", "US5", "1.1.1"),        # bâti résidentiel
        ("CS1.1.1.1", "US2", "1.2.1"),        # bâti industriel
        ("CS1.1.1.2", "US4.1.1", "1.2.2"),    # route
        ("CS1.1.1.2", "US4.1.3", "1.2.4"),    # piste d'aéroport : l'usage l'emporte
        ("CS1.2.1", "US1.3", "1.3.1"),        # carrière
        ("CS2.1.1.2", None, "3.1.5"),         # conifères : plantation
        ("CS2.1.1.1", "US5", "1.4.1"),        # arbres d'un jardin résidentiel
        ("CS2.2.1", "US1.1", "2.4.1"),        # herbacé agricole
        ("CS2.2.2", "US1.1", "2.4.1"),        # autre non ligneux agricole : culture
        ("2.1.2", "6.2", "3.2.3"),            # codes sans préfixe CS / US
    ],
)
def test_map_ocsge(cs, us, attendu):
    assert map_ocsge(cs, us, "reunion")["code"] == attendu


def test_map_ocsge_comparaison_par_segments():
    # CS1.1 ne doit pas couvrir un code CS1.11 (inexistant) par simple préfixe de texte
    assert map_ocsge("CS1.11", None, "reunion")["code"] is None


def test_map_ocsge_territoire():
    assert map_ocsge("CS2.1.1.1", None, "reunion")["code"] == "3.1.6"
    assert map_ocsge("CS2.1.1.1", None, "mayotte")["code"] == "3.1.4"


def test_map_ocsge_a_verifier():
    assert map_ocsge("CS2.2.1", "US1.1", "reunion")["review"] is True
    assert map_ocsge("CS1.1", "US2", "reunion")["review"] is False


def test_map_cirad_canne_selon_territoire():
    assert map_cirad("Canne à sucre", "reunion")["code"] == "2.1.1"
    resultat = map_cirad("Canne à sucre", "mayotte")
    assert resultat["code"] is None and resultat["review"] is True


def test_map_cirad_repli_mots_cles():
    resultat = map_cirad("Tamarinaie", "reunion")
    assert resultat["code"] == "3.1.3" and resultat["review"] is True


def test_map_feature_selon_la_source():
    assert map_feature(BY_KEY["ocsge_976_2023"],
                       {"CODE_CS": "CS2.1.1.1", "CODE_US": "US6.3"})["code"] == "3.1.4"
    assert map_feature(BY_KEY["cirad_974_2020"], {"niveau3": 3})["code"] == "2.3.1"


def test_find_source_file(tmp_path):
    source = BY_KEY["ocsge_974_2022"]
    assert find_source_file(source, tmp_path) is None
    (tmp_path / "OCSGE_974_2022.SHP").write_text("")
    (tmp_path / "ocsge_974_2022.gpkg").write_text("")
    assert find_source_file(source, tmp_path).name == "ocsge_974_2022.gpkg"  # gpkg d'abord


def test_find_source_file_dossier_absent(tmp_path):
    assert find_source_file(BY_KEY["cirad_974_2020"], tmp_path / "absent") is None


def test_sources_for_territoire():
    cles = [s.key for s in sources_for("mayotte")]
    assert cles == ["cirad_976_2023", "ocsge_976_2023", "ocsge_976_2020"]


def test_is_agricultural():
    assert is_agricultural("2.1.1") and is_agricultural("2.4.1")
    assert not is_agricultural("3.1.1") and not is_agricultural(None)


@pytest.mark.parametrize("niveau3,attendu", [(1, "2.1.1"), ("16", "3.1.6"), (22, "3.2.4"),
                                             (24, "3.3.1"), (200, "3.2.3")])
def test_cirad_974_2020_par_code(niveau3, attendu):
    assert map_feature(BY_KEY["cirad_974_2020"], {"niveau3": niveau3})["code"] == attendu


def test_cirad_974_2020_ombre_et_code_inconnu():
    ombre = map_feature(BY_KEY["cirad_974_2020"], {"niveau3": 25})
    assert ombre["code"] is None and "Ombre" in ombre["note"]
    assert map_feature(BY_KEY["cirad_974_2020"], {"niveau3": 99})["code"] is None


def test_fichier_cirad_sous_son_nom_d_origine(tmp_path):
    (tmp_path / "OS_SPOT_2020_32740.gpkg").write_text("")
    assert find_source_file(BY_KEY["cirad_974_2020"], tmp_path).name == "OS_SPOT_2020_32740.gpkg"
