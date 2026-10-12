import pytest

from cynogis.core.fielddata import (
    parse_count,
    parse_date,
    parse_number,
    read_csv,
    standardize,
    suggest_columns,
)


def test_colonnes_terrain():
    found = suggest_columns(["Date", "Observateur", "Espèce", "Nb individus", "Latitude",
                             "Longitude", "Remarque"])
    assert found == {"date_obs": "Date", "observ": "Observateur", "taxon": "Espèce",
                     "effectif": "Nb individus", "lon": "Longitude", "lat": "Latitude"}


def test_colonnes_kobo():
    found = suggest_columns(["today", "_releve_gps_latitude", "_releve_gps_longitude",
                             "_releve_gps_altitude", "_releve_gps_precision", "_submitted_by"])
    assert found == {"date_obs": "today", "observ": "_submitted_by",
                     "precis_m": "_releve_gps_precision", "lon": "_releve_gps_longitude",
                     "lat": "_releve_gps_latitude"}


def test_valeurs():
    assert parse_number("55,4521") == pytest.approx(55.4521)
    assert parse_number(" ") is None
    assert parse_count("3") == 3 and parse_count("2.0") == 2
    with pytest.raises(ValueError):
        parse_count("2,5")
    assert parse_date("12/10/2026") == "2026-10-12"
    assert parse_date("2026-10-12T08:15:00.000+04:00") == "2026-10-12T08:15:00+04:00"
    assert parse_date("12/10/2026 08:15") == "2026-10-12T08:15:00"
    with pytest.raises(ValueError):
        parse_date("hier")


def test_standardize_signale_les_valeurs_illisibles():
    values, problems = standardize({"n": "beaucoup", "sp": " Bulbul ", "d": "12/10/2026"},
                                   {"effectif": "n", "taxon": "sp", "date_obs": "d"})
    assert values == {"effectif": None, "taxon": "Bulbul", "date_obs": "2026-10-12"}
    assert problems == ["effectif"]


def test_read_csv_point_virgule_cp1252(tmp_path):
    path = tmp_path / "releve.csv"
    path.write_bytes("Espèce;Latitude;Longitude\nTec-tec;-21,1;55,5\n;;\n".encode("cp1252"))
    columns, rows = read_csv(path)
    assert columns == ["Espèce", "Latitude", "Longitude"]
    assert rows == [{"Espèce": "Tec-tec", "Latitude": "-21,1", "Longitude": "55,5"}]
