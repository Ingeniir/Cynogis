from __future__ import annotations

import logging
from pathlib import Path

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtGui import QIcon

from .bridge.connection import new_token, remove_connection_file, write_connection_file
from .bridge.server import HOST, BridgeServer
from .compat import QAction
from .core.audit import AuditLog
from .core.dispatcher import Dispatcher
from .core.log import setup_logging, teardown_logging
from .core.policy import PermissionPolicy
from .core.registry import Level, ToolRegistry
from .tools import (
    algorithms,
    atlas,
    coefficients,
    density,
    editing,
    export,
    features,
    fielddata,
    geoprocessing,
    habref,
    impacts,
    landscape,
    layers,
    measures,
    overlaps,
    project_audit,
    proximity,
    pyqgis,
    referentials,
    sampling,
    shapefiles,
    stakes,
    styling,
    system,
    taxref,
    terrain,
    webservices,
    zoning,
)
from .tools.tasks import ProcessingExecutor
from .ui.confirm import make_confirmer

PLUGIN_DIR = Path(__file__).resolve().parent
DATA_DIR = Path.home() / ".cynogis"
MENU = "&Cynogis"
TOOL_MODULES = (system, layers, features, measures, overlaps, geoprocessing, algorithms,
                editing, shapefiles, coefficients, landscape, terrain, styling, export,
                proximity, referentials, webservices, fielddata, taxref, habref,
                stakes, density, sampling, atlas, zoning,
                impacts, pyqgis, project_audit)
logger = logging.getLogger("cynogis")


class CynogisPlugin:
    def __init__(self, iface) -> None:
        self.iface = iface
        self._action: QAction | None = None
        self._bridge: BridgeServer | None = None
        self._token: str | None = None
        self._log_handler = setup_logging()
        registry = ToolRegistry()
        for module in TOOL_MODULES:
            registry.register_module(module)
        self._dispatcher = Dispatcher(
            registry,
            policy=PermissionPolicy(max_level=Level.DESTROY,
                                    confirm=make_confirmer(iface.mainWindow())),
            audit=AuditLog(DATA_DIR / "audit"),
            executor=ProcessingExecutor(),
        )
        logger.info("Outils chargés : %s", ", ".join(registry.names))

    # --- Cycle de vie QGIS --------------------------------------------------
    def initGui(self) -> None:
        self._action = QAction(QIcon(str(PLUGIN_DIR / "icons" / "icon.svg")),
                               "Serveur GeoMCP", self.iface.mainWindow())
        self._action.setCheckable(True)
        self._action.setToolTip("Démarrer / arrêter le serveur GeoMCP")
        self._action.toggled.connect(self._on_toggled)
        self.iface.addToolBarIcon(self._action)
        self.iface.addPluginToMenu(MENU, self._action)

        self._load_palettes()
        project = QgsProject.instance()
        project.aboutToBeCleared.connect(self._cancel_jobs)
        project.layersWillBeRemoved.connect(self._cancel_jobs)

    def unload(self) -> None:
        project = QgsProject.instance()
        project.aboutToBeCleared.disconnect(self._cancel_jobs)
        project.layersWillBeRemoved.disconnect(self._cancel_jobs)
        self._cancel_jobs()
        self._stop_bridge()
        if self._action is not None:
            self.iface.removeToolBarIcon(self._action)
            self.iface.removePluginMenu(MENU, self._action)
            self._action.deleteLater()
            self._action = None
        teardown_logging(self._log_handler)

    # --- Pont -------------------------------------------------------------
    def _on_toggled(self, checked: bool) -> None:
        if checked:
            self._start_bridge()
        else:
            self._stop_bridge()

    def _start_bridge(self) -> None:
        if self._bridge is not None:
            return
        token = new_token()
        bridge = BridgeServer(self._dispatcher, token, parent=self.iface.mainWindow())
        try:
            bridge.start()
            write_connection_file(HOST, bridge.port, token)
        except (RuntimeError, OSError) as exc:
            bridge.stop()
            bridge.deleteLater()
            self._notify(f"Échec du démarrage : {exc}", Qgis.MessageLevel.Critical)
            self._set_checked(False)
            return
        self._bridge, self._token = bridge, token
        self._notify(f"Serveur démarré (port {bridge.port})", Qgis.MessageLevel.Success)

    def _stop_bridge(self) -> None:
        if self._bridge is None:
            return
        self._bridge.stop()
        self._bridge.deleteLater()
        self._bridge = None
        if self._token:
            remove_connection_file(self._token)
            self._token = None
        self._notify("Serveur arrêté", Qgis.MessageLevel.Info)

    def _cancel_jobs(self, *_args) -> None:
        """Projet fermé, couche supprimée ou plugin déchargé : un traitement en cours
        pourrait reprendre sur une couche détruite (plantage) ; il est annulé."""
        if self._dispatcher.jobs is not None:
            self._dispatcher.jobs.cancel_all("Projet fermé, couche supprimée ou plugin "
                                             "déchargé pendant le traitement : annulé.")

    def _set_checked(self, value: bool) -> None:
        if self._action is not None:
            self._action.blockSignals(True)
            self._action.setChecked(value)
            self._action.blockSignals(False)

    def _notify(self, message: str, level: Qgis.MessageLevel) -> None:
        logger.info(message)
        self.iface.messageBar().pushMessage("GeoMCP", message, level=level, duration=5)

    def _load_palettes(self) -> None:
        """Charge les palettes enregistrées par l'utilisateur, sans bloquer au besoin."""
        import json

        from .core.palettes import PALETTES_FILE, load_user_palettes

        if not PALETTES_FILE.exists():
            return
        try:
            report = load_user_palettes(json.loads(PALETTES_FILE.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            logger.warning("Palettes utilisateur illisibles (%s) : fichier ignoré.", exc)
            return
        if report["rejected"]:
            logger.warning("Palettes ignorées : %s", ", ".join(report["rejected"]))
