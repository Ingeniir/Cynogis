"""Exécution de la segmentation persistée dans une tâche QGIS."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qgis.core import QgsTask

from ..core.jobs import Done, SegmentLandcover
from ..core.landcover_execution import (
    SegmentationCancelledError,
    SegmentationControl,
)


class LandcoverSegmentationTask(QgsTask):
    """Exécute la persistance et transmet une seule terminaison au job."""

    def __init__(
        self,
        step: SegmentLandcover,
        done: Done,
        forget: Callable[[Any], None],
    ) -> None:
        if not isinstance(step, SegmentLandcover):
            raise TypeError("step doit être une SegmentLandcover.")
        super().__init__(f"Cynogis : {step.label}", QgsTask.Flag.CanCancel)
        self.step = step
        self.done = done
        self.forget = forget
        self.result: dict[str, Any] | None = None
        self.error: Exception | None = None
        self._delivered = False

    def run(self) -> bool:
        try:
            control = SegmentationControl(
                on_progress=self.setProgress,
                is_cancelled=self.isCanceled,
            )
            control.check_cancelled()

            # Chargement du moteur uniquement dans le worker.
            from ..landcover_processing.persist import persist_segmentation

            self.result = persist_segmentation(
                preparation_directory=self.step.preparation_directory,
                output_parent=self.step.output_parent,
                config=self.step.config,
                control=control,
            )
        except Exception as error:
            self.error = error
            return False
        return True

    def finished(self, success: bool) -> None:
        if self._delivered:
            return
        self._delivered = True

        try:
            self.forget(self)
        except Exception as cleanup_error:
            original = self.error
            message = (
                "Finalisation de la segmentation OBIA impossible : "
                f"{type(cleanup_error).__name__}: {cleanup_error}"
            )
            if original is not None:
                message += (
                    " ; erreur initiale du calcul : "
                    f"{type(original).__name__}: {original}"
                )
            combined = RuntimeError(message)
            combined.__cause__ = original if original is not None else cleanup_error
            self.error = combined

        if self.error is not None:
            self.done(None, self.error)
        elif self.isCanceled():
            # Conserver un éventuel manifeste complet après annulation tardive.
            self.done(
                self.result,
                SegmentationCancelledError("Segmentation OBIA annulée depuis QGIS."),
            )
        elif not success or self.result is None:
            self.done(
                None,
                RuntimeError("Segmentation terminée sans résultat ni erreur explicite."),
            )
        else:
            self.done(self.result, None)
