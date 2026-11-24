"""Outil segment_landcover : vrai registre, vrai Dispatcher, vraie tâche, vrai SLIC.

Nécessite PyQGIS, GDAL, NumPy et scikit-image. Sous pytest sans QGIS, le module est
ignoré. Le Python de QGIS n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" \
        tests/integration/test_segment_landcover_tool.py

Processus QGIS de test isolé : petits GeoTIFF synthétiques, préparation réelle dans un
dossier temporaire. En sortie, même après un échec, les tâches sont arrêtées et leur arrêt
confirmé AVANT la restauration de la propriété Qt du verrou OBIA et la suppression du
dossier ; arrêt non confirmé = processus de test interrompu, rien restauré ni supprimé.
Ni la session QGIS de travail ni l'orthophoto réelle ne sont utilisées.

- test_registry_*, test_policy_*, test_invalid_*, test_params_* : vrai registre et vrai
  Dispatcher, refus avant toute tâche ;
- test_real_* : vraie LandcoverSegmentationTask, vraie persistance (vrai GDAL, vrai SLIC) ;
- test_task_* : vraie tâche, persist_segmentation remplacé par un traitement contrôlé ;
- test_process_* : processus séparés (import du plugin, découverte côté serveur MCP avec
  un client de pont double : ce n'est PAS un parcours MCP stdio/TCP réel).
"""
from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import inspect
import json
import os
import shutil
import subprocess
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
    pytest.importorskip("skimage", reason="scikit-image absent : suite ignorée")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import QgsApplication, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, QObject

_QGS = QgsApplication.instance()
if _QGS is None:
    _QGS = QgsApplication([], True)
    _QGS.initQgis()

import numpy as np  # noqa: E402
from osgeo import gdal, ogr, osr  # noqa: E402

import cynogis.plugin as plugin_mod  # noqa: E402
from cynogis.bridge.protocol import PROTOCOL_VERSION, decode_request  # noqa: E402
from cynogis.core.audit import AuditLog  # noqa: E402
from cynogis.core.dispatcher import Dispatcher  # noqa: E402
from cynogis.core.errors import ErrorCode, ToolError  # noqa: E402
from cynogis.core.jobs import SegmentLandcover  # noqa: E402
from cynogis.core.landcover import PreparationConfig  # noqa: E402
from cynogis.core.policy import PermissionPolicy  # noqa: E402
from cynogis.core.registry import Level, ToolRegistry  # noqa: E402
from cynogis.landcover_processing import persist  # noqa: E402
from cynogis.landcover_processing.prepare import prepare_native_inputs  # noqa: E402
from cynogis.landcover_processing.segment import SlicConfig  # noqa: E402
from cynogis.tools import landcover  # noqa: E402
from cynogis.tools import outputs as outputs_mod  # noqa: E402
from cynogis.tools import tasks as tasks_mod  # noqa: E402
from cynogis.tools.landcover_guard import _PROPERTY_NAME as GUARD  # noqa: E402
from cynogis.tools.tasks import ProcessingExecutor  # noqa: E402

TOOL = "segment_landcover"
REPO = Path(__file__).resolve().parents[2]
PLUGIN_DIR = REPO / "plugin"
X0, Y0, PIXEL, SIZE = 341000.0, 7642400.0, 0.5, 40
GRID = (X0, PIXEL, 0.0, Y0, 0.0, -PIXEL)
INPUTS = ("preparation.json", "image_rgb.tif", "aoi_mask.tif",
          "validity_mask.tif", "analysis_mask.tif")
STOP = threading.Event()


# --- Harnais -------------------------------------------------------------------------------
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


def guard_free() -> bool:
    return QCoreApplication.instance().property(GUARD) in (None, "")


def _wkt(epsg=2975):
    reference = osr.SpatialReference()
    assert reference.ImportFromEPSG(epsg) == 0
    return reference.ExportToWkt()


