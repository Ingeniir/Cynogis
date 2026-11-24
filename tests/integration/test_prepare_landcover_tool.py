"""Outil prepare_landcover_inputs : vrai registre, vrai Dispatcher, vraie tâche.

Nécessite PyQGIS, GDAL et NumPy. Sous pytest sans QGIS, le module est ignoré. Le Python
de QGIS n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" \
        tests/integration/test_prepare_landcover_tool.py

Processus QGIS de test isolé : petits GeoTIFF et périmètres temporaires, couches
ajoutées au QgsProject de ce processus. En sortie, même après un échec, les tâches sont
arrêtées et leur arrêt confirmé AVANT le retrait des couches et la restauration de la
propriété Qt du verrou OBIA ; arrêt non confirmé = processus de test interrompu, rien
retiré ni restauré (voir environment()). Ni la session QGIS de travail ni l'orthophoto
réelle ne sont utilisées.

- test_registry_* : registre construit comme le plugin (TOOL_MODULES) ;
- test_policy_*, test_invalid_* : vrai Dispatcher, rejet avant toute tâche ;
- test_real_task_* : vrai ProcessingExecutor et vraie LandcoverPreparationTask ;
  test_real_task_cancel_* remplace prepare_native_inputs par un traitement contrôlé.

CYNOGIS_CATALOG_DUMP=<fichier> : écrit l'entrée list_tools de l'outil (contrôle de
découverte côté serveur MCP, hors de ce fichier).
"""
from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plugin"))
else:
    import pytest

    pytest.importorskip("qgis.core", exc_type=ImportError)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QObject

_QGS = QgsApplication.instance()
if _QGS is None:
    _QGS = QgsApplication([], True)
    _QGS.initQgis()

import numpy as np  # noqa: E402
from osgeo import gdal, osr  # noqa: E402

import cynogis.plugin as plugin_mod  # noqa: E402
from cynogis.bridge.protocol import PROTOCOL_VERSION, decode_request  # noqa: E402
from cynogis.core.audit import AuditLog  # noqa: E402
from cynogis.core.dispatcher import Dispatcher  # noqa: E402
from cynogis.core.errors import ErrorCode, ToolError  # noqa: E402
from cynogis.core.jobs import PrepareLandcover  # noqa: E402
from cynogis.core.landcover import PreparationConfig  # noqa: E402
from cynogis.core.policy import PermissionPolicy  # noqa: E402
from cynogis.core.registry import Level, ToolRegistry  # noqa: E402
from cynogis.landcover_processing import prepare as preparation  # noqa: E402
from cynogis.tools import landcover  # noqa: E402
from cynogis.tools import outputs as outputs_mod  # noqa: E402
from cynogis.tools.landcover_guard import _PROPERTY_NAME as GUARD  # noqa: E402
from cynogis.tools.tasks import ProcessingExecutor  # noqa: E402

TOOL = "prepare_landcover_inputs"
GRID = (341000.0, 0.5, 0.0, 7642400.0, 0.0, -0.5)
AOI_WKT = ("POLYGON ((341000 7642398, 341002 7642398, 341002 7642400, "
           "341000 7642400, 341000 7642398))")
STOP = threading.Event()


# --- Outils --------------------------------------------------------------------------------
def spin(condition, timeout=30.0) -> bool:
    deadline = time.monotonic() + timeout
    while not condition() and time.monotonic() < deadline:
        QCoreApplication.processEvents()
        time.sleep(0.005)
    return condition()


@contextlib.contextmanager
def patched(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)


def make_geotiff(path: Path, width=4, height=4, epsg=2975) -> Path:
    reference = osr.SpatialReference()
    assert reference.ImportFromEPSG(epsg) == 0
    dataset = gdal.GetDriverByName("GTiff").Create(str(path), width, height, 3, gdal.GDT_Byte)
    try:
        dataset.SetGeoTransform(GRID)
        dataset.SetProjection(reference.ExportToWkt())
        for index, value in enumerate((10, 20, 30)):
            values = np.full((height, width), value, np.uint8)
            values[1, 1] = 255                              # pixel NoData dans le périmètre
            band = dataset.GetRasterBand(index + 1)
            band.WriteArray(values)
            band.SetNoDataValue(255)
    finally:
        dataset.Close()
    return path


