"""Exécute des opérations de nettoyage indépendantes.

Une erreur ordinaire ne doit pas empêcher les opérations suivantes.
Aucune dépendance QGIS ou Qt.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable

logger = logging.getLogger(__name__)

CleanupStep = tuple[str, Callable[[], object]]
CleanupFailure = tuple[str, Exception]

def run_cleanup_steps(
        steps: Iterable[CleanupStep],
) -> list[CleanupFailure]:
    """Tente chaque étape et retourne les erreurs rencontrées.

    Les erreurs sont journalisées avec leur traceback.
    KeyboardInterrupt et SystemExit ne sont pas interceptés.
    """
    failures: list[CleanupFailure] = []

    for label, operation in steps:
        try:
            operation()
        except Exception as exc:
            failures.append((label, exc))
            logger.exception("Échec du nettoyage : %s", label)

    return failures