class Env:
    """Préparation réelle dans un dossier temporaire + dispatchers suivis."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="cynogis_segment_tool_")).resolve()
        # Le projet du processus a pour dossier self.root (setPresetHomePath) :
        # racine OBIA imposée = self.root/mcp_outputs/obia.
        self.obia = self.root / "mcp_outputs" / "obia"
        self.output = self.obia / "segmentations"
        self.output.mkdir(parents=True)
        self.executors = []
        self.prep = self._prepare()

    def _prepare(self) -> Path:
        source = self.root / "source.tif"
        rgb = np.random.default_rng(20261118).integers(0, 255, (3, SIZE, SIZE), np.uint8)
        rgb[0, : SIZE // 2] = 200
        dataset = gdal.GetDriverByName("GTiff").Create(str(source), SIZE, SIZE, 3,
                                                       gdal.GDT_Byte)
        try:
            dataset.SetGeoTransform(GRID)
            dataset.SetProjection(_wkt())
            for index in range(3):
                dataset.GetRasterBand(index + 1).WriteArray(rgb[index])
        finally:
            dataset.Close()
        xmax, ymin = X0 + PIXEL * SIZE, Y0 - PIXEL * SIZE
        aoi = ogr.CreateGeometryFromWkt(
            f"POLYGON (({X0} {ymin}, {xmax} {ymin}, {xmax} {Y0}, {X0} {Y0}, {X0} {ymin}))")
        parent = self.obia / "preparations"
        parent.mkdir()
        report = prepare_native_inputs(
            raster_path=source, aoi_wkb=bytes(aoi.ExportToWkb()), aoi_crs_wkt=_wkt(),
            rgb_bands=[1, 2, 3], output_parent=parent,
            config=PreparationConfig(validity_policy="respect_source_masks"))
        return Path(report["output_directory"])

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

    def fingerprints(self):
        return {name: hashlib.sha256((self.prep / name).read_bytes()).hexdigest()
                for name in INPUTS}


def abort_test_process(message: str) -> None:
    """Arrêt non confirmé : aucun essai ne doit suivre dans ce processus."""
    print(f"ARRÊT DU PROCESSUS DE TEST : {message}", file=sys.stderr, flush=True)
    if __name__ != "__main__":
        pytest.exit(message, returncode=1)
    raise SystemExit(message)


@contextlib.contextmanager
def environment():
    """Nettoyage dans l'ordre : arrêt confirmé, puis verrou, puis dossier."""
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
                f"une tâche n'a pas confirmé son arrêt ; verrou et dossier {env.root} "
                "laissés en place")
        if not guard_free():
            abort_test_process(
                "verrou OBIA encore détenu alors qu'aucune tâche n'est active ; "
                f"non restauré, dossier {env.root} conservé")
        app.setProperty(GUARD, saved)
        if succeeded:
            shutil.rmtree(env.root)
        else:
            print(f"dossier de l'essai conservé : {env.root}", file=sys.stderr, flush=True)


def request(method, **params):
    raw = {"v": PROTOCOL_VERSION, "id": "1", "method": method, "params": params,
           "token": "t"}
    return decode_request(json.dumps(raw).encode())


def params(env, **overrides):
    values = {"preparation_directory": str(env.prep), "output_parent": str(env.output)}
    values.update(overrides)
    return values


def final_response(dispatcher, job_id, timeout=60.0):
    box = {}

    def done():
        box["r"] = dispatcher.dispatch(request("get_job_status", job_id=job_id))
        return box["r"].job_id is None

    assert spin(done, timeout), "job non terminé"
    return box["r"]


def quick_engine(captured):
    """Double de persist : capture la configuration reçue, sans calcul ni fichier."""
    def engine(*, preparation_directory, output_parent, config, control):
        captured.append(config)
        return {"status": "complete", "output_directory": str(output_parent), "files": []}
    return engine


def controlled_engine(entered, mode):
    """Double de persist : progression à 10, puis attente pilotée par l'annulation."""
    def engine(*, output_parent, control, **_kwargs):
        control.checkpoint(10)
        entered.set()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not STOP.is_set():
            if mode == "cancel":
                control.check_cancelled()
            elif control.is_cancelled():  # "late" : sortie complète malgré l'annulation
                return {"status": "complete", "files": [],
                        "output_directory": str(Path(output_parent) / "complet")}
            time.sleep(0.01)
        raise RuntimeError("annulation jamais reçue (test)")
    return engine


