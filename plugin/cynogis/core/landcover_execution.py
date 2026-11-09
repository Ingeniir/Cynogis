"""Contrôle coopératif de l'exécution des traitements OBIA.

Les callbacks sont exécutés dans le thread qui effectue le traitement.
Ils ne doivent pas manipuler directement l'interface graphique.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


class PreparationCancelledError(Exception):
    """Annulation détectée avant la publication du résultat."""

@dataclass(frozen=True)
class PreparationControl:
    """Callbacks facultatifs de progression et d'annulation.

    on_progress :
        Reçoit un pourcentage de progression.

    is_cancelled :
        Retourne True lorsqu'une annulation est demandée.

    Une exception provenant d'un callback n'est pas ignorée :
    elle fait échouer le traitement et déclenche son nettoyage.
    """

    on_progress: Callable[[float], None] | None = None
    is_cancelled: Callable[[], bool] | None = None

    def check_cancelled(self) -> None:
        if self.is_cancelled is not None and self.is_cancelled():
            raise PreparationCancelledError("Préparation OBIA annulée.")

    def checkpoint(self, progress: float) -> None:
        """Contrôle l'annulation avant et après la notification."""
        self.check_cancelled()

        if self.on_progress is not None:
            self.on_progress(float(progress))

        # Une annulation peut arriver pendant le callback
        self.check_cancelled()
