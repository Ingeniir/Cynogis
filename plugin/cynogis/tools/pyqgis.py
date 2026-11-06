"""Exécution de code PyQGIS libre, après validation humaine du code et de ses étapes."""
from __future__ import annotations

import contextlib
import inspect
import io
import logging
import textwrap
import traceback
from collections.abc import Generator
from typing import Any

import qgis.core
from qgis.PyQt import QtCore, QtGui, QtWidgets

from ..core.codecheck import blocking_calls, risky_names
from ..core.errors import ErrorCode, ToolError
from ..core.jobs import AlgCall, Fetch, Pacer, Steps
from ..core.registry import Level, tool
from ..core.schema import Param
from ..ui.confirm import register_detail_provider
from .common import to_json_value

logger = logging.getLogger("cynogis.pyqgis")
MAX_STDOUT = 5000

_PRELUDE = "def __cynogis_main__():\n    result = None\n"
_EPILOGUE = "\n    return result\n"

def _details(params: dict) -> list[str]:
    steps = [str(s) for s in params.get("steps") or []]
    # En tête (partie visible) : les étapes sont écrites par l'IA, le code fait foi.
    risky = risky_names(str(params.get("code", "")))
    alert = [f"⚠ Appels sensibles dans le code : {', '.join(risky)}", ""] if risky else []
    return [*alert, *(f"{i}. {s}" for i, s in enumerate(steps, 1)),
            "", f"Justification : {params.get('justification', '')}",
            "", "Code :", *str(params.get("code", "")).splitlines()]

def _as_generator(code: str, namespace: dict[str, Any]) -> Generator:
    """Compile le code comme corps de fonction. S'il contient un yield, c'est
    un générateur ; sinon on l'enveloppe pour que le dispatcher voie toujours un job."""
    source = _PRELUDE + textwrap.indent(code, "    ") + _EPILOGUE
    exec(compile(source, "<execute_pyqgis>", "exec"), namespace)
    out = namespace["__cynogis_main__"]()
    if inspect.isgenerator(out):
        return out

    def _immediate():
        return out
        yield  # rend la fonction génératrice

    return _immediate()

def _run_algorithm(algorithm_id: str, params: dict) -> Steps:
    """Dans le code : res = yield from run_algorithm("native:buffer", {...})"""
    return (yield AlgCall(algorithm_id, params))

def _fetch(url: str, authcfg: str | None = None, label: str = "téléchargement",
           geojson: bool = False) -> Steps:
    """Dans le code : data = yield from fetch(url)"""
    return (yield Fetch(url, authcfg, label, geojson))

@tool(level=Level.DESTROY, params={
    "code": Param("string",
        "Code Python exécuté dans QGIS comme un traitement de fond. Disponibles sans "
        "import : iface, project, tout qgis.core, QtCore, QtGui, QtWidgets. "
        "OBLIGATOIRE pour ne pas geler QGIS : "
        "(1) tout algorithme Processing via `res = yield from run_algorithm(id, params)` "
        "(jamais processing.run) ; "
        "(2) toute boucle sur des entités : `pace = Pacer('libellé', total)` puis "
        "`yield from pace(i)` en tête de boucle ; "
        "(3) tout téléchargement via `data = yield from fetch(url)`. "
        "Mettre la valeur à renvoyer dans `result` ; print() est capturé."),
    "steps": Param("array", "Courte description de chaque action du code, dans l'ordre, en "
                   "français et compréhensible par un non-développeur (ex. « Supprime le champ "
                   "temp de la couche Parcelles »). Affichée à l'utilisateur pour validation : "
                   "elle doit couvrir TOUT ce que fait le code.", items="string"),
    "justification": Param("string", "Pourquoi aucun outil dédié ne suffit."),
})
def execute_pyqgis(code: str, steps: list[str], justification: str) -> Steps:
    """Exécute du code PyQGIS libre, en dernier recours quand aucun outil Cynogis ne convient.
    L'utilisateur voit les étapes décrites et le code, puis accepte ou refuse : en cas de
    refus, ne pas réessayer sans lui demander. Le code peut tout faire : rester au plus près
    de la demande, préférer le tampon d'édition, ne jamais supprimer de fichier."""
    if not code.strip():
        raise ToolError(ErrorCode.INVALID_PARAMS, "code est vide.")
    if not [s for s in steps if str(s).strip()]:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Décris au moins une étape dans steps.")
    blocking = blocking_calls(code)
    if blocking:
        raise ToolError(ErrorCode.INVALID_PARAMS,
            f"Appels bloquants interdits : {', '.join(blocking)}. Utiliser "
            "`yield from run_algorithm(...)`, `yield from pace(i)` ou `yield from fetch(...)`.")

    from qgis.utils import iface
    namespace: dict[str, Any] = {name: getattr(qgis.core, name) for name in dir(qgis.core)
                                 if not name.startswith("_")}
    namespace.update(iface=iface, project=qgis.core.QgsProject.instance(),
                     QtCore=QtCore, QtGui=QtGui, QtWidgets=QtWidgets,
                     run_algorithm=_run_algorithm, fetch=_fetch, Pacer=Pacer,
                     __name__="cynogis_pyqgis")
    # NB : `processing` n'est plus injecté → l'IA est forcée de passer par run_algorithm.

    stdout = io.StringIO()
    logger.info("execute_pyqgis : %s", " | ".join(steps))

    try:
        with contextlib.redirect_stdout(stdout):
            gen = _as_generator(code, namespace)
    except Exception as exc:
        raise _failure(exc, stdout) from exc

    # Relais manuel : redirect_stdout ne doit être actif que pendant que le code
    # de l'IA tourne, pas pendant qu'une QgsTask travaille en arrière-plan.
    value, error = None, None
    while True:
        try:
            with contextlib.redirect_stdout(stdout):
                step = gen.throw(error) if error else gen.send(value)
        except StopIteration as stop:
            out = stdout.getvalue()
            return {"result": to_json_value(stop.value),
                    "stdout": out[-MAX_STDOUT:], "stdout_truncated": len(out) > MAX_STDOUT}
        except Exception as exc:
            raise _failure(exc, stdout) from exc
        try:
            value, error = (yield step), None   # le JobManager exécute l'étape
        except Exception as exc:                # étape échouée → remontée dans le code IA
            value, error = None, exc


def _failure(exc: Exception, stdout: io.StringIO) -> ToolError:
    return ToolError(ErrorCode.EXECUTION_FAILED, f"{type(exc).__name__} : {exc}",
                     {"traceback": traceback.format_exc()[-3000:],
                      "stdout": stdout.getvalue()[-2000:]})


register_detail_provider("execute_pyqgis", _details)
