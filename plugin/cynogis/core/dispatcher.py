"""Routage + validation + permissions + audit. Python pur : testable sans QGIS."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from ..bridge.protocol import Request, Response
from .audit import AuditLog
from .errors import ErrorCode, ToolError
from .policy import PermissionPolicy
from .registry import Level, ToolRegistry, ToolSpec
from .schema import Param, validate_params

logger = logging.getLogger("cynogis.dispatcher")


@dataclass
class ToolResult:
    data: Any
    warnings: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)  # couches/fichiers créés (pour l'audit)


class Dispatcher:
    def __init__(self, registry: ToolRegistry, policy: PermissionPolicy | None = None,
                 audit: AuditLog | None = None) -> None:
        self.registry = registry
        self.policy = policy or PermissionPolicy()
        self.audit = audit
        registry.add(ToolSpec("list_tools", "Catalogue interne des outils.", Level.READ, {},
                              self._list_tools, internal=True))
        if audit is not None:
            registry.add(ToolSpec(
                "get_audit_log",
                "Dernières actions exécutées dans QGIS via Cynogis (journal d'audit) : outil, "
                "paramètres, succès ou code d'erreur, couches créées.",
                Level.READ,
                {"limit": Param("integer", "Nombre d'entrées (les plus récentes d'abord).",
                                required=False, default=20, minimum=1, maximum=200),
                 "tool": Param("string", "Ne garder que cet outil.", required=False)},
                self._get_audit_log))

    def _list_tools(self) -> dict[str, Any]:
        return {"tools": self.registry.listing()}

    def _get_audit_log(self, limit: int, tool: str | None) -> dict[str, Any]:
        assert self.audit is not None
        return {"entries": self.audit.recent(limit, tool)}

    def dispatch(self, request: Request) -> Response:
        spec = self.registry.get(request.method)
        if spec is None:
            return Response.failure(request.id, ToolError(
                ErrorCode.UNKNOWN_METHOD, f"Outil inconnu : {request.method}",
                {"available": self.registry.names}))
        started = time.perf_counter()
        response, outputs = self._execute(spec, request)
        if self.audit is not None and not spec.internal:
            response.audit_id = self.audit.record(
                tool=spec.name, level=int(spec.level), params=request.params, ok=response.ok,
                error_code=(response.error or {}).get("code"),
                duration_ms=(time.perf_counter() - started) * 1000, outputs=outputs)
        return response

    def _execute(self, spec: ToolSpec, request: Request) -> tuple[Response, list[str]]:
        try:
            params = validate_params(spec.params, request.params)
            self.policy.check(spec, params)
            result = spec.handler(**params)
        except ToolError as err:
            return Response.failure(request.id, err), []
        except Exception as exc:  # filet de sécurité : QGIS ne doit jamais planter
            logger.exception("Erreur interne dans %s", spec.name)
            return Response.failure(request.id, ToolError(
                ErrorCode.INTERNAL_ERROR, f"{type(exc).__name__}: {exc}")), []
        if isinstance(result, ToolResult):
            return (Response(id=request.id, ok=True, data=result.data, warnings=result.warnings),
                    result.outputs)
        return Response(id=request.id, ok=True, data=result), []
