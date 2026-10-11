"""Nom, types et valeurs de champs - logique indépendante de PyQGIS."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from .naming import to_ascii

NAME_LIMITS = {"gpkg": 63, "shp": 10, "geojson": 63, "memory": 63}

RESERVED_FIELDS = frozenset({"fid", "ogc_fid", "geom", "geometry", "the_geom", "_uid_"})

_INVALID_FIELD = re.compile(r"[^A-Za-z0-9_]+")

@dataclass(frozen=True)
class FieldType:
    """Type logique de champ, traduit ensuite en type Qt par la couche QGIS."""

    name: str
    label: str
    qt_name: str
    default_length: int
    default_precision: int
    shapefile_ok: bool = True

FIELD_TYPES: dict[str, FieldType] = {
    "string": FieldType("string", "Texte", "QString", 254, 0),
    "integer": FieldType("integer", "Entier", "int", 10, 0),
    "long": FieldType("long", "Entier long", "qlonglong", 18, 0),
    "real": FieldType("real", "Décimal", "double", 20, 6),
    "boolean": FieldType("boolean", "Booléen", "bool", 1, 0, shapefile_ok=False),
    "date": FieldType("date", "Date", "QDate", 10, 0),
    "datetime": FieldType("datetime", "Date et heure", "QDateTime", 0, 0, shapefile_ok=False),
}

ALIASES = {
    "text": "string", "str": "string", "varchar": "string", "texte": "string",
    "int": "integer", "entier": "integer", "int64": "long", "bigint": "long",
    "double": "real", "float": "real", "decimal": "real", "numeric": "real",
    "bool": "boolean", "booleen": "boolean",
}

def resolve_type(name: str) -> FieldType:
    """Traduit un nom de type libre en type Cynogis, erreur claire sinon."""
    key = to_ascii(str(name or "")).strip().lower()
    key = ALIASES.get(key, key)
    if key not in FIELD_TYPES:
        raise ValueError(
            f"Type de champ inconnu : {name}. Types acceptés : {', '.join(FIELD_TYPES)}."
        )
    return FIELD_TYPES[key]

def sanitize_field_name(name: str, limit: int = 63) -> str:
    """Nettoie un nom de champ : sans accent, sans espace, jamais vide."""
    candidate = _INVALID_FIELD.sub("_", to_ascii(str(name or "")).strip())
    candidate = re.sub(r"_{2,}", "_", candidate).strip("_")
    if not candidate:
        candidate = "champ"
    if candidate[0].isdigit():
        candidate = f"c_{candidate}"
    candidate = candidate[:limit].strip("_") or "champ"
    if candidate.lower() in RESERVED_FIELDS:
        candidate = f"{candidate}_1"[:limit]
    return candidate


def unique_field_name(name: str, existing: Iterable[str], limit: int = 63) -> str:
    """Nom de champ nettoyé et non déjà utilisé, troncature comprise.

    La comparaison ignore la casse : les pilotes OGR ne distinguent pas
    « Surface » de « surface ».
    """
    used = {str(value).lower() for value in existing}
    base = sanitize_field_name(name, limit)
    if base.lower() not in used:
        return base
    for index in range(1, 1000):
        suffix = f"_{index}"
        candidate = base[: max(limit - len(suffix), 1)].strip("_") + suffix
        if candidate.lower() not in used:
            return candidate
    raise ValueError(f"Impossible de trouver un nom de champ libre à partir de « {name} ».")


def truncate_field_names(names: Sequence[str], limit: int = 10) -> dict[str, str]:
    """Table de correspondance nom d'origine -> nom tronqué unique.

    Utilisée à l'export Shapefile, où les noms sont limités à 10 caractères :
    on maîtrise la troncature au lieu de laisser OGR produire des doublons.
    """
    mapping: dict[str, str] = {}
    taken: list[str] = []
    for name in names:
        short = unique_field_name(name, taken, limit)
        mapping[name] = short
        taken.append(short)
    return mapping


def _parse_date(value: Any, with_time: bool):
    if isinstance(value, datetime):
        return value if with_time else value.date()
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day) if with_time else value
    text = str(value).strip().replace("/", "-")
    if text.endswith("Z"):
        text = text[:-1]
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        attendu = "AAAA-MM-JJ HH:MM:SS" if with_time else "AAAA-MM-JJ"
        raise ValueError(f"Date invalide : {value!r} (format attendu : {attendu}).") from exc
    return parsed if with_time else parsed.date()


def coerce_value(value: Any, type_name: str) -> Any:
    """Convertit une valeur JSON vers le type du champ, ou lève une erreur.

    La valeur None est toujours acceptée : elle représente une valeur absente.
    """
    if value is None:
        return None
    field_type = resolve_type(type_name)
    kind = field_type.name
    if kind == "string":
        return value if isinstance(value, str) else str(value)
    if kind in ("integer", "long"):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Valeur décimale {value} refusée pour un champ entier.")
            return int(value)
        try:
            return int(str(value).strip())
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Entier attendu, reçu {value!r}.") from exc
    if kind == "real":
        try:
            return float(str(value).strip().replace(",", "."))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Nombre attendu, reçu {value!r}.") from exc
    if kind == "boolean":
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in ("true", "1", "oui", "vrai", "yes"):
            return True
        if text in ("false", "0", "non", "faux", "no"):
            return False
        raise ValueError(f"Booléen attendu, reçu {value!r}.")
    return _parse_date(value, with_time=(kind == "datetime"))


def coerce_record(record: dict, types: dict[str, str],
                  strict: bool = True) -> tuple[dict, list[str]]:
    """Convertit un dictionnaire d'attributs, champ par champ.

    En mode non strict, les champs inconnus de la couche sont ignorés avec un
    avertissement plutôt que de faire échouer tout le lot.
    """
    converted: dict[str, Any] = {}
    warnings: list[str] = []
    for key, value in (record or {}).items():
        if key not in types:
            message = f"Champ inconnu ignoré : {key}"
            if strict:
                raise ValueError(
                    f"Le champ « {key} » n'existe pas dans la couche. "
                    f"Champs disponibles : {', '.join(sorted(types)) or 'aucun'}."
                )
            warnings.append(message)
            continue
        converted[key] = coerce_value(value, types[key])
    return converted, warnings
