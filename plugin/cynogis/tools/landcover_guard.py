"""Exclusion des préparations OBIA dans une même application QGIS."""

from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

from qgis.PyQt.QtCore import QCoreApplication, QThread

from ..core.errors import ErrorCode, ToolError

# Nom stable entre les générations du plugin.
# Ne pas le modifier sans prévoir la coexistence avec les anciennes tâches.
_PROPERTY_NAME = "cynogis_obia_preparation_owner_v1"

def _application() -> QCoreApplication:
    application = QCoreApplication.instance()
    if application is None:
        raise RuntimeError(
            "Une application Qt est nécessaire pour le verrou OBIA."
        )

    if QThread.currentThread() != application.thread():
        raise RuntimeError(
            "Le verrou OBIA doit être manipulé sur le thread principal."
        )

    return application

def acquire_landcover_guard() -> Callable[[], None]:
    """Acquiert le verrou et renvoie sa fonction de libération.

    Acquisition et libération sont réservées au thread principal.
    Le verrou appartient à l'application, pas au module du plugin.
    """
    application = _application()
    current_owner = application.property(_PROPERTY_NAME)

    # Une valeur inattendue est traitée comme un verrou occupé.
    # Ne jamais écraser un état que cette génération ne comprend pas.
    if current_owner is not None and current_owner != "":
        raise ToolError(
            ErrorCode.BUSY,
            "Une préparation OBIA détient encore le verrou de cette "
            "application QGIS. Attendre sa terminaison, y compris "
            "si une annulation ou un rechargement a été demandé."
        )

    owner = uuid4().hex
    application.setProperty(_PROPERTY_NAME, owner)

    # setProperty() n'indique pas le succès de l'ajout d'une propriété
    # dynamique par sa valeur de retour : vérifier la valeur enregistrée.
    if application.property(_PROPERTY_NAME) != owner:
        raise RuntimeError(
            "Impossible d'acquérir le verrou de préparation OBIA."
        )

    released = False

    def release() -> None:
        nonlocal released

        if released:
            return

        current_application = _application()
        if current_application != application:
            raise RuntimeError(
                "L'application propriétaire du verrou OBIA a changé."
            )

        # Ne jamais effacer le verrou d'un autre propriétaire.
        if application.property(_PROPERTY_NAME) != owner:
            released = True
            return

        application.setProperty(_PROPERTY_NAME, "")

        if application.property(_PROPERTY_NAME) != "":
            raise RuntimeError(
                "Impossible de libérer le verrou de préparation OBIA."
            )

        released = True

    return release
