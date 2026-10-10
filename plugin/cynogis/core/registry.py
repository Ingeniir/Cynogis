"""Niveaux de permission, décorateur @tool et registre des outils. Python pur."""
from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from types import ModuleType
from typing import Any

from .schema import Param, object_schema


class Level(IntEnum):
    READ = 0      # lecture seule
    CREATE = 1    # crée de nouvelles données, ne touche pas l'existant
    MODIFY = 2    # tampon d'édition, validation humaine pour enregistrer
    DESTROY = 3   # irréversible, confirmation humaine obligatoire


LEVEL_LABELS = {
    Level.READ: "lecture seule",
    Level.CREATE: "crée de nouvelles données sans modifier l'existant",
    Level.MODIFY: "modifie dans le tampon d'édition ; un humain valide l'enregistrement",
    Level.DESTROY: "action irréversible ; confirmation humaine obligatoire",
}
_ATTR = "__cynogis_tool__"


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    level: Level
    params: dict[str, Param]
    handler: Callable[..., Any]
    internal: bool = False

    def listing(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": f"{self.description}\n\n[Niveau {int(self.level)} : "
                           f"{LEVEL_LABELS[self.level]}]",
            "level": int(self.level),
            "input_schema": object_schema(self.params),
        }


def tool(*, level: Level, params: dict[str, Param] | None = None, name: str | None = None,
         internal: bool = False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Déclare une fonction comme outil. La docstring sert de description pour l'IA."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        doc = inspect.cleandoc(fn.__doc__ or "")
        if not doc:
            raise ValueError(f"{fn.__name__} : docstring obligatoire (description pour l'IA)")
        spec_params = dict(params or {})
        signature = set(inspect.signature(fn).parameters)
        if signature != set(spec_params):
            raise ValueError(
                f"{fn.__name__} : paramètres déclarés {sorted(spec_params)} "
                f"≠ signature {sorted(signature)}")
        setattr(fn, _ATTR, ToolSpec(name or fn.__name__, doc, Level(level), spec_params, fn,
                                    internal))
        return fn

    return decorator


def spec_of(fn: Callable[..., Any]) -> ToolSpec:
    spec = getattr(fn, _ATTR, None)
    if not isinstance(spec, ToolSpec):
        raise ValueError(f"{fn!r} n'est pas décoré avec @tool")
    return spec


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def add(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Outil déjà enregistré : {spec.name}")
        self._tools[spec.name] = spec

    def register(self, *functions: Callable[..., Any]) -> None:
        for fn in functions:
            self.add(spec_of(fn))

    def register_module(self, module: ModuleType) -> int:
        """Enregistre toutes les fonctions @tool DÉFINIES dans le module."""
        count = 0
        for obj in vars(module).values():
            spec = getattr(obj, _ATTR, None)
            if isinstance(spec, ToolSpec) and getattr(obj, "__module__", None) == module.__name__:
                self.add(spec)
                count += 1
        if count == 0:  # ex. module resté en mémoire avec une ancienne classe ToolSpec
            raise ValueError(f"Aucun outil @tool trouvé dans {module.__name__}")
        return count

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    @property
    def names(self) -> list[str]:
        return sorted(n for n, s in self._tools.items() if not s.internal)

    def listing(self) -> list[dict[str, Any]]:
        return [self._tools[n].listing() for n in self.names]