# --- 1. Catalogue réel --------------------------------------------------------------------
def test_registry_catalog_matches_signature():
    assert landcover in plugin_mod.TOOL_MODULES
    with environment() as env:
        dispatcher, _ = env.dispatcher()
        spec = dispatcher.registry.get(TOOL)
        assert spec is not None and spec.level == Level.CREATE
        assert spec.handler is landcover.segment_landcover
        assert inspect.isgeneratorfunction(spec.handler)
        signature = inspect.signature(spec.handler).parameters
        assert list(spec.params) == list(signature)
        for name, param in spec.params.items():
            default = signature[name].default
            if default is inspect.Parameter.empty:
                assert param.required, name
            else:
                assert not param.required and param.default == default, name

        catalog = dispatcher.dispatch(request("list_tools")).data["tools"]
        entry = next(e for e in catalog if e["name"] == TOOL)
        assert entry["level"] == int(Level.CREATE)
        schema = entry["input_schema"]
        properties = schema["properties"]
        assert schema["required"] == ["preparation_directory"]  # output_parent facultatif
        assert properties["target_segment_area_m2"]["default"] == 25.0
        assert properties["compactness"]["default"] == 10.0
        assert properties["max_num_iter"] == {
            "type": "integer", "description": properties["max_num_iter"]["description"],
            "minimum": 1, "maximum": 100, "default": 10}
        for name in ("target_segment_area_m2", "compactness"):
            assert properties[name]["type"] == "number"
            assert "minimum" not in properties[name]          # pas de minimum=0 trompeur
        assert schema["additionalProperties"] is False


# --- 2. Permission insuffisante ------------------------------------------------------------
def test_policy_read_only_is_refused():
    with environment() as env:
        dispatcher, _ = env.dispatcher(max_level=Level.READ)
        response = dispatcher.dispatch(request(TOOL, **params(env)))
        assert response.error["code"] == "PERMISSION_DENIED"
        assert response.job_id is None and dispatcher.jobs.running is None
        assert env.outputs() == [] and guard_free()


# --- 3. Configuration transmise ------------------------------------------------------------
def test_params_defaults_and_existing_conventions():
    with environment() as env:
        dispatcher, _ = env.dispatcher()
        captured = []
        with patched(persist, "persist_segmentation", quick_engine(captured)):
            for overrides in ({}, {"target_segment_area_m2": None, "compactness": None,
                                   "max_num_iter": 10.0}):
                started = dispatcher.dispatch(request(TOOL, **params(env, **overrides)))
                assert started.job_id, started.error
                assert final_response(dispatcher, started.job_id).ok
        # Défauts omis, null = défaut, 10.0 normalisé en entier (conventions existantes).
        assert captured == [SlicConfig(), SlicConfig()]
        assert all(type(c) is SlicConfig and type(c.max_num_iter) is int for c in captured)
        assert captured[0] == SlicConfig(25.0, 10.0, 10)


def test_real_custom_configuration_in_manifest():
    with environment() as env:
        dispatcher, _ = env.dispatcher()
        custom = {"target_segment_area_m2": 7.0, "compactness": 12.5, "max_num_iter": 8}
        started = dispatcher.dispatch(request(TOOL, **params(env, **custom)))
        final = final_response(dispatcher, started.job_id)
        assert final.ok, final.error
        assert final.data["configuration"] == custom


