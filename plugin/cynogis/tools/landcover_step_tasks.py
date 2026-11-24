"""Caractéristiques et délimitation OBIA exécutées dans une tâche QGIS.

Mêmes règles de terminaison que LandcoverSegmentationTask : une seule remise au job,
erreur technique prioritaire sur l'annulation, résultat complet conservé après une
annulation tardive.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qgis.core import QgsTask

from ..core.jobs import DelineateLandcover, Done, ExtractLandcoverFeatures
from ..core.landcover_execution import (
    DelineationCancelledError,
    DelineationControl,
    FeatureExtractionCancelledError,
    FeatureExtractionControl,
)


def _run_features(step: ExtractLandcoverFeatures, control) -> dict[str, Any]:
    from ..landcover_processing.persist_features import persist_object_features

    return persist_object_features(
        preparation_directory=step.preparation_directory,
        segmentation_directory=step.segmentation_directory,
        output_parent=step.output_parent,
        control=control,
    )


def _run_delineation(step: DelineateLandcover, control) -> dict[str, Any]:
    from ..landcover_processing.delineate import persist_delineation

    return persist_delineation(
        preparation_directory=step.preparation_directory,
        segmentation_directory=step.segmentation_directory,
        features_directory=step.features_directory,
        output_parent=step.output_parent,
        config=step.config,
        control=control,
    )


# Type d'étape → (contrôle, annulation, exécution). Moteurs importés dans le worker.
_KINDS = {
    ExtractLandcoverFeatures: (
        FeatureExtractionControl, FeatureExtractionCancelledError, _run_features),
    DelineateLandcover: (DelineationControl, DelineationCancelledError, _run_delineation),
}


class LandcoverStepTask(QgsTask):
    """Exécute l'étape hors du thread principal et rappelle le job une seule fois."""

    def __init__(
        self,
        step: ExtractLandcoverFeatures | DelineateLandcover,
        done: Done,
        forget: Callable[[Any], None],
    ) -> None:
        kind = _KINDS.get(type(step))
        if kind is None:
            raise TypeError(f"Étape OBIA non prise en charge : {type(step).__name__}.")
        super().__init__(f"Cynogis : {step.label}", QgsTask.Flag.CanCancel)
        self.step = step
        self.done = done
        self.forget = forget
        self._control_type, self._cancelled_type, self._run = kind
        self.result: dict[str, Any] | None = None
        self.error: Exception | None = None
        self._delivered = False

    def run(self) -> bool:
        try:
            control = self._control_type(
                on_progress=self.setProgress, is_cancelled=self.isCanceled)
            control.check_cancelled()
            self.result = self._run(self.step, control)
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
                f"Finalisation impossible ({self.step.label}) : "
                f"{type(cleanup_error).__name__}: {cleanup_error}"
            )
            if original is not None:
                message += (
                    f" ; erreur initiale du calcul : {type(original).__name__}: {original}"
                )
            combined = RuntimeError(message)
            combined.__cause__ = original if original is not None else cleanup_error
            self.error = combined

        if self.error is not None:
            self.done(None, self.error)
        elif self.isCanceled():
            # Conserver un éventuel manifeste complet après annulation tardive.
            self.done(self.result,
                      self._cancelled_type(f"{self.step.label} annulée depuis QGIS."))
        elif not success or self.result is None:
            self.done(None, RuntimeError(
                f"{self.step.label} : tâche terminée sans résultat ni erreur explicite."))
        else:
            self.done(self.result, None)
