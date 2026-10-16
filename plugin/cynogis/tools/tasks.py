"""Exécuteur des étapes des jobs (core/jobs.py) : algorithmes Processing et téléchargements.

Par défaut, l'algorithme tourne dans une QgsProcessingAlgRunnerTask (thread de QGIS, visible
et annulable dans la barre des tâches) : l'interface reste utilisable. Préparation et
post-traitement restent sur le thread principal (executed y est émis).

Repli sur le thread principal, avec l'interface repeinte pendant le calcul (saisies ignorées) :
- algorithme marqué NoThreading par QGIS ;
- couche d'entrée en cours d'édition (la lire depuis un autre thread risque la corruption).

Téléchargement (Fetch) : QgsBlockingNetworkRequest (proxy, certificats, authcfg de
l'utilisateur) dans une QgsTask, décodage GeoJSON compris.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from qgis import processing
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsBlockingNetworkRequest,
    QgsFeedback,
    QgsJsonUtils,
    QgsMapLayer,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProject,
    QgsTask,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QTimer, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from ..compat import EXCLUDE_USER_INPUT
from ..core.errors import ErrorCode, ToolError
from ..core.jobs import AlgCall, Done, Fetch

PUMP_INTERVAL_S = 0.1  # repli synchrone : repeindre l'interface au plus toutes les 100 ms
logger = logging.getLogger("cynogis.tasks")
_NO_ERROR = getattr(QgsBlockingNetworkRequest, "ErrorCode", QgsBlockingNetworkRequest).NoError


@dataclass(eq=False)
class _Handle:
    step: AlgCall
    context: QgsProcessingContext
    feedback: QgsProcessingFeedback
    done: Done
    cancelled: bool = False


class ProcessingExecutor:
    def __init__(self) -> None:
        # La tâche garde des pointeurs vers context et feedback : les garder en vie jusqu'à
        # executed, même après une annulation.
        self._active: set[_Handle] = set()

    def start(self, step: AlgCall | Fetch, done: Done) -> _Handle | _FetchTask:
        if isinstance(step, Fetch):
            task = _FetchTask(step, done, self._active.discard)
            self._active.add(task)  # garder l'objet Python de la tâche jusqu'à finished
            QgsApplication.taskManager().addTask(task)
            return task
        algorithm = QgsApplication.processingRegistry().createAlgorithmById(step.algorithm_id)
        if algorithm is None:
            raise ToolError(ErrorCode.ALGORITHM_NOT_ALLOWED,
                            f"Algorithme {step.algorithm_id} indisponible.")
        context = QgsProcessingContext()
        context.setProject(QgsProject.instance())
        ok, message = algorithm.checkParameterValues(step.params, context)
        if not ok:
            raise ToolError(ErrorCode.PROCESSING_FAILED, f"{step.algorithm_id} : {message}")
        handle = _Handle(step, context, QgsProcessingFeedback(), done)
        self._active.add(handle)
        if _needs_main_thread(algorithm, step.params):
            logger.info("%s : exécution sur le thread principal", step.algorithm_id)
            QTimer.singleShot(0, lambda: self._run_here(handle))
        else:
            task = QgsProcessingAlgRunnerTask(algorithm, step.params, context, handle.feedback)
            task.setDescription(f"Cynogis : {algorithm.displayName()}")
            task.executed.connect(lambda success, results: self._finish(handle, success, results))
            QgsApplication.taskManager().addTask(task)
        return handle

    def progress(self, handle: _Handle | _FetchTask | None) -> float:
        return float(handle.feedback.progress()) if handle is not None else 0.0

    def pause(self, resume: Callable[[], None]) -> None:
        QTimer.singleShot(0, resume)  # après l'affichage et les requêtes en attente

    def cancel(self, handle: _Handle | _FetchTask | None) -> None:
        if handle is not None and not handle.cancelled:
            handle.cancelled = True
            handle.feedback.cancel()  # la tâche s'arrête et se termine en échec

    # --- Fin d'étape (thread principal) ----------------------------------------------------
    def _run_here(self, handle: _Handle) -> None:
        if handle.cancelled:
            self._finish(handle, False, {})
            return
        last = [0.0]

        def pump(_progress: float) -> None:
            now = time.monotonic()
            if now - last[0] >= PUMP_INTERVAL_S:
                last[0] = now
                QCoreApplication.processEvents(EXCLUDE_USER_INPUT)

        handle.feedback.progressChanged.connect(pump)
        try:
            results = processing.run(handle.step.algorithm_id, handle.step.params,
                                     context=handle.context, feedback=handle.feedback)
        except QgsProcessingException:
            self._finish(handle, False, {})
        else:
            self._finish(handle, True, results, taken=True)
        finally:
            handle.feedback.progressChanged.disconnect(pump)

    def _finish(self, handle: _Handle, success: bool, results: dict[str, Any],
                taken: bool = False) -> None:
        self._active.discard(handle)
        if handle.cancelled:
            return  # le job est déjà clos
        if handle.feedback.isCanceled():  # annulé depuis la barre des tâches de QGIS
            handle.done(None, ToolError(ErrorCode.CANCELLED,
                                        "Traitement annulé par l'utilisateur dans QGIS."))
            return
        if not success:
            handle.done(None, ToolError(
                ErrorCode.PROCESSING_FAILED, f"{handle.step.algorithm_id} : échec du traitement.",
                {"log": handle.feedback.textLog()[-2000:]}))
            return
        handle.done(dict(results) if taken else _take_layers(handle.context, results), None)


def _take_layers(context: QgsProcessingContext, results: dict[str, Any]) -> dict[str, Any]:
    """Comme processing.run : les couches temporaires (memory:) passent du contexte à
    l'appelant, sinon elles disparaissent avec lui."""
    store = context.temporaryLayerStore()
    return {key: context.takeResultLayer(value)
            if isinstance(value, str) and store.mapLayer(value) is not None else value
            for key, value in results.items()}


