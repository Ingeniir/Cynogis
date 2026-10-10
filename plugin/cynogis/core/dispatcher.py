"""Routage méthode -> fonction. Python pur : testable sans QGIS."""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..bridge.protocol import Request, Response
from .errors import ErrorCode, ToolError

logger = logging.getLogger("cynogis.dispatcher")
Handler = Callable[[dict[str, Any]], Any]

@dataclass
class ToolResult:
    data: Any
    warnings: list[str] = field(default_factory=list)

class Dispatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, name: str, handler: Handler) -> None:
        if name in self._handlers:
            raise ValueError(f"Méthode déjà enregistrée : {name}")
        self._handlers[name] = handler

    @property
    def methods(self) -> list[str]:
        return sorted(self._handlers)

    def dispatch(self, request: Request) -> Response:
        handler = self._handlers.get(request.method)
        if handler is None:
            err = ToolError(ErrorCode.UNKNOWN_METHOD, f"Méthode inconnue : {request.method}", {"available": self.methods})
            return Response.failure(request.id, err)
        try:
            result = handler(request.params)
        except ToolError as err:
            return Response.failure(request.id, err)
        except Exception as exc:
            logger.exception("Erreur interne dans %s", request.method)
            err = ToolError(ErrorCode.INTERNAL_ERROR, f"{type(exc).__name__}: {exc}")
            return Response.failure(request.id, err)

        if isinstance(result, ToolResult):
            return Response(id=request.id, ok=True, data=result.data, warnings=result.warnings)

        return Response(id=request.id, ok=True, data=result)
