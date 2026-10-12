import pytest

from cynogis.core.stakes import (
    level_for,
    level_number,
    parse_criteria,
    parse_overrides,
    parse_thresholds,
    score,
    to_score,
)

CRITERIA = parse_criteria([
    {"name": "protection", "expression": '"nb_prot" > 0', "weight": 3},
    {"name": "rarete", "expression": '"rarete"', "weight": 2, "max": 4},
    {"name": "naturalite", "expression": '"nat"', "max": 3},
])


def test_score_pondere():
    assert score({"protection": 1, "rarete": 4, "naturalite": 3}, CRITERIA) == 100.0
    # (3*1 + 2*0.5 + 1*0) / 6 = 66,7 ; valeur au-delà du max plafonnée, absente = 0
    assert score({"protection": 1, "rarete": 2, "naturalite": None}, CRITERIA) == 66.7
    assert score({"protection": 0, "rarete": 9, "naturalite": -1}, CRITERIA) == pytest.approx(
        33.3)


def test_niveaux():
    thresholds = parse_thresholds(None)
    assert [level_for(v, thresholds) for v in (0, 19.9, 20, 59.9, 60, 80, 100)] == \
        [1, 1, 2, 3, 4, 5, 5]
    assert level_number("très fort") == 4 and level_number(5) == 5
    with pytest.raises(ValueError):
        level_number("énorme")
    with pytest.raises(ValueError):
        parse_thresholds([50, 40, 60, 80])


def test_validation():
    assert to_score(True) == 1.0 and to_score("2,5") is None and to_score(None) is None
    with pytest.raises(ValueError):
        parse_criteria([{"name": "a", "expression": "1", "weight": 0}])
    with pytest.raises(ValueError):
        parse_criteria([{"name": "a", "expression": "1"}, {"name": "a", "expression": "2"}])
    rule = parse_overrides([{"expression": '"nb_prot" > 0', "level": "fort"}])[0]
    assert rule.level == 3 and rule.label == '"nb_prot" > 0'
