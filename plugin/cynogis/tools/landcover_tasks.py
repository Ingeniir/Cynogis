"""Exécution de la préparation OBIA dans une tâche QGIS."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qgis.core import QgsTask

from ..core.jobs import Done, PrepareLandcover
from ..core.landcover_execution import (
    PreparationCancelledError,
    PreparationControl,
)


class LandcoverPreparationTask(QgsTask):
    """Calcule hors du thread principal et rappelle le job une seule fois."""

    def __init__(
            self,
            step: PrepareLandcover,
            done: Done,
            forget: Callable[[Any], None],
    ) -> None:
        super().__init__(f"Cynogis : {step.label}", QgsTask.Flag.CanCancel)

        self.step = step
        self.done = done
        self.forget = forget
        self.result: dict | None = None
        self.error: Exception | None = None
        self._delivered = False

    def run(self) -> bool:
        try:
            control = PreparationControl(
                on_progress=self.setProgress,
                is_cancelled=self.isCanceled
            )
            control.check_cancelled()

            # Import tardif: démarrer le plugin ne doit pas importer
            # automatiquement GDAL et NumPy pour cette fonctionnalité.
            from ..landcover_processing.prepare import prepare_native_inputs

            self.result = prepare_native_inputs(
                raster_path=self.step.raster_path,
                aoi_wkb=self.step.aoi_wkb,
                aoi_crs_wkt=self.step.aoi_crs_wkt,
                rgb_bands=list(self.step.rgb_bands),
                output_parent=self.step.output_parent,
                config=self.step.config,
                control=control,
            )
            return True

        except Exception as exc:
            self.error = exc
            return False

    def finished(self, success: bool) -> None:
        if self._delivered:
            return

        self._delivered = True
        self.forget(self)

        # Une erreur technique reste prioritaire sur le drapeau d'annulation.
        if self.error is not None:
            self.done(None, self.error)
            return

        if self.isCanceled():
            # Peut concerner une tâche annulée avant run(), ou juste après
            # la production d'un résultat complet.
            self.done(
                self.result,
                PreparationCancelledError(
                    "Préparation OBIA annulée depuis QGIS."
                ),
            )
            return

        if not success or self.result is None:
            self.done(
                None,
                RuntimeError(
                    "La tâche OBIA s'est terminée sans résultat ni erreur explicite."
                ),
            )
            return

        self.done(self.result, None)