# --- 4. Paramètres refusés avant toute tâche -----------------------------------------------
def test_invalid_parameters_create_nothing():
    with environment() as env:
        dispatcher, _ = env.dispatcher()
        a_file = env.root / "fichier.txt"
        a_file.write_text("x", encoding="utf-8")
        inside = env.prep / "sous_dossier"
        inside.mkdir()
        acquired = []
        real_acquire = tasks_mod.acquire_landcover_guard
        cases = {
            "préparation vide": {"preparation_directory": ""},
            "sortie blanche": {"output_parent": "   "},
            "préparation relative": {"preparation_directory": "preparations"},
            "sortie relative": {"output_parent": "segmentations"},
            "préparation absente": {"preparation_directory": str(env.root / "absent")},
            "sortie absente": {"output_parent": str(env.root / "absent")},
            "préparation fichier": {"preparation_directory": str(a_file)},
            "sortie fichier": {"output_parent": str(a_file)},
            "sortie = préparation": {"output_parent": str(env.prep)},
            "sortie dans la préparation": {"output_parent": str(inside)},
            "surface nulle": {"target_segment_area_m2": 0},
            "surface négative": {"target_segment_area_m2": -1.5},
            "compacité nulle": {"compactness": 0.0},
            "surface booléenne": {"target_segment_area_m2": True},
            "itérations booléennes": {"max_num_iter": True},
            "itérations 0": {"max_num_iter": 0},
            "itérations 101": {"max_num_iter": 101},
            "itérations décimales": {"max_num_iter": 10.5},
            "paramètre inconnu": {"sigma": 1},
        }
        with patched(tasks_mod, "acquire_landcover_guard",
                     lambda: acquired.append(1) or real_acquire()):
            for label, override in cases.items():
                response = dispatcher.dispatch(request(TOOL, **params(env, **override)))
                assert not response.ok, label
                assert response.error["code"] == "INVALID_PARAMS", (label, response.error)
                assert response.job_id is None, label
        assert acquired == []                                  # verrou jamais acquis
        assert env.outputs() == [] and list(inside.iterdir()) == []
        assert dispatcher.jobs.running is None and guard_free()


def test_params_helper_rejects_non_json_values():
    with environment() as env:
        prep, out = str(env.prep), str(env.output)
        for bad in (float("nan"), float("inf"), float("-inf"), 10**400, True, "25", None):
            for position in (2, 3):
                values = [prep, out, 25.0, 10.0, 10]
                values[position] = bad
                try:
                    landcover._build_segmentation_step(*values)
                except ToolError as exc:
                    assert exc.code == ErrorCode.INVALID_PARAMS, (bad, position)
                else:
                    raise AssertionError(f"refus attendu : {bad!r} en position {position}")
        for bad in (True, 10.5, 0, 101, None):
            try:
                landcover._build_segmentation_step(prep, out, 25.0, 10.0, bad)
            except ToolError as exc:
                assert exc.code == ErrorCode.INVALID_PARAMS, bad
            else:
                raise AssertionError(f"refus attendu : max_num_iter={bad!r}")
        for bad in (None, 3, b"bytes"):
            try:
                landcover._build_segmentation_step(bad, out, 25.0, 10.0, 10)
            except ToolError as exc:
                assert exc.code == ErrorCode.INVALID_PARAMS, bad
            else:
                raise AssertionError(f"refus attendu : chemin {bad!r}")
        assert env.outputs() == []


# --- 5. Prévalidation : aucune lecture, aucun moteur ---------------------------------------
def _alias(link: Path, target: Path) -> bool:
    """Lien symbolique, sinon jonction Windows ; False si le système refuse les deux."""
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass
    try:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
        return True
    except (ImportError, OSError):
        return False


def test_params_prevalidation_reads_nothing():
    with environment() as env:
        empty = env.root / "preparation_vide"
        empty.mkdir()

        def forbidden(*_args, **_kwargs):
            raise AssertionError("aucune lecture ni calcul attendus à la validation")

        with patched(persist, "persist_segmentation", forbidden), \
                patched(persist, "_load_inputs", forbidden), \
                patched(persist, "_read_json", forbidden):
            # Dossier vide accepté ici : seule la tâche contrôlera son contenu.
            step, _ = landcover._build_segmentation_step(
                str(empty), str(env.output), 25.0, 10.0, 10)
        assert step.preparation_directory == empty and step.output_parent == env.output
        assert env.outputs() == [] and guard_free()

        # Liens créés DANS la racine OBIA : seul le contrôle préparation/sortie est en jeu.
        aliases = {"alias de la préparation": (env.obia / "alias_prep", env.prep),
                   "alias vers l'intérieur": (env.obia / "alias_dedans", env.prep / "x")}
        (env.prep / "x").mkdir()
        tested = []
        for label, (link, target) in aliases.items():
            if not _alias(link, target):
                print(f"alias non testé (système) : {label}")
                continue
            tested.append(label)
            try:
                landcover._build_segmentation_step(
                    str(env.prep), str(link), 25.0, 10.0, 10)
            except ToolError as exc:
                assert exc.code == ErrorCode.INVALID_PARAMS
                assert "dossier de préparation" in exc.message, exc.message
            else:
                raise AssertionError(f"alias non détecté : {label}")
        print(f"alias testés : {tested}")
        for link, _ in aliases.values():
            if link.exists() or link.is_symlink():
                os.rmdir(link)                                  # retire le lien seul
        (env.prep / "x").rmdir()