def _needs_main_thread(algorithm: Any, params: dict[str, Any]) -> bool:
    if algorithm.flags() & Qgis.ProcessingAlgorithmFlag.NoThreading:
        return True
    return any(isinstance(layer, QgsVectorLayer) and layer.isEditable()
               for layer in _input_layers(params))


def _input_layers(params: dict[str, Any]) -> Iterator[QgsMapLayer]:
    project = QgsProject.instance()
    for value in params.values():
        for item in value if isinstance(value, (list, tuple)) else (value,):
            if isinstance(item, QgsMapLayer):
                yield item
            elif isinstance(item, str) and (layer := project.mapLayer(item)) is not None:
                yield layer


class _FetchTask(QgsTask):
    """GET hors du thread principal ; finished (thread principal) rappelle le job."""

    def __init__(self, step: Fetch, done: Done, forget: Callable[[Any], None]) -> None:
        super().__init__(f"Cynogis : {step.label}", QgsTask.Flag.CanCancel)
        self.step, self.done, self.forget = step, done, forget
        self.feedback = QgsFeedback()
        self.cancelled = False  # annulé par le job : ne plus le rappeler
        self.result: Any = None
        self.error = ""

    def run(self) -> bool:
        request = QgsBlockingNetworkRequest()
        if self.step.authcfg:
            request.setAuthCfg(self.step.authcfg)
        if request.get(QNetworkRequest(QUrl(self.step.url)), False, self.feedback) != _NO_ERROR:
            self.error = request.errorMessage()
            return False
        content = bytes(request.reply().content())
        if not self.step.geojson:
            self.result = content
            return True
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            self.error = f"réponse illisible ({exc})"
            return False
        fields = QgsJsonUtils.stringToFields(text)
        self.result = (fields, QgsJsonUtils.stringToFeatureList(text, fields))
        return True

    def cancel(self) -> None:  # bouton Annuler de la barre des tâches
        self.feedback.cancel()
        super().cancel()

    def finished(self, success: bool) -> None:
        self.forget(self)
        if self.cancelled:
            return
        if self.feedback.isCanceled():
            self.done(None, ToolError(ErrorCode.CANCELLED,
                                      "Téléchargement annulé par l'utilisateur dans QGIS."))
        elif not success:
            self.done(None, ToolError(ErrorCode.NETWORK_ERROR,
                                      f"Service injoignable : {self.error or 'erreur inconnue'}",
                                      {"url": self.step.url}))
        else:
            self.done(self.result, None)
