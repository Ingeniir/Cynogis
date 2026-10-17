"""Routage + validation + permissions + audit. Python pur : testable sans QGIS."""
from __future__ import annotations

import dataclasses
import inspect
import logging
import time
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any

from ..bridge.protocol import Request, Response
from .audit import AuditLog
from .errors import ErrorCode, ToolError
from .jobs import RUNNING, Executor, JobManager
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
                 audit: AuditLog | None = None, executor: Executor | None = None) -> None:
        self.registry = registry
        self.policy = policy or PermissionPolicy()
        self.audit = audit
        self.jobs = JobManager(executor) if executor is not None else None
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
        if self.jobs is not None:  # appelés par le serveur MCP, invisibles pour l'IA
            job_id = {"job_id": Param("string", "Identifiant du traitement.")}
            registry.add(ToolSpec("get_job_status", "Avancement ou résultat d'un traitement.",
                                  Level.READ, job_id, self._get_job_status, internal=True))
            registry.add(ToolSpec("cancel_job", "Annule un traitement en cours.",
                                  Level.READ, job_id, self._cancel_job, internal=True))

    def _list_tools(self) -> dict[str, Any]:
        return {"tools": self.registry.listing()}

    def _get_audit_log(self, limit: int, tool: str | None) -> dict[str, Any]:
        assert self.audit is not None
        return {"entries": self.audit.recent(limit, tool)}

    def _get_job_status(self, job_id: str) -> Response:
        assert self.jobs is not None
        job = self.jobs.get(job_id)
        if job.status == RUNNING:
            return Response(id=None, ok=True, data=self.jobs.status(job), job_id=job.id)
        return job.response  # réponse finale de l'outil, déjà auditée

    def _cancel_job(self, job_id: str) -> dict[str, Any]:
        assert self.jobs is not None
        job = self.jobs.get(job_id)
        self.jobs.cancel(job)
        return self.jobs.status(job)

    def dispatch(self, request: Request) -> Response:
        spec = self.registry.get(request.method)
        if spec is None:
            return Response.failure(request.id, ToolError(
                ErrorCode.UNKNOWN_METHOD, f"Outil inconnu : {request.method}",
                {"available": self.registry.names}))
        started = time.perf_counter()

        def finish(result: Any, error: BaseException | None) -> Response:
            response, outputs = self._to_response(request.id, spec, result, error)
            if self.audit is not None and not spec.internal:
                response.audit_id = self.audit.record(
                    tool=spec.name, level=int(spec.level), params=request.params,
                    ok=response.ok, error_code=(response.error or {}).get("code"),
                    duration_ms=(time.perf_counter() - started) * 1000, outputs=outputs)
            return response

        try:
            self._check_busy(spec)
            params = validate_params(spec.params, request.params)
            self.policy.check(spec, params)
            self._check_busy(spec)  # un job a pu démarrer pendant la fenêtre de confirmation
            result = spec.handler(**params)
            if inspect.isgenerator(result):
                return self._start_job(spec, request, result, finish)
        except Exception as exc:  # filet de sécurité : QGIS ne doit jamais planter
            return finish(None, exc)
        return finish(result, None)

    def _check_busy(self, spec: ToolSpec) -> None:
        """Pendant un traitement, seules les lectures passent : rien ne doit modifier le
        projet sous les pieds de l'algorithme."""
        job = self.jobs.running if self.jobs is not None else None
        if job is not None and spec.level > Level.READ:
            raise ToolError(ErrorCode.BUSY,
                            f"Traitement {job.tool} en cours (job {job.id}) : attendre sa fin "
                            f"avant de lancer {spec.name}.")

    def _start_job(self, spec: ToolSpec, request: Request, generator: Generator[Any, Any, Any],
                   finish: Any) -> Response:
        """Outil générateur : le code jusqu'à la première étape Processing s'exécute ici ;
        la suite devient un job et la réponse part tout de suite avec son job_id."""
        try:
            first = next(generator)
        except StopIteration as stop:  # aucune étape Processing : réponse immédiate
            return finish(stop.value, None)
        if self.jobs is None:
            generator.close()
            raise ToolError(ErrorCode.INTERNAL_ERROR, "Aucun exécuteur de traitements.")
        job = self.jobs.start(spec.name, generator, first, finish)
        if job.response is not None:  # échec dès le lancement
            return job.response
        return Response(id=request.id, ok=True, data=self.jobs.status(job), job_id=job.id)

    @staticmethod
    def _to_response(request_id: str, spec: ToolSpec, result: Any,
                     error: BaseException | None) -> tuple[Response, list[str]]:
        if isinstance(error, ToolError):
            return Response.failure(request_id, error), []
        if error is not None:
            logger.error("Erreur interne dans %s", spec.name, exc_info=error)
            return Response.failure(request_id, ToolError(
                ErrorCode.INTERNAL_ERROR, f"{type(error).__name__}: {error}")), []
        if isinstance(result, Response):  # get_job_status : réponse finale d'un job
            return dataclasses.replace(result, id=request_id), []
        if isinstance(result, ToolResult):
            return (Response(id=request_id, ok=True, data=result.data, warnings=result.warnings),
                    result.outputs)
        return Response(id=request_id, ok=True, data=result), []
