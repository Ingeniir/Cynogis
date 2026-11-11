from __future__ import annotations

import logging
from pathlib import Path

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtGui import QIcon

from .bridge.connection import new_token, remove_connection_file, write_connection_file
from .bridge.server import HOST, BridgeServer
from .compat import QAction
from .core.audit import AuditLog
from .core.cleanup import CleanupStep, run_cleanup_steps
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
    landcover,
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
    tabular,
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
TOOL_MODULES = (system, layers, features, measures, tabular, overlaps, geoprocessing, algorithms,
                editing, shapefiles, coefficients, landscape, landcover, terrain, styling, export,
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
        self._unloading = False
        self._unload_failures: list[str] = []
        self._bridge_stop_in_progress = False
        self._bridge_cleanup_pending = False
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
                               "Serveur Cynogis", self.iface.mainWindow())
        self._action.setCheckable(True)
        self._action.setToolTip("Démarrer / arrêter le serveur Cynogis")
        self._action.toggled.connect(self._on_toggled)
        self.iface.addToolBarIcon(self._action)
        self.iface.addPluginToMenu(MENU, self._action)

        self._load_palettes()
        project = QgsProject.instance()
        project.aboutToBeCleared.connect(self._cancel_jobs)
        project.layersWillBeRemoved.connect(self._cancel_jobs)

    def unload(self) -> None:
        """Démonte les ressources du plugin sans attendre les tâches actives.

        Une demande d'annulation ne confirme pas leur arrêt.
        Les échecs de nettoyage sont conservés et journalisés.
        """
        if self._unloading:
            return

        self._unloading = True
        project = QgsProject.instance()
        action = self._action

        steps: list[CleanupStep] = [
            (
                "déconnexion du signal aboutToBeCleared",
                lambda: project.aboutToBeCleared.disconnect(self._cancel_jobs),
            ),
            (
                "déconnexion du signal layersWillBeRemoved",
                lambda: project.layersWillBeRemoved.disconnect(self._cancel_jobs),
            ),
            # Ne plus accepter de nouvelles requêtes avant d'annuler.
            ("arrêt du pont", self._stop_bridge),
            (
                "détachement des finisseurs des jobs",
                self._detach_job_finishers,
            ),
            ("demande d'annulation des jobs", self._cancel_jobs),
        ]

        if action is not None:
            steps.extend([
                (
                    "retrait de l'icône de barre d'outils",
                    lambda: self.iface.removeToolBarIcon(action),
                ),
                (
                    "retrait de l'entrée de menu",
                    lambda: self.iface.removePluginMenu(MENU, action),
                ),
                (
                    "suppression différée de l'action",
                    lambda: action.deleteLater(),
                ),
            ])

        failures = run_cleanup_steps(steps)
        self._action = None

        # Conserver uniquement des textes : ne pas retenir les tracebacks
        # et leurs références d'objets dans l'instance.
        self._unload_failures = [
            f"{label} : {type(error).__name__} : {error}"
            for label, error in failures
        ]

        if failures:
            logger.error(
                "Déchargement Cynogis incomplet : %s",
                " ; ".join(self._unload_failures),
            )

        log_failures = run_cleanup_steps([
            (
                "arrêt de la journalisation du plugin",
                lambda: teardown_logging(self._log_handler),
            ),
        ])

        self._unload_failures.extend(
            f"{label} : {type(error).__name__} : {error}"
            for label, error in log_failures
        )

    # --- Pont -------------------------------------------------------------
    def _on_toggled(self, checked: bool) -> None:
        if self._unloading:
            self._set_checked(False)
            return

        try:
            if checked:
                self._start_bridge()
            else:
                self._stop_bridge()
        except Exception as exc:
            logger.exception("Échec du changement d'état du pont Cynogis.")
            self._set_checked(False)
            self._notify(
                f"Le pont n'est pas disponible : {exc}",
                Qgis.MessageLevel.Critical,
            )

    def _start_bridge(self) -> None:
        if self._unloading:
            logger.warning(
                "Démarrage du pont refusé : déchargement du plugin en cours."
            )
            return

        if self._bridge_stop_in_progress:
            raise RuntimeError("Un arrêt du pont est déjà en cours.")

        if self._bridge_cleanup_pending:
            self._stop_bridge()

        if self._bridge is not None:
            return

        token = new_token()
        bridge = BridgeServer(
            self._dispatcher,
            token,
            parent=self.iface.mainWindow(),
        )

        # Garder les références avant les opérations susceptibles d'échouer.
        self._bridge = bridge
        self._token = token

        try:
            bridge.start()
            write_connection_file(HOST, bridge.port, token)
        except Exception as start_error:
            failures = run_cleanup_steps([
                (
                    "nettoyage après échec du démarrage",
                    lambda: self._stop_bridge(notify=False),
                )
            ])

            if failures:
                raise RuntimeError(
                    f"Échec du démarrage : {start_error}. "
                    f"Le nettoyage reste incomplet : {failures[0][1]}"
                ) from start_error

            raise

        self._notify(
            f"Serveur démarré (port {bridge.port})",
            Qgis.MessageLevel.Success,
        )

    def _stop_bridge(self, *, notify: bool = True) -> None:
        if self._bridge_stop_in_progress:
            raise RuntimeError("Un arrêt du pont est déjà en cours.")

        bridge = self._bridge
        token = self._token

        if bridge is None and token is None:
            self._bridge_cleanup_pending = False
            return

        self._bridge_stop_in_progress = True
        self._bridge_cleanup_pending = True

        def stop_and_release_bridge() -> None:
            if bridge is None:
                return

            bridge.stop()
            bridge.deleteLater()

            if self._bridge is bridge:
                self._bridge = None

        def remove_and_release_connection() -> None:
            if token is None:
                return

            remove_connection_file(token, strict=True)

            if self._token == token:
                self._token = None

        try:
            steps: list[CleanupStep] = []

            if bridge is not None:
                steps.append((
                    "arrêt et suppression différée du serveur TCP",
                    stop_and_release_bridge,
                ))

            if token is not None:
                steps.append((
                    "suppression du fichier de connexion",
                    remove_and_release_connection,
                ))

            failures = run_cleanup_steps(steps)

            if failures:
                labels = ", ".join(label for label, _error in failures)
                raise RuntimeError(
                    f"Arrêt du pont incomplet : {labels}"
                ) from failures[0][1]

            self._bridge_cleanup_pending = False

        finally:
            self._bridge_stop_in_progress = False

        if notify:
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
        if self._unloading:
            return
        self.iface.messageBar().pushMessage("Cynogis", message, level=level, duration=5)

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

    def _detach_job_finishers(self) -> None:
        """Empêche les terminaisons futures d'appeler l'ancien dispatcher."""
        jobs = self._dispatcher.jobs
        if jobs is not None:
            jobs.detach_finishers()
