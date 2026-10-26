"""Traitements longs sans geler QGIS. Python pur : testable sans QGIS.

Un outil qui lance des algorithmes Processing ou télécharge est un générateur : il cède une
étape (AlgCall, Fetch) au lieu d'appeler Processing ou le réseau. L'exécuteur (tools/tasks.py)
lance l'étape dans une QgsTask et rappelle quand elle est finie, sur le thread principal ; le
générateur reprend alors avec les résultats. Entre deux étapes, la boucle d'événements de
QGIS est libre.

Une boucle Python longue cède des Pause (via Pacer) : la boucle d'événements traite ce qui
attend (affichage, requêtes du pont) puis la boucle reprend. Un outil qui cède une Pause est
un job comme un autre.

Côté pont, la requête reçoit tout de suite un job_id ; le serveur MCP attend la fin en
interrogeant get_job_status. Un seul job à la fois.
"""
from __future__ import annotations

import time
import uuid
from collections import Counter
from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol

from .errors import ErrorCode, ToolError

RUNNING, DONE, FAILED, CANCELLED = "running", "done", "failed", "cancelled"
KEEP_FINISHED = 20  # jobs terminés gardés pour get_job_status
PAUSE_INTERVAL_S = 0.1  # une boucle Python rend la main au plus toutes les 100 ms


@dataclass(frozen=True)
class AlgCall:
    """Étape cédée par un outil : un algorithme Processing et ses paramètres."""

    algorithm_id: str
    params: dict[str, Any]


@dataclass(frozen=True)
class Fetch:
    """Étape cédée par un outil : téléchargement HTTP GET (gestionnaire réseau de QGIS).
    Résultat : le contenu (bytes), ou (champs, entités) si geojson."""

    url: str
    authcfg: str | None = None
    label: str = "téléchargement"
    geojson: bool = False


@dataclass(frozen=True)
class Pause:
    """Étape cédée par une boucle Python : rendre la main à la boucle d'événements."""

    label: str
    progress: float | None = None  # 0 à 100 si le total est connu


class Pacer:
    """Points de pause d'une boucle : « yield from pace(i) » cède une Pause si la dernière
    date de plus de interval_s, sinon ne fait rien (coût : une lecture d'horloge)."""

    def __init__(self, label: str, total: int | None = None,
                 interval_s: float = PAUSE_INTERVAL_S) -> None:
        self.label, self.total, self.interval_s = label, total, interval_s
        self._last = time.monotonic()

    def __call__(self, done: int | None = None) -> Generator[Pause, Any, None]:
        if time.monotonic() - self._last < self.interval_s:
            return
        progress = 100.0 * done / self.total if self.total and done is not None else None
        yield Pause(self.label, progress)
        self._last = time.monotonic()


def run_now(steps: Generator[Pause, Any, Any]) -> Any:
    """Déroule d'un coup un générateur qui ne cède que des Pause (appel hors job, sur un
    volume borné), et renvoie son résultat."""
    try:
        while True:
            step = next(steps)
            if not isinstance(step, Pause):
                raise TypeError(f"Étape inattendue hors job : {step!r}")
    except StopIteration as stop:
        return stop.value


# --- Notes d'exécution ---------------------------------------------------------------------
# Un helper partagé (ex. area_m2) signale un fait sans le faire remonter à la main : le
# dispatcher rattache les notes à l'appel en cours (ou à son job) et les ajoute aux warnings.
_notes: Counter[str] | None = None


def note(template: str) -> None:
    """Note à reporter en avertissement ; {n} dans template = nombre d'occurrences.
    Hors appel d'outil (console, script), ne fait rien."""
    if _notes is not None:
        _notes[template] += 1


@contextmanager
def collecting(notes: Counter[str]) -> Iterator[None]:
    """Rattache les note() du code exécuté dans le bloc à notes (imbrication possible)."""
    global _notes
    previous, _notes = _notes, notes
    try:
        yield
    finally:
        _notes = previous


def render_notes(notes: Counter[str]) -> list[str]:
    return [template.format(n=n) for template, n in notes.items()]


Step = AlgCall | Fetch | Pause
# Type de retour des outils et helpers qui cèdent des étapes (appel avec « yield from »).
Steps = Generator[Step, Any, Any]
Done = Callable[[Any, "BaseException | None"], None]  # (résultats, erreur)


class Executor(Protocol):
    def start(self, step: AlgCall | Fetch, done: Done) -> Any:
        """Lance l'étape et renvoie un handle ; done est appelé une fois, sur le thread
        principal, après le retour de start."""
        ...

    def progress(self, handle: Any) -> float:
        """Avancement de l'étape en cours, de 0 à 100."""
        ...

    def cancel(self, handle: Any) -> None: ...

    def pause(self, resume: Callable[[], None]) -> None:
        """Appelle resume depuis la boucle d'événements, une fois ce qui attend traité."""
        ...


Finisher = Callable[[Any, "BaseException | None"], Any]  # (résultat, erreur) → réponse finale


@dataclass
class Job:
    id: str
    tool: str
    generator: Generator[Step, Any, Any]
    finisher: Finisher
    status: str = RUNNING
    step: int = 0
    algorithm: str = ""
    handle: Any = None     # étape Processing en cours, None pendant une boucle Python
    progress: float | None = None  # avancement annoncé par la dernière Pause
    response: Any = None   # réponse finale, fournie par finisher
    notes: Counter[str] = field(default_factory=Counter)  # note() du générateur
    started: float = field(default_factory=time.monotonic)
    finished: float | None = None


class JobManager:
    def __init__(self, executor: Executor) -> None:
        self.executor = executor
        self._jobs: dict[str, Job] = {}

    @property
    def running(self) -> Job | None:
        return next((j for j in self._jobs.values() if j.status == RUNNING), None)

    def start(self, tool: str, generator: Generator[Step, Any, Any], first: Step,
              finisher: Finisher, notes: Counter[str] | None = None) -> Job:
        """Démarre un job dont le générateur vient de céder sa première étape ; notes
        reçoit les note() de la suite du générateur."""
        job = Job(uuid.uuid4().hex[:12], tool, generator, finisher,
                  notes=Counter() if notes is None else notes)
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
        if job.status != RUNNING:
            progress = 100.0
        elif job.handle is not None:
            progress = self.executor.progress(job.handle)
        else:
            progress = job.progress or 0.0
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
        if isinstance(step, Pause):
            job.algorithm, job.progress, job.handle = step.label, step.progress, None
            self.executor.pause(lambda: self._advance(job, None, None))
            return
        if not isinstance(step, (AlgCall, Fetch)):
            self._advance(job, None, TypeError(f"Étape inattendue : {step!r}"))
            return
        job.step += 1
        job.algorithm = step.algorithm_id if isinstance(step, AlgCall) else step.label
        job.progress = None
        try:
            job.handle = self.executor.start(step, lambda v, e: self._advance(job, v, e))
        except Exception as exc:  # algorithme introuvable, paramètres refusés…
            self._advance(job, None, exc)

    def _advance(self, job: Job, value: Any, error: BaseException | None) -> None:
        if job.status != RUNNING:
            return
        try:
            with collecting(job.notes):
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
