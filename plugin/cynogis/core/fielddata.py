"""Données de terrain (GPX, CSV, KoboToolbox, QField) vers un schéma standard. Python pur."""
from __future__ import annotations

import csv
import io
import re
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .naming import normalize

# Schéma de la couche produite (noms <= 10 caractères : compatibles Shapefile).
STANDARD_FIELDS = (("date_obs", "string"), ("observ", "string"), ("taxon", "string"),
                   ("effectif", "integer"), ("precis_m", "real"))
COORDINATES = ("lon", "lat")
SYNONYMS: dict[str, tuple[str, ...]] = {
    "date_obs": ("date_obs", "date", "date observation", "date de l observation", "datetime",
                 "time", "timestamp", "horodatage", "today", "start", "submission time"),
    "observ": ("observ", "observateur", "observateurs", "observer", "auteur", "operateur",
               "agent", "recorder", "username", "submitted by"),
    "taxon": ("taxon", "espece", "species", "nom scientifique", "scientific name", "lb nom",
              "nom valide", "nom latin"),
    "effectif": ("effectif", "nombre", "nb", "nb individus", "count", "abondance", "individus",
                 "quantite"),
    "precis_m": ("precis m", "precision", "precision gps", "accuracy", "horizontal accuracy",
                 "hacc"),
    "lon": ("lon", "longitude", "lng", "long", "x", "coord x"),
    "lat": ("lat", "latitude", "y", "coord y"),
}
# Colonnes « groupe_question_latitude » de KoboToolbox (point GPS d'une question geopoint).
SUFFIXES = {"lat": ("latitude",), "lon": ("longitude",), "precis_m": ("precision", "accuracy")}
DATE_FORMATS = ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y")


def column_key(name: str) -> str:
    """Forme comparable d'un nom de colonne (« _GPS_Latitude » → « gps latitude »)."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", normalize(str(name))).split())


def suggest_columns(columns: Iterable[str]) -> dict[str, str]:
    """Champ standard (ou lon/lat) → colonne source, d'après les synonymes puis les suffixes
    KoboToolbox. Une colonne ne sert qu'une fois."""
    keys = {column: column_key(column) for column in columns}
    found: dict[str, str] = {}
    for target, synonyms in SYNONYMS.items():
        wanted = [column_key(s) for s in synonyms]
        free = [c for c in keys if c not in found.values()]
        match = next((c for w in wanted for c in free if keys[c] == w), None)
        if match is None:
            match = next((c for c in free if keys[c].split()[-1:] and
                          keys[c].split()[-1] in SUFFIXES.get(target, ())), None)
        if match is not None:
            found[target] = match
    return found


def parse_number(value: Any) -> float | None:
    """Nombre, virgule décimale acceptée ; None si vide. ValueError si illisible."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    return float(text) if text else None


def parse_count(value: Any) -> int | None:
    number = parse_number(value)
    if number is None:
        return None
    if not number.is_integer() or number < 0:
        raise ValueError(f"Effectif invalide : {value!r}")
    return int(number)


def parse_date(value: Any) -> str | None:
    """Date ISO (« AAAA-MM-JJ » ou « AAAA-MM-JJTHH:MM:SS ») ; formats français acceptés."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        for fmt in DATE_FORMATS:
            try:
                parsed = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Date illisible : {value!r}") from None
    if len(text) <= 10 and parsed.time() == datetime.min.time():
        return parsed.date().isoformat()
    return parsed.isoformat(timespec="seconds")


PARSERS = {"date_obs": parse_date, "effectif": parse_count, "precis_m": parse_number,
           "lon": parse_number, "lat": parse_number}


def standardize(record: Mapping[str, Any], mapping: Mapping[str, str]) -> tuple[dict, list[str]]:
    """Valeurs standard (et lon/lat) d'un enregistrement ; liste des champs illisibles."""
    values: dict[str, Any] = {}
    problems: list[str] = []
    for target, column in mapping.items():
        raw = record.get(column)
        parser = PARSERS.get(target)
        if parser is None:
            values[target] = None if raw in (None, "") else str(raw).strip()
            continue
        try:
            values[target] = parser(raw)
        except (TypeError, ValueError):
            values[target] = None
            problems.append(target)
    return values, problems


def read_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Colonnes et lignes d'un CSV : séparateur (, ; tabulation) et encodage détectés."""
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    try:
        dialect: Any = csv.Sniffer().sniff(text[:20000], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    rows = [row for row in reader if any((v or "").strip() for v in row.values())]
    return list(reader.fieldnames or []), rows
