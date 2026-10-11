import pytest

from cynogis.core.landscape import (
    CLASSES,
    GROUPS,
    apply_mapping,
    classes_for,
    get_class,
    merge_nomenclature,
    score_match,
    suggest_mapping,
    validate_codes,
)


def test_codes_uniques():
    codes = [item.code for item in CLASSES]
    assert len(codes) == len(set(codes))


def test_groupes_connus():
    assert all(item.group in GROUPS for item in CLASSES)


def test_classes_specifiques_territoire():
    reunion = {item.code for item in classes_for("reunion")}
    mayotte = {item.code for item in classes_for("mayotte")}
    assert "3.1.3" in reunion and "3.1.3" not in mayotte   # tamarinaie
    assert "3.3.3" in mayotte and "3.3.3" not in reunion   # padza
    assert "5.1.1" in reunion and "5.1.1" in mayotte       # ravine, commune


def test_classes_for_territoire_inconnu():
    with pytest.raises(ValueError):
        classes_for("guadeloupe")


def test_validate_codes():
    assert validate_codes(["2.1.1", "9.9.9"]) == ["9.9.9"]
    assert validate_codes(["3.1.3"], "mayotte") == ["3.1.3"]


def test_score_match_exact_et_mot_cle():
    canne = get_class("2.1.1")
    assert score_match("Canne à sucre", canne) == 1.0
    assert score_match("canne", canne) >= 0.8


def test_suggest_mapping_reconnait_les_libelles():
    proposition = suggest_mapping(["Canne à sucre", "Ravine", "Mangrove"], "mayotte")
    assert proposition["mapping"]["Ravine"]["code"] == "5.1.1"
    assert proposition["mapping"]["Mangrove"]["code"] == "4.2.1"


def test_suggest_mapping_valeurs_inconnues():
    proposition = suggest_mapping(["zone XYZ 42"], "reunion")
    assert proposition["unmatched"] == ["zone XYZ 42"]
    assert proposition["matched_count"] == 0


def test_apply_mapping_insensible_aux_accents():
    mapping = {"Forêt humide": "3.1.1"}
    assert apply_mapping("foret humide", mapping) == "3.1.1"
    assert apply_mapping("autre chose", mapping, default="3.3.4") == "3.3.4"


def test_merge_nomenclature_valide():
    ajout = merge_nomenclature(
        [
            {"code": "9.1.1", "label": "Zone test", "group": "1", "territory": "reunion"}
        ]
    )
    assert ajout[0].code == "9.1.1"


@pytest.mark.parametrize(
    "entree",
    [
        {"code": "2.1.1", "label": "Doublon", "group": "2"},
        {"code": "9.2.1", "label": "Sans groupe", "group": "7"},
        {"code": "", "label": "Sans code", "group": "1"},
    ],
)
def test_merge_nomenclature_refuse(entree):
    with pytest.raises(ValueError):
        merge_nomenclature([entree])


@pytest.mark.parametrize("valeur", ["Transport", "Zone commerciale", "Litière"])
def test_score_match_mots_entiers(valeur):
    # « port », « mer », « lit » ne doivent pas être trouvés à l'intérieur d'un mot
    assert score_match(valeur, get_class("1.2.4")) < 0.8
    assert score_match(valeur, get_class("5.2.2")) < 0.8
    assert score_match(valeur, get_class("5.1.1")) < 0.8