# --- 6. Générateur suspendu ----------------------------------------------------------------
QT_TYPES = (QObject,)


def _plain(value) -> bool:
    if isinstance(value, (*QT_TYPES, np.ndarray)):
        return False
    if isinstance(value, (list, tuple)):
        return all(_plain(v) for v in value)
    if isinstance(value, dict):
        return all(_plain(v) for v in value.values())
    return True


def test_task_suspended_generator_holds_plain_step():
    entered = threading.Event()
    with environment() as env, patched(persist, "persist_segmentation",
                                       controlled_engine(entered, "cancel")):
        dispatcher, _ = env.dispatcher()
        started = dispatcher.dispatch(request(TOOL, **params(env)))
        assert started.ok and started.job_id, started.error
        job = dispatcher.jobs.get(started.job_id)
        step = job.handle.step
        assert isinstance(step, SegmentLandcover)
        assert step.preparation_directory.is_absolute() and step.output_parent.is_absolute()
        assert type(step.config) is SlicConfig
        local_values = job.generator.gi_frame.f_locals
        assert all(_plain(v) for v in local_values.values()), local_values
        assert spin(entered.is_set)
        dispatcher.dispatch(request("cancel_job", job_id=started.job_id))
        assert final_response(dispatcher, started.job_id).error["code"] == "CANCELLED"


# --- 7 et 8. Bout en bout réel -------------------------------------------------------------
def test_real_end_to_end_with_audit():
    with environment() as env:
        before = env.fingerprints()
        layers_before = sorted(QgsProject.instance().mapLayers())
        dispatcher, audit = env.dispatcher()

        started = dispatcher.dispatch(request(TOOL, **params(env)))
        assert started.ok and started.job_id, started.error
        busy = dispatcher.dispatch(request(TOOL, **params(env)))
        assert busy.error["code"] == "BUSY"

        final = final_response(dispatcher, started.job_id)
        assert final.ok, final.error
        report = final.data
        directory = Path(report["output_directory"])
        manifest = json.loads((directory / "segmentation.json").read_text(encoding="utf-8"))
        assert report == manifest                                # exactement le manifeste
        assert directory.parent == env.output
        assert all((directory / name).is_file() for name in report["files"])
        assert report["diagnostics"]["objects"] >= 1
        assert report["configuration"] == dataclasses.asdict(SlicConfig())

        assert len(final.warnings) == 4
        assert any("objets non classés" in w for w in final.warnings)
        assert any("ne valident pas" in w for w in final.warnings)
        # Le refus BUSY ci-dessus est audité (comportement existant) : une seule réussite.
        entries = [e for e in audit.recent(10) if e["tool"] == TOOL and e["ok"]]
        assert len(entries) == 1
        assert [e["error_code"] for e in audit.recent(10)
                if e["tool"] == TOOL and not e["ok"]] == ["BUSY"]
        assert sorted(entries[0]["outputs"]) == sorted(
            str(directory / name) for name in report["files"])

        assert env.fingerprints() == before
        assert sorted(QgsProject.instance().mapLayers()) == layers_before
        assert guard_free()


def test_real_unsaved_project_fallback_warning_reaches_final_response():
    with environment() as env:
        dispatcher, audit = env.dispatcher()
        fallback = env.root / "repli"
        QgsProject.instance().setPresetHomePath("")
        with patched(outputs_mod, "FALLBACK_DIR", fallback):
            started = dispatcher.dispatch(
                request(TOOL, preparation_directory=str(env.prep)))   # output_parent omis
        assert started.ok and started.job_id, started.error
        final = final_response(dispatcher, started.job_id)
        assert final.ok, final.error
        directory = Path(final.data["output_directory"])
        assert directory.parent == (fallback / "obia").resolve()
        assert len(final.warnings) == 5
        assert final.warnings[0].startswith("Projet sans emplacement local")
        entries = [e for e in audit.recent(10) if e["tool"] == TOOL]
        assert len(entries) == 1 and entries[0]["ok"]
        assert env.outputs() == [] and guard_free()