class Env:
    """Couches temporaires dans le projet du processus de test + nettoyage complet."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="cynogis_prepare_tool_"))
        # Le projet du processus a pour dossier self.root (setPresetHomePath) :
        # racine OBIA imposée = self.root/mcp_outputs/obia.
        self.obia = self.root / "mcp_outputs" / "obia"
        self.output = self.obia / "sorties"
        self.output.mkdir(parents=True)
        self.layers, self.executors = [], []

    def raster(self, name="ortho", **kwargs):
        path = make_geotiff(self.root / f"{name}.tif", **kwargs)
        layer = QgsRasterLayer(str(path), name, "gdal")
        assert layer.isValid()
        return self._add(layer), path

    def aoi(self, epsg=2975, wkt=AOI_WKT):
        layer = QgsVectorLayer(f"Polygon?crs=EPSG:{epsg}", "perimetre", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(wkt))
        assert layer.dataProvider().addFeatures([feature])
        fid = next(layer.getFeatures()).id()
        return self._add(layer), fid

    def _add(self, layer):
        QgsProject.instance().addMapLayer(layer)
        self.layers.append(layer.id())
        return layer

    def dispatcher(self, max_level=Level.DESTROY, name="audit"):
        registry = ToolRegistry()
        for module in plugin_mod.TOOL_MODULES:
            registry.register_module(module)
        executor = ProcessingExecutor()
        self.executors.append(executor)
        audit = AuditLog(self.root / name)
        dispatcher = Dispatcher(registry, policy=PermissionPolicy(max_level=max_level),
                                audit=audit, executor=executor)
        return dispatcher, audit

    def outputs(self):
        return sorted(p.name for p in self.output.iterdir())


def abort_test_process(message: str) -> None:
    """Arrêt de tâche non confirmé : aucun essai ne doit suivre dans ce processus.

    Lève une BaseException (pytest.exit ou SystemExit), que ni le lanceur direct
    (`except Exception`) ni pytest ne traitent comme un simple échec d'essai.
    """
    print(f"ARRÊT DU PROCESSUS DE TEST : {message}", file=sys.stderr, flush=True)
    if __name__ != "__main__":
        pytest.exit(message, returncode=1)
    raise SystemExit(message)


@contextlib.contextmanager
def environment():
    """Nettoyage dans l'ordre : arrêt confirmé, puis couches, verrou, dossier.

    Arrêt confirmé = plus aucune tâche dans `executor._active`, donc finished() exécuté
    et verrou rendu par la tâche elle-même. Sinon : couches, verrou et env.root restent
    en place (une tâche vivante peut encore les utiliser) et le processus s'arrête.

    env.root : supprimé si l'essai a réussi et l'arrêt est confirmé ; conservé (chemin
    affiché) si l'essai a échoué, pour l'examen, ou si l'arrêt n'est pas confirmé.
    """
    app = QCoreApplication.instance()
    saved = app.property(GUARD)
    app.setProperty(GUARD, "")
    STOP.clear()
    env = Env()
    project = QgsProject.instance()
    saved_home = project.presetHomePath()
    project.setPresetHomePath(str(env.root))
    succeeded = False
    try:
        yield env
        succeeded = True
    finally:
        project.setPresetHomePath(saved_home)
        STOP.set()
        for executor in env.executors:
            for task in list(executor._active):
                task.cancel()
        stopped = all([spin(lambda e=e: not e._active) for e in env.executors])
        if not stopped:
            abort_test_process(
                "une tâche de préparation n'a pas confirmé son arrêt ; couches, verrou "
                f"et dossier {env.root} laissés en place")
        if app.property(GUARD) not in (None, ""):
            abort_test_process(
                "verrou OBIA encore détenu alors qu'aucune tâche n'est active ; "
                f"non restauré, dossier {env.root} conservé")
        QgsProject.instance().removeMapLayers(env.layers)
        app.setProperty(GUARD, saved)
        if succeeded:
            shutil.rmtree(env.root)
        else:
            print(f"dossier de l'essai conservé : {env.root}", file=sys.stderr, flush=True)


def request(method, **params):
    raw = {"v": PROTOCOL_VERSION, "id": "1", "method": method, "params": params,
           "token": "t"}
    return decode_request(json.dumps(raw).encode())


def params(raster, aoi, fid, output, **overrides):
    values = {"raster_layer_id": raster.id(), "aoi_layer_id": aoi.id(),
              "aoi_feature_id": fid, "rgb_bands": [1, 2, 3],
              "output_parent": str(output), "validity_policy": "respect_source_masks"}
    values.update(overrides)
    return values


def final_response(dispatcher, job_id, timeout=60.0):
    box = {}

    def done():
        box["r"] = dispatcher.dispatch(request("get_job_status", job_id=job_id))
        return box["r"].job_id is None

    assert spin(done, timeout), "job non terminé"
    return box["r"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- Registre et catalogue -----------------------------------------------------------------
def test_registry_discovers_tool_through_existing_module():
    assert landcover in plugin_mod.TOOL_MODULES
    with environment() as env:
        dispatcher, _ = env.dispatcher()
        spec = dispatcher.registry.get(TOOL)
        assert spec is not None and spec.level == Level.CREATE
        assert spec.handler is landcover.prepare_landcover_inputs
        signature = list(inspect.signature(spec.handler).parameters)
        assert list(spec.params) == signature                # décorateur = signature
        assert inspect.isgeneratorfunction(spec.handler)

        catalog = dispatcher.dispatch(request("list_tools")).data["tools"]
        entry = next(e for e in catalog if e["name"] == TOOL)
        schema = entry["input_schema"]
        # output_parent : facultatif (racine imposée par Cynogis si omis).
        assert sorted(schema["required"]) == sorted(set(signature) - {"output_parent"})
        assert inspect.signature(spec.handler).parameters["output_parent"].default is None
        assert schema["properties"]["rgb_bands"]["items"] == {"type": "integer"}
        assert schema["properties"]["validity_policy"]["enum"] == ["respect_source_masks"]
        dump = os.environ.get("CYNOGIS_CATALOG_DUMP")
        if dump:
            Path(dump).write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")


def test_policy_below_create_is_refused():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, _ = env.dispatcher(max_level=Level.READ)
        response = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, env.output)))
        assert response.error["code"] == "PERMISSION_DENIED"
        assert env.outputs() == []


# --- Paramètres invalides : rejet sans dossier créé ---------------------------------------
def test_invalid_parameters_create_no_output():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, _ = env.dispatcher()
        a_file = env.root / "fichier.txt"
        a_file.write_text("x", encoding="utf-8")
        cases = {
            "relatif": {"output_parent": "sorties"},
            "absent": {"output_parent": str(env.root / "absent")},
            "fichier": {"output_parent": str(a_file)},
            "bandes": {"rgb_bands": [1, 1, 2]},
            "politique": {"validity_policy": "ignorer"},
            "entite": {"aoi_feature_id": 999},
        }
        for label, override in cases.items():
            response = dispatcher.dispatch(
                request(TOOL, **params(raster, aoi, fid, env.output, **override)))
            assert not response.ok, label
            assert response.error["code"] == "INVALID_PARAMS", (label, response.error)
            assert response.job_id is None, label
        assert env.outputs() == []
        assert dispatcher.jobs.running is None


# --- Racine de sortie imposée : <projet>/mcp_outputs/obia ---------------------------------
def _without_output_parent(raster, aoi, fid, env):
    values = params(raster, aoi, fid, env.output)
    del values["output_parent"]
    return values


def _tool_error(function, *args) -> ToolError:
    try:
        function(*args)
    except ToolError as exc:
        return exc
    raise AssertionError("ToolError attendue")


def test_output_parent_outside_root_is_refused_without_redirection():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, audit = env.dispatcher()
        outside = env.root / "dehors"                        # existe, hors racine
        outside.mkdir()
        response = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, outside)))
        assert response.error["code"] == "INVALID_PARAMS", response.error
        assert "extérieur à la racine" in response.error["message"]
        assert response.job_id is None and dispatcher.jobs.running is None
        assert list(outside.iterdir()) == []                 # aucune redirection
        assert env.outputs() == [] and [p.name for p in env.obia.iterdir()] == ["sorties"]
        assert [e["ok"] for e in audit.recent(10) if e["tool"] == TOOL] == [False]


def test_output_parent_omitted_uses_project_root():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, audit = env.dispatcher()
        started = dispatcher.dispatch(request(TOOL, **_without_output_parent(raster, aoi, fid,
                                                                             env)))
        assert started.ok and started.job_id, started.error
        final = final_response(dispatcher, started.job_id)
        assert final.ok, final.error
        directory = Path(final.data["output_directory"])
        assert directory.parent == env.obia.resolve()
        assert not any("sans emplacement local" in w for w in final.warnings)
        entries = [e for e in audit.recent(10) if e["tool"] == TOOL]
        assert len(entries) == 1 and entries[0]["ok"]
        assert all(Path(p).parent == directory for p in entries[0]["outputs"])


def test_unsaved_project_falls_back_with_explicit_warning():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        fallback = env.root / "repli"
        project = QgsProject.instance()
        project.setPresetHomePath("")
        assert project.homePath() == ""                      # aucun emplacement local
        with patched(outputs_mod, "FALLBACK_DIR", fallback):
            step, warnings = landcover._build_preparation_step(
                raster.id(), aoi.id(), fid, [1, 2, 3], None, "respect_source_masks")
            assert step.output_parent == (fallback / "obia").resolve()
            assert any("Projet sans emplacement local" in w for w in warnings)
            # Dossier de l'ancienne racine : extérieur au repli, donc refusé.
            error = _tool_error(landcover._build_preparation_step, raster.id(), aoi.id(),
                                fid, [1, 2, 3], str(env.output), "respect_source_masks")
            assert error.code == ErrorCode.INVALID_PARAMS
        assert env.outputs() == []


def test_unsaved_project_fallback_warning_reaches_final_response():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, audit = env.dispatcher()
        fallback = env.root / "repli"
        QgsProject.instance().setPresetHomePath("")
        with patched(outputs_mod, "FALLBACK_DIR", fallback):
            started = dispatcher.dispatch(
                request(TOOL, **_without_output_parent(raster, aoi, fid, env)))
        assert started.ok and started.job_id, started.error
        final = final_response(dispatcher, started.job_id)
        assert final.ok, final.error
        directory = Path(final.data["output_directory"])
        assert directory.parent == (fallback / "obia").resolve()
        assert sum("Projet sans emplacement local" in w for w in final.warnings) == 1
        entries = [e for e in audit.recent(10) if e["tool"] == TOOL]
        assert len(entries) == 1 and entries[0]["ok"]
        assert env.outputs() == []                           # rien dans l'ancienne racine


def test_inaccessible_project_home_is_refused_without_fallback():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, _ = env.dispatcher()
        missing = env.root / "projet_deplace"
        fallback = env.root / "repli"
        QgsProject.instance().setPresetHomePath(str(missing))
        with patched(outputs_mod, "FALLBACK_DIR", fallback):
            response = dispatcher.dispatch(
                request(TOOL, **_without_output_parent(raster, aoi, fid, env)))
        assert response.error["code"] == "WRITE_FAILED", response.error
        assert response.job_id is None
        assert not missing.exists() and not fallback.exists()


def test_root_creation_failure_is_refused():
    with environment() as env:
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, _ = env.dispatcher()
        home = env.root / "projet_bloque"
        home.mkdir()
        (home / "mcp_outputs").write_text("fichier homonyme", encoding="utf-8")
        QgsProject.instance().setPresetHomePath(str(home))
        response = dispatcher.dispatch(
            request(TOOL, **_without_output_parent(raster, aoi, fid, env)))
        assert response.error["code"] == "WRITE_FAILED", response.error
        assert (home / "mcp_outputs").is_file()


def test_layer_id_and_feature_id_are_not_confused():
    # Régression : la couche du périmètre doit être cherchée par aoi_layer_id, jamais
    # par aoi_feature_id (sinon TypeError -> INTERNAL_ERROR pour tout appel valide).
    # Les identifiants invalides sont refusés plus tôt par inspect_landcover_inputs :
    # seul un appel valide atteint la recherche de couche du helper.
    with environment() as env:
        raster, _ = env.raster()
        decoy, decoy_fid = env.aoi(wkt="POLYGON((341000.2 7642398.2, 341000.8 7642398.2, "
                                       "341000.8 7642398.8, 341000.2 7642398.8, "
                                       "341000.2 7642398.2))")
        aoi, fid = env.aoi()
        assert fid == decoy_fid                             # même fid, couches distinctes
        expected = aoi.getFeature(fid).geometry()
        assert not expected.equals(decoy.getFeature(decoy_fid).geometry())

        step, _ = landcover._build_preparation_step(
            raster.id(), aoi.id(), fid, [1, 2, 3], str(env.output), "respect_source_masks")
        captured = QgsGeometry()
        captured.fromWkb(step.aoi_wkb)
        assert captured.equals(expected)                    # périmètre de aoi_layer_id
        assert step.aoi_crs_wkt == aoi.crs().toWkt()
        assert env.outputs() == []


def test_invalid_crs_mismatch_is_rejected_without_transformation():
    with environment() as env:
        raster, _ = env.raster()
        # Même rectangle reprojeté : il recouvre le raster, seul le SCR diffère.
        geometry = QgsGeometry.fromWkt(AOI_WKT)
        geometry.transform(QgsCoordinateTransform(
            QgsCoordinateReferenceSystem("EPSG:2975"),
            QgsCoordinateReferenceSystem("EPSG:4471"), QgsProject.instance()))
        aoi, fid = env.aoi(epsg=4471, wkt=geometry.asWkt())
        dispatcher, _ = env.dispatcher()
        response = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, env.output)))
        assert response.error["code"] == "INVALID_PARAMS", response.error
        assert "même SCR" in response.error["message"], response.error
        assert "Aucune projection automatique" in response.error["message"]
        assert env.outputs() == []


def test_invalid_whole_raster_pixel_limit():
    with environment() as env:
        raster, _ = env.raster(name="grand", width=1001, height=1000)
        aoi, fid = env.aoi()                                 # périmètre minuscule
        dispatcher, _ = env.dispatcher()
        response = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, env.output)))
        assert response.error["code"] == "INVALID_PARAMS", response.error
        assert "1 000 000" in response.error["message"]
        assert env.outputs() == []


# --- Vraie tâche ---------------------------------------------------------------------------
QT_TYPES = (QObject, QgsGeometry, QgsFeature, QgsCoordinateReferenceSystem)


def _plain(value) -> bool:
    if isinstance(value, QT_TYPES):
        return False
    if isinstance(value, (list, tuple)):
        return all(_plain(v) for v in value)
    if isinstance(value, dict):
        return all(_plain(v) for v in value.values())
    return True


def test_real_task_end_to_end():
    with environment() as env:
        raster, source = env.raster()
        aoi, fid = env.aoi()
        source_hash = sha256(source)
        aoi_wkb = bytes(next(aoi.getFeatures()).geometry().asWkb())
        layers_before = sorted(QgsProject.instance().mapLayers())
        dispatcher, audit = env.dispatcher()

        started = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, env.output)))
        assert started.ok and started.job_id, started.error
        job = dispatcher.jobs.get(started.job_id)

        # Étape transmise et générateur suspendu : aucun objet QGIS.
        step = job.handle.step
        assert isinstance(step, PrepareLandcover)
        assert isinstance(step.raster_path, Path) and isinstance(step.output_parent, Path)
        assert isinstance(step.aoi_wkb, bytes) and isinstance(step.aoi_crs_wkt, str)
        assert isinstance(step.rgb_bands, tuple)
        assert isinstance(step.config, PreparationConfig)
        assert step.config.max_pixels == 1_000_000
        local_values = job.generator.gi_frame.f_locals
        assert all(_plain(v) for v in local_values.values()), local_values

        busy = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, env.output)))
        assert busy.error["code"] == "BUSY"

        final = final_response(dispatcher, started.job_id)
        assert final.ok, final.error
        report = final.data
        directory = Path(report["output_directory"])
        manifest = json.loads((directory / "preparation.json").read_text(encoding="utf-8"))
        assert report == manifest                            # résultat = manifeste natif
        assert directory.parent == env.output.resolve()
        assert all((directory / name).is_file() for name in report["files"])

        excluded = report["counts"]["invalid_pixels_inside_aoi"]
        assert excluded >= 1
        assert any(f"{excluded} pixels du périmètre sont exclus" in w for w in final.warnings)
        assert any("sans prouver une absence réelle de donnée" in w for w in final.warnings)

        entries = [e for e in audit.recent(10) if e["tool"] == TOOL and e["ok"]]
        assert len(entries) == 1
        assert sorted(entries[0]["outputs"]) == sorted(
            str(directory / name) for name in report["files"])

        assert sha256(source) == source_hash                 # source inchangée
        assert sorted(QgsProject.instance().mapLayers()) == layers_before
        assert bytes(next(aoi.getFeatures()).geometry().asWkb()) == aoi_wkb
        assert not aoi.isEditable()
        assert QCoreApplication.instance().property(GUARD) in (None, "")


def test_real_task_native_crs_check_stays_active():
    with environment() as env:
        raster, _ = env.raster()                             # GeoTIFF en EPSG:2975
        raster.setCrs(QgsCoordinateReferenceSystem("EPSG:4471"))  # SCR de couche forcé
        aoi, fid = env.aoi(epsg=4471)
        dispatcher, _ = env.dispatcher()
        started = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, env.output)))
        assert started.job_id, started.error                 # contrôles QGIS passés
        final = final_response(dispatcher, started.job_id)
        assert not final.ok
        assert "même SCR" in final.error["message"], final.error
        assert dispatcher.jobs.get(started.job_id).status == "failed"
        assert env.outputs() == []


def test_real_task_cancel_job_uses_existing_infrastructure():
    entered = threading.Event()

    def controlled(*, control, **_kwargs):
        entered.set()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not STOP.is_set():
            control.check_cancelled()
            time.sleep(0.01)
        raise RuntimeError("annulation jamais reçue (test)")

    with environment() as env, patched(preparation, "prepare_native_inputs", controlled):
        raster, _ = env.raster()
        aoi, fid = env.aoi()
        dispatcher, audit = env.dispatcher()
        started = dispatcher.dispatch(request(TOOL, **params(raster, aoi, fid, env.output)))
        assert started.job_id and spin(entered.is_set)
        pending = dispatcher.dispatch(request("cancel_job", job_id=started.job_id))
        assert pending.data["status"] == "running"
        assert pending.data["cancellation_requested"] is True
        final = final_response(dispatcher, started.job_id)
        assert final.error["code"] == "CANCELLED"
        assert env.outputs() == []
        assert [e["error_code"] for e in audit.recent(10) if e["tool"] == TOOL] == ["CANCELLED"]


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in list(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
        else:
            print(f"PASS {name}")
    print(f"{len(tests) - failed} réussis, {failed} échoués")
    sys.exit(1 if failed else 0)
