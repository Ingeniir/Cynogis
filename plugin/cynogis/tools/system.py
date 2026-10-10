from __future__ import annotations

from typing import Any

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtCore import QT_VERSION_STR

from .. import __version__
from ..core.dispatcher import Dispatcher


def ping(_params: dict[str, Any]) -> dict[str, Any]:
    return {"pong": True, "plugin_version": __version__,
            "qgis_version": Qgis.QGIS_VERSION, "qt_version": QT_VERSION_STR}


def get_project_info(_params: dict[str, Any]) -> dict[str, Any]:
    project = QgsProject.instance()
    return {
        "title": project.title() or None,
        "file": project.fileName() or None,
        "home_path": project.homePath() or None,
        "crs": project.crs().authid() or None,
        "layer_count": len(project.mapLayers()),
    }


def register(dispatcher: Dispatcher) -> None:
    dispatcher.register("ping", ping)
    dispatcher.register("get_project_info", get_project_info)
