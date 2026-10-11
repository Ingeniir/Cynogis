"""Contrôle des permissions par niveau. Python pur."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .errors import ErrorCode, ToolError
from .registry import Level, ToolSpec

Confirmer = Callable[[ToolSpec, dict[str, Any]], bool]


@dataclass
class PermissionPolicy:
    max_level: Level = Level.DESTROY
    confirm: Confirmer | None = None

    def check(self, spec: ToolSpec, params: dict[str, Any]) -> None:
        if spec.level > self.max_level:
            raise ToolError(
                ErrorCode.PERMISSION_DENIED,
                f"L'outil {spec.name} (niveau {int(spec.level)}) dépasse le niveau autorisé "
                f"({int(self.max_level)}). Demande à l'utilisateur de le faire lui-même.")
        if spec.level >= Level.DESTROY and (self.confirm is None or not self.confirm(spec, params)):
            raise ToolError(ErrorCode.PERMISSION_DENIED,
                            f"Action {spec.name} refusée par l'utilisateur. Ne pas réessayer "
                            "sans lui demander.")
