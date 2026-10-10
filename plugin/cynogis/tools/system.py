from __future__ import annotations

from collections import Counter

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtCore import QT_VERSION_STR

from .. import __version__
from ..core.dispatcher import ToolResult
from ..core.registry import Level, tool
from ..core.territory import TERRITORIES, UNKNOWN
from .common import crs_info, layer_kind, territory_info


@tool(level=Level.READ)
def ping() -> dict:
    """Vérifie que QGIS et le plugin Cynogis répondent. Renvoie les versions QGIS, Qt et plugin."""
    return {"pong": True, "plugin_version": __version__,
            "qgis_version": Qgis.QGIS_VERSION, "qt_version": QT_VERSION_STR}


@tool(level=Level.READ)
def get_project_info() -> ToolResult:
    """Informations générales du projet QGIS ouvert : titre, fichier, SCR, nombre de couches
    par type et territoire détecté (La Réunion, Mayotte, mixte ou inconnu).
    À appeler en premier pour comprendre le contexte de travail."""
    project = QgsProject.instance()
    layers = list(project.mapLayers().values())
    found: set[str] = set()
    warnings: list[str] = []
    for layer in layers:
        info, layer_warnings = territory_info(layer)
        warnings += layer_warnings
        if info["code"] != "unknown":
            found.add(info["code"])
    if len(found) == 1:
        territory = TERRITORIES[found.pop()].as_dict()
    elif found:
        territory = {"code": "mixed", "name": "Plusieurs territoires", "reference_crs": None}
    else:
        territory = dict(UNKNOWN)
    if project.crs().isValid() and project.crs().isGeographic():
        warnings.insert(0, f"SCR du projet géographique ({project.crs().authid()}).")
    data = {
        "title": project.title() or None,
        "file": project.fileName() or None,
        "home_path": project.homePath() or None,
        "crs": crs_info(project.crs()),
        "layer_count": len(layers),
        "layers_by_type": dict(Counter(layer_kind(lyr) for lyr in layers)),
        "territory": territory,
    }
    return ToolResult(data, warnings[:20])
