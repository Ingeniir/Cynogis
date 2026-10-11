from datetime import date, datetime

import pytest

from cynogis.core.fields import (
    coerce_record,
    coerce_value,
    resolve_type,
    sanitize_field_name,
    truncate_field_names,
    unique_field_name,
)


@pytest.mark.parametrize(
    "brut,attendu",
    [("Surface (ha)", "Surface_ha"), ("n° parcelle", "n_parcelle"), ("", "champ"),
     ("2024", "c_2024")],
)
def test_sanitize_field_name(brut, attendu):
    assert sanitize_field_name(brut) == attendu


def test_sanitize_reserve():
    assert sanitize_field_name("fid") == "fid_1"


def test_unique_field_name_insensible_casse():
    assert unique_field_name("Type", ["type"]) == "Type_1"


def test_unique_field_name_tronque():
    assert unique_field_name("occupation_du_sol", [], 10) == "occupation"


def test_truncate_field_names_sans_doublon():
    mapping = truncate_field_names(["occupation_sol", "occupation_eau"], 10)
    assert len(set(mapping.values())) == 2
    assert all(len(short) <= 10 for short in mapping.values())


def test_resolve_type_alias():
    assert resolve_type("double").name == "real"
    assert resolve_type("ENTIER").name == "integer"


def test_resolve_type_inconnu():
    with pytest.raises(ValueError):
        resolve_type("polygone")


@pytest.mark.parametrize(
    "valeur,type_nom,attendu",
    [
        ("12", "integer", 12),
        (3.0, "integer", 3),
        ("1,5", "real", 1.5),
        ("oui", "boolean", True),
        (None, "integer", None),
        (42, "string", "42"),
    ],
)
def test_coerce_value(valeur, type_nom, attendu):
    assert coerce_value(valeur, type_nom) == attendu


def test_coerce_value_decimal_refuse():
    with pytest.raises(ValueError):
        coerce_value(1.5, "integer")


def test_coerce_value_dates():
    assert coerce_value("2026-10-11", "date") == date(2026, 10, 11)
    assert coerce_value("2026-10-11T08:30:00", "datetime") == datetime(2026, 10, 11, 8, 30)


def test_coerce_value_date_invalide():
    with pytest.raises(ValueError):
        coerce_value("11/13/2026", "date")


def test_coerce_record_champ_inconnu_strict():
    with pytest.raises(ValueError):
        coerce_record({"absent": 1}, {"type": "string"}, strict=True)


def test_coerce_record_non_strict():
    valeurs, avertissements = coerce_record(
        {"absent": 1, "type": "foret"}, {"type": "string"}, strict=False
    )
    assert valeurs == {"type": "foret"}
    assert avertissements
