"""Description et validation des paramètres d'outils. Python pur, sans dépendance."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from .errors import ErrorCode, ToolError

_JSON_TYPES: dict[str, type | tuple[type, ...]] = {
    "string": str, "integer": int, "number": (int, float),
    "boolean": bool, "array": list, "object": dict,
}
_MISSING = object()


@dataclass(frozen=True)
class Param:
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: tuple[Any, ...] | None = None
    minimum: float | None = None
    maximum: float | None = None
    items: str | None = None

    def __post_init__(self) -> None:
        if self.type not in _JSON_TYPES:
            raise ValueError(f"Type de paramètre inconnu : {self.type}")
        if self.items is not None and self.items not in _JSON_TYPES:
            raise ValueError(f"Type d'élément inconnu : {self.items}")

    def json_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {"type": self.type, "description": self.description}
        if self.enum is not None:
            schema["enum"] = list(self.enum)
        if self.minimum is not None:
            schema["minimum"] = self.minimum
        if self.maximum is not None:
            schema["maximum"] = self.maximum
        if self.type == "array":
            schema["items"] = {"type": self.items} if self.items else {}
        if not self.required and self.default is not None:
            schema["default"] = self.default
        return schema


def _type_ok(value: Any, type_name: str) -> bool:
    if isinstance(value, bool) and type_name in ("integer", "number"):
        return False  # en Python, True est un int : on refuse
    return isinstance(value, _JSON_TYPES[type_name])


def _check(name: str, p: Param, value: Any) -> str | None:
    if not _type_ok(value, p.type):
        return f"{name} : type {p.type} attendu, reçu {type(value).__name__}"
    if p.enum is not None and value not in p.enum:
        return f"{name} : valeur {value!r} non autorisée (choix : {', '.join(map(str, p.enum))})"
    if p.type in ("integer", "number"):
        if p.minimum is not None and value < p.minimum:
            return f"{name} : {value} < minimum {p.minimum}"
        if p.maximum is not None and value > p.maximum:
            return f"{name} : {value} > maximum {p.maximum}"
    if p.type == "array" and p.items:
        bad = [i for i, v in enumerate(value) if not _type_ok(v, p.items)]
        if bad:
            return f"{name} : éléments de type {p.items} attendus (indices {bad[:5]})"
    return None


def validate_params(spec: dict[str, Param], raw: dict[str, Any]) -> dict[str, Any]:
    """Renvoie les paramètres nettoyés (avec les valeurs par défaut) ou lève INVALID_PARAMS."""
    errors: list[str] = []
    unknown = sorted(set(raw) - set(spec))
    if unknown:
        errors.append(f"paramètres inconnus : {', '.join(unknown)}")
    clean: dict[str, Any] = {}
    for name, p in spec.items():
        value = raw.get(name, _MISSING)
        if value is _MISSING or value is None:
            if p.required:
                errors.append(f"{name} : paramètre obligatoire")
            else:
                clean[name] = copy.deepcopy(p.default)
            continue
        if p.type == "integer" and isinstance(value, float) and value.is_integer():
            value = int(value)  # 10.0 → 10
        err = _check(name, p, value)
        if err:
            errors.append(err)
        else:
            clean[name] = value
    if errors:
        raise ToolError(
            ErrorCode.INVALID_PARAMS,
            "Paramètres invalides : " + " ; ".join(errors),
            {"errors": errors, "expected": object_schema(spec)},
        )
    return clean


def object_schema(spec: dict[str, Param]) -> dict[str, Any]:
    """Schéma JSON (inputSchema MCP) d'un ensemble de paramètres."""
    return {
        "type": "object",
        "properties": {n: p.json_schema() for n, p in spec.items()},
        "required": [n for n, p in spec.items() if p.required],
        "additionalProperties": False,
    }
