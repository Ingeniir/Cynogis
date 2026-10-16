"""Traitements longs sans geler QGIS. Python pur : testable sans QGIS.

Un outil qui lance des algorithmes Processing est un générateur : il cède une étape
(AlgCall) au lieu d'appeler Processing. L'exécuteur (tools/tasks.py) lance l'étape dans une
QgsTask et rappelle quand elle est finie, sur le thread principal ; le générateur reprend alors
avec les résultats. Entre deux étapes, la boucle d'événements de QGIS est libre.

Côté pont, la requête reçoit tout de suite un job_id ; le serveur MCP attend la fin en
interrogeant get_job_status. Un seul job à la fois.
"""
from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from typing import Any, Protocol

from .errors import ErrorCode, ToolError

RUNNING, DONE, FAILED, CANCELLED = "running", "done", "failed", "cancelled"
KEEP_FINISHED = 20  # jobs terminés gardés pour get_job_status


@dataclass(frozen=True)
class AlgCall:
    """Étape cédée par un outil : un algorithme Processing et ses paramètres."""

    algorithm_id: str
    params: dict[str, Any]


Done = Callable[[Any, "BaseException | None"], None]  # (résultats, erreur)


class Executor(Protocol):
    def start(self, step: AlgCall, done: Done) -> Any:
        """Lance l'étape et renvoie un handle ; done est appelé une fois, sur le thread
        principal, après le retour de start."""
        ...

    def progress(self, handle: Any) -> float:
        """Avancement de l'étape en cours, de 0 à 100."""
        ...

    def cancel(self, handle: Any) -> None: ...


Finisher = Callable[[Any, "BaseException | None"], Any]  # (résultat, erreur) → réponse finale


@dataclass
class Job:
    id: str
    tool: str
    generator: Generator[AlgCall, Any, Any]
    finisher: Finisher
    status: str = RUNNING
    step: int = 0
    algorithm: str = ""
    handle: Any = None
    response: Any = None   # réponse finale, fournie par finisher
    started: float = field(default_factory=time.monotonic)
    finished: float | None = None


class JobManager:
    def __init__(self, executor: Executor) -> None:
        self.executor = executor
        self._jobs: dict[str, Job] = {}

    @property
    def running(self) -> Job | None:
        return next((j for j in self._jobs.values() if j.status == RUNNING), None)

    def start(self, tool: str, generator: Generator[AlgCall, Any, Any], first: AlgCall,
              finisher: Finisher) -> Job:
        """Démarre un job dont le générateur vient de céder sa première étape."""
        job = Job(uuid.uuid4().hex[:12], tool, generator, finisher)
        self._jobs[job.id] = job
        self._prune()
        self._launch(job, first)
        return job

    def get(self, job_id: str) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise ToolError(ErrorCode.JOB_NOT_FOUND,
                            f"Traitement {job_id} inconnu (QGIS redémarré ?).")
        return job

    def status(self, job: Job) -> dict[str, Any]:
        progress = self.executor.progress(job.handle) if job.status == RUNNING else 100.0
        return {"job_id": job.id, "tool": job.tool, "status": job.status, "step": job.step,
                "algorithm": job.algorithm, "progress": round(progress, 1),
                "elapsed_s": round((job.finished or time.monotonic()) - job.started, 1)}

    def cancel(self, job: Job, reason: str = "Traitement annulé.") -> None:
        if job.status != RUNNING:
            return
        job.status = CANCELLED  # avant tout : un rappel tardif de l'exécuteur sera ignoré
        self.executor.cancel(job.handle)
        job.generator.close()
        self._finish(job, None, ToolError(ErrorCode.CANCELLED, reason), CANCELLED)

    def cancel_all(self, reason: str) -> None:
        for job in list(self._jobs.values()):
            self.cancel(job, reason)

    # --- Déroulement ---------------------------------------------------------------------
    def _launch(self, job: Job, step: Any) -> None:
        if not isinstance(step, AlgCall):
            self._advance(job, None, TypeError(f"Étape inattendue : {step!r}"))
            return
        job.step += 1
        job.algorithm = step.algorithm_id
        try:
            job.handle = self.executor.start(step, lambda v, e: self._advance(job, v, e))
        except Exception as exc:  # algorithme introuvable, paramètres refusés…
            self._advance(job, None, exc)

    def _advance(self, job: Job, value: Any, error: BaseException | None) -> None:
        if job.status != RUNNING:
            return
        try:
            step = job.generator.throw(error) if error else job.generator.send(value)
        except StopIteration as stop:
            self._finish(job, stop.value, None, DONE)
        except Exception as exc:
            self._finish(job, None, exc, FAILED)
        else:
            self._launch(job, step)

    def _finish(self, job: Job, result: Any, error: BaseException | None, status: str) -> None:
        job.status, job.finished, job.handle = status, time.monotonic(), None
        job.response = job.finisher(result, error)

    def _prune(self) -> None:
        finished = sorted((j for j in self._jobs.values() if j.finished is not None),
                          key=lambda j: j.finished or 0.0)
        for job in finished[:-KEEP_FINISHED]:
            del self._jobs[job.id]