# --- 9. Préparation incomplète ou manifeste invalide : échec dans la tâche ------------------
def test_real_incomplete_or_invalid_preparation_fails_in_task():
    for damage in ("fichier manquant", "manifeste invalide"):
        with environment() as env:
            if damage == "fichier manquant":
                (env.prep / "analysis_mask.tif").unlink()
            else:
                (env.prep / "preparation.json").write_text("{", encoding="utf-8")
            dispatcher, _ = env.dispatcher()
            started = dispatcher.dispatch(request(TOOL, **params(env)))
            assert started.job_id, (damage, started.error)       # prévalidation passée
            final = final_response(dispatcher, started.job_id)
            assert not final.ok and final.job_id is None, damage  # pas de faux succès
            assert dispatcher.jobs.get(started.job_id).status == "failed", damage
            assert env.outputs() == [], damage
            assert spin(lambda: not env.executors[0]._active) and guard_free(), damage
            print(f"{damage} : {final.error['code']} — {final.error['message'][:80]}")


# --- 10. Progression, BUSY et annulation ----------------------------------------------------
def test_task_progress_busy_then_cancelled():
    entered = threading.Event()
    with environment() as env, patched(persist, "persist_segmentation",
                                       controlled_engine(entered, "cancel")):
        dispatcher, audit = env.dispatcher()
        started = dispatcher.dispatch(request(TOOL, **params(env)))
        assert started.job_id and spin(entered.is_set)

        def progressed():
            status = dispatcher.dispatch(request("get_job_status", job_id=started.job_id))
            return status.job_id and status.data["progress"] == 10.0

        assert spin(progressed)
        assert dispatcher.dispatch(request(TOOL, **params(env))).error["code"] == "BUSY"
        pending = dispatcher.dispatch(request("cancel_job", job_id=started.job_id))
        assert pending.data["status"] == "running"
        assert pending.data["cancellation_requested"] is True
        assert dispatcher.dispatch(request(TOOL, **params(env))).error["code"] == "BUSY"
        final = final_response(dispatcher, started.job_id)
        assert final.error["code"] == "CANCELLED"
        codes = [e["error_code"] for e in audit.recent(10) if e["tool"] == TOOL]
        assert [c for c in codes if c != "BUSY"] == ["CANCELLED"]  # audit terminal unique
        assert codes.count("BUSY") == 2                            # refus audités
        assert env.outputs() == [] and guard_free()


# --- 11. Erreur technique et annulation tardive ---------------------------------------------
def test_task_technical_error_and_late_cancellation_are_preserved():
    with environment() as env:
        def failing(**_kwargs):
            raise OSError("disque plein (test)")

        dispatcher, audit = env.dispatcher()
        with patched(persist, "persist_segmentation", failing):
            started = dispatcher.dispatch(request(TOOL, **params(env)))
            final = final_response(dispatcher, started.job_id)
        assert final.error["code"] == "INTERNAL_ERROR"
        assert "disque plein" in final.error["message"]
        assert dispatcher.jobs.get(started.job_id).status == "failed"

        entered = threading.Event()
        with patched(persist, "persist_segmentation", controlled_engine(entered, "late")):
            started = dispatcher.dispatch(request(TOOL, **params(env)))
            assert spin(entered.is_set)
            dispatcher.dispatch(request("cancel_job", job_id=started.job_id))
            final = final_response(dispatcher, started.job_id)
        assert final.error["code"] == "CANCELLED"
        assert final.error["details"] == {
            "retained_output_directory": str(env.output / "complet"),
            "outputs_loaded": False}
        codes = [e["error_code"] for e in audit.recent(10) if e["tool"] == TOOL]
        assert sorted(codes) == ["CANCELLED", "INTERNAL_ERROR"]  # un audit par job
        assert guard_free()


