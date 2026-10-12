"""Exécution de code PyQGIS libre, après validation humaine du code et de ses étapes."""
from __future__ import annotations

import contextlib
import io
import logging
import traceback
from typing import Any

import processing
import qgis.core
from qgis.PyQt import QtCore, QtGui, QtWidgets

from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..ui.confirm import register_detail_provider
from .common import to_json_value

logger = logging.getLogger("cynogis.pyqgis")
MAX_STDOUT = 5000


@tool(level=Level.DESTROY, params={
    "code": Param("string", "Code Python à exécuter dans QGIS. Disponibles sans import : iface, "
                  "project (QgsProject.instance()), processing, tout qgis.core, QtCore, QtGui, "
                  "QtWidgets. Mettre la valeur à renvoyer dans la variable result ; print() "
                  "est capturé."),
    "steps": Param("array", "Courte description de chaque action du code, dans l'ordre, en "
                   "français et compréhensible par un non-développeur (ex. « Supprime le champ "
                   "temp de la couche Parcelles »). Affichée à l'utilisateur pour validation : "
                   "elle doit couvrir TOUT ce que fait le code.", items="string"),
    "justification": Param("string", "Pourquoi aucun outil dédié ne suffit."),
})
def execute_pyqgis(code: str, steps: list[str], justification: str) -> dict:
    """Exécute du code PyQGIS libre, en dernier recours quand aucun outil Cynogis ne convient.
    L'utilisateur voit les étapes décrites et le code, puis accepte ou refuse : en cas de
    refus, ne pas réessayer sans lui demander. Le code tourne sur le thread principal de
    QGIS (pas de traitement long) et peut tout faire : rester au plus près de la demande,
    préférer le tampon d'édition, ne jamais supprimer de fichier."""
    if not code.strip():
        raise ToolError(ErrorCode.INVALID_PARAMS, "code est vide.")
    if not [s for s in steps if str(s).strip()]:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Décris au moins une étape dans steps.")
    from qgis.utils import iface
    namespace: dict[str, Any] = {name: getattr(qgis.core, name) for name in dir(qgis.core)
                                 if not name.startswith("_")}
    namespace.update(iface=iface, project=qgis.core.QgsProject.instance(),
                     processing=processing, QtCore=QtCore, QtGui=QtGui, QtWidgets=QtWidgets,
                     result=None, __name__="cynogis_pyqgis")
    stdout = io.StringIO()
    logger.info("execute_pyqgis : %s", " | ".join(steps))
    try:
        with contextlib.redirect_stdout(stdout):
            exec(compile(code, "<execute_pyqgis>", "exec"), namespace)
    except Exception as exc:
        raise ToolError(ErrorCode.EXECUTION_FAILED, f"{type(exc).__name__} : {exc}",
                        {"traceback": traceback.format_exc()[-3000:],
                         "stdout": stdout.getvalue()[-2000:]}) from exc
    out = stdout.getvalue()
    return {"result": to_json_value(namespace.get("result")),
            "stdout": out[-MAX_STDOUT:], "stdout_truncated": len(out) > MAX_STDOUT}


def _details(params: dict) -> list[str]:
    steps = [str(s) for s in params.get("steps") or []]
    return [*(f"{i}. {s}" for i, s in enumerate(steps, 1)),
            "", f"Justification : {params.get('justification', '')}",
            "", "Code :", *str(params.get("code", "")).splitlines()]


register_detail_provider("execute_pyqgis", _details)