# --- 12. Processus frais : import du plugin et lecture du catalogue -------------------------
_IMPORT_SCRIPT = r"""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from qgis.core import QgsApplication
app = QgsApplication([], False)
app.initQgis()
import cynogis.plugin as plugin_mod
from cynogis.core.registry import ToolRegistry
registry = ToolRegistry()
for module in plugin_mod.TOOL_MODULES:
    registry.register_module(module)
assert "segment_landcover" in [t["name"] for t in registry.listing()]
engines = ("cynogis.landcover_processing.persist", "cynogis.landcover_processing.segment",
           "skimage", "scipy")
print("catalogue", [m for m in engines if m in sys.modules])
from cynogis.tools import landcover
import shutil
from qgis.core import QgsProject
root = Path(tempfile.mkdtemp()).resolve()
QgsProject.instance().setPresetHomePath(str(root))  # racine OBIA dans le dossier temporaire
out = root / "mcp_outputs" / "obia" / "out"
(root / "prep").mkdir(); out.mkdir(parents=True)
landcover._build_segmentation_step(str(root / "prep"), str(out), 25.0, 10.0, 10)
print("appel", [m for m in engines if m in sys.modules])
shutil.rmtree(root)
"""


def test_process_plugin_import_loads_no_engine():
    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_SCRIPT, str(PLUGIN_DIR)], capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=300, check=False)
    assert result.returncode == 0, result.stderr[-2000:]
    assert "catalogue []" in result.stdout
    # SlicConfig charge segment (léger), jamais les moteurs de calcul.
    assert "appel ['cynogis.landcover_processing.segment']" in result.stdout


# --- 13. Découverte côté serveur MCP (client de pont double) --------------------------------
_SERVER_SCRIPT = r"""
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[3])  # server/src, comme pythonpath de pytest
from cynogis_server import app
from cynogis_server.client import BridgeError, BridgeResult
catalog = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

class DoubleBridge:
    def _read_connection(self):
        raise BridgeError("QGIS_UNAVAILABLE", "double sans connexion")
    async def call(self, method, params=None):
        assert method == "list_tools", method
        return BridgeResult({"tools": catalog})

app._client = DoubleBridge()
app._specs_cache = None
app.CACHE_FILE = Path(sys.argv[2])  # jamais le cache réel de l'utilisateur
tools = asyncio.run(app.list_tools())
tool = next(t for t in tools if t.name == "segment_landcover")
print(json.dumps({"schema": tool.inputSchema, "read_only": tool.annotations.readOnlyHint,
                  "destructive": tool.annotations.destructiveHint}))
"""


def test_process_server_discovers_tool_from_catalog():
    venv_python = REPO / ".venv" / "Scripts" / "python.exe"
    if not venv_python.is_file():
        print("venv absent : découverte côté serveur non testée")
        return
    with environment() as env:
        dispatcher, _ = env.dispatcher()
        catalog = dispatcher.dispatch(request("list_tools")).data["tools"]
        catalog_file = env.root / "catalogue.json"
        catalog_file.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
        cache_file = env.root / "tools_cache.json"
        # Environnement sans PYTHONHOME/PYTHONPATH/PYTHONEXECUTABLE posés par QGIS : le
        # Python du venv ne charge pas la bibliothèque standard de QGIS et reconnaît son
        # venv. (-I est exclu ici : le lanceur Windows du venv perdrait ses paquets.)
        clean_env = {k: v for k, v in os.environ.items()
                     if k.upper() not in ("PYTHONHOME", "PYTHONPATH", "PYTHONEXECUTABLE")}
        result = subprocess.run(
            [str(venv_python), "-c", _SERVER_SCRIPT, str(catalog_file), str(cache_file),
             str(REPO / "server" / "src")],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120, check=False, env=clean_env)
        assert result.returncode == 0, result.stderr[-2000:]
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        expected = next(e for e in catalog if e["name"] == TOOL)["input_schema"]
        assert seen["schema"] == expected
        assert seen["read_only"] is False and seen["destructive"] is False
        assert json.loads(cache_file.read_text(encoding="utf-8")) == catalog


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
