"""Segmentation OBIA raccordée aux jobs : vraie LandcoverSegmentationTask dans QGIS.

Nécessite PyQGIS, GDAL, NumPy et scikit-image. Sous pytest sans QGIS, le module est
ignoré. Le Python de QGIS n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" \
        tests/integration/test_landcover_segmentation_task.py

Processus QGIS de test isolé, fichiers dans des dossiers temporaires ; aucun projet ni
plugin de la session de travail n'est touché. Familles :
- test_real_* : vraie préparation puis vraie persistance (vrai GDAL, vrai SLIC) dans une
  vraie tâche QgsTaskManager, vrai ProcessingExecutor et vrai JobManager/Dispatcher ;
- test_task_* : vraie tâche, traitement contrôlé (persist_segmentation ou
  prepare_native_inputs remplacés le temps de l'essai, pilotés par événements) ;
- test_double_* : constructeur de tâche ou gestionnaire de tâches remplacés par des doubles.

Chaque essai arrête ses tâches avant de restaurer la propriété Qt du verrou. Si l'arrêt
n'est pas confirmé, la suite s'interrompt sans effacer le verrou (diagnostics affichés).
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path
from types import SimpleNamespace

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plugin"))
else:
    import pytest

    pytest.importorskip("qgis.core", exc_type=ImportError)
    pytest.importorskip("skimage", reason="scikit-image absent : suite ignorée")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication

_QGS = QgsApplication.instance()
if _QGS is None:
    _QGS = QgsApplication([], True)
    _QGS.initQgis()

import numpy as np  # noqa: E402
from osgeo import gdal, ogr, osr  # noqa: E402
from qgis.core import QgsProject, QgsTask  # noqa: E402

from cynogis.bridge.protocol import PROTOCOL_VERSION, decode_request  # noqa: E402
from cynogis.core.audit import AuditLog  # noqa: E402
from cynogis.core.dispatcher import Dispatcher, ToolResult  # noqa: E402
from cynogis.core.errors import ErrorCode, ToolError  # noqa: E402
from cynogis.core.jobs import JobManager, PrepareLandcover, SegmentLandcover  # noqa: E402
from cynogis.core.landcover import PreparationConfig  # noqa: E402
from cynogis.core.landcover_execution import SegmentationCancelledError  # noqa: E402
from cynogis.core.registry import Level, ToolRegistry, tool  # noqa: E402
from cynogis.landcover_processing import persist  # noqa: E402
from cynogis.landcover_processing import prepare as preparation  # noqa: E402
from cynogis.landcover_processing.segment import SlicConfig  # noqa: E402
from cynogis.tools import tasks as tasks_mod  # noqa: E402
from cynogis.tools.landcover_guard import _PROPERTY_NAME as GUARD  # noqa: E402
from cynogis.tools.landcover_segmentation_tasks import LandcoverSegmentationTask  # noqa: E402
from cynogis.tools.landcover_tasks import LandcoverPreparationTask  # noqa: E402
from cynogis.tools.tasks import ProcessingExecutor  # noqa: E402

PLUGIN_DIR = Path(__file__).resolve().parents[2] / "plugin"
X0, Y0, PIXEL = 341000.0, 7642400.0, 0.5
GRID = (X0, PIXEL, 0.0, Y0, 0.0, -PIXEL)
SIZE = 40
STOP = threading.Event()  # débloque tout traitement contrôlé au nettoyage
EXECUTORS: list[ProcessingExecutor] = []
MAIN_THREAD = threading.main_thread()


# --- Harnais -----------------------------------------------------------------------------
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


def _abort(message: str) -> None:
    """Arrêt non confirmé : interrompre toute la suite, sans toucher au verrou."""
    print(message, file=sys.stderr)
    if "pytest" in sys.modules:
        import pytest

        pytest.exit(message, returncode=3)
    raise SystemExit(message)


def stop_tasks(executor, timeout=30.0) -> bool:
    for task in list(executor._active):
        if isinstance(task, (LandcoverPreparationTask, LandcoverSegmentationTask)):
            task.cancel()
    return spin(lambda: not executor._active, timeout)


@contextlib.contextmanager
def isolated():
    """Verrou libre au départ ; en sortie, arrêt confirmé PUIS propriété restaurée."""
    app = QCoreApplication.instance()
    saved = app.property(GUARD)
    app.setProperty(GUARD, "")
    STOP.clear()
    try:
        yield
    finally:
        STOP.set()
        stopped = all([stop_tasks(executor) for executor in EXECUTORS])
        if not stopped:
            remaining = [(type(task).__name__, int(task.status()))
                         for executor in EXECUTORS for task in executor._active]
            _abort(f"Arrêt des tâches non confirmé : {remaining}. Verrou laissé en l'état.")
        EXECUTORS.clear()
        app.setProperty(GUARD, saved)


def new_executor() -> ProcessingExecutor:
    executor = ProcessingExecutor()
    EXECUTORS.append(executor)
    return executor


def wait_done(job, executor):
    assert spin(lambda: job.status != "running"), "la tâche réelle n'a pas terminé"
    assert spin(lambda: not executor._active), "la tâche n'a pas été libérée"


def expect_busy(start):
    try:
        start()
    except ToolError as exc:
        assert exc.code == ErrorCode.BUSY
    else:
        raise AssertionError("BUSY attendu")


# --- Entrées : vraie préparation sur un GeoTIFF temporaire -------------------------------
def _wkt():
    reference = osr.SpatialReference()
    assert reference.ImportFromEPSG(2975) == 0
    return reference.ExportToWkt()


def _aoi_wkb():
    xmax, ymin = X0 + PIXEL * SIZE, Y0 - PIXEL * SIZE
    wkt = f"POLYGON (({X0} {ymin}, {xmax} {ymin}, {xmax} {Y0}, {X0} {Y0}, {X0} {ymin}))"
    return bytes(ogr.CreateGeometryFromWkt(wkt).ExportToWkb())


def _prepare_step(sample) -> PrepareLandcover:
    return PrepareLandcover(
        raster_path=sample["source"], aoi_wkb=_aoi_wkb(), aoi_crs_wkt=_wkt(),
        rgb_bands=(1, 2, 3), output_parent=sample["prep_parent"],
        config=PreparationConfig(validity_policy="respect_source_masks"))


def make_sample(prefix: str, *, prepared: bool = True) -> dict:
    root = Path(tempfile.mkdtemp(prefix=prefix)).resolve()
    source = root / "source.tif"
    rgb = np.random.default_rng(20261118).integers(0, 255, (3, SIZE, SIZE), dtype=np.uint8)
    rgb[0, : SIZE // 2] = 200
    dataset = gdal.GetDriverByName("GTiff").Create(str(source), SIZE, SIZE, 3, gdal.GDT_Byte)
    try:
        dataset.SetGeoTransform(GRID)
        dataset.SetProjection(_wkt())
        for index in range(3):
            dataset.GetRasterBand(index + 1).WriteArray(rgb[index])
    finally:
        dataset.Close()
    sample = {"root": root, "source": source, "prep_parent": root / "preparations",
              "out": root / "segmentations"}
    sample["prep_parent"].mkdir()
    sample["out"].mkdir()
    if prepared:
        step = _prepare_step(sample)
        report = preparation.prepare_native_inputs(
            raster_path=step.raster_path, aoi_wkb=step.aoi_wkb, aoi_crs_wkt=step.aoi_crs_wkt,
            rgb_bands=list(step.rgb_bands), output_parent=step.output_parent,
            config=step.config)
        sample["prep"] = Path(report["output_directory"])
    return sample


def segment_step(sample, prep=None) -> SegmentLandcover:
    return SegmentLandcover(
        preparation_directory=prep or sample["prep"], output_parent=sample["out"],
        config=SlicConfig(target_segment_area_m2=4.0))


def snapshot(directory: Path) -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.iterdir() if p.is_file()}


def start_job(sample, executor=None):
    executor = executor or new_executor()
    manager = JobManager(executor)
    published, finished = [], []

    def generator():
        report = yield segment_step(sample)
        published.append(report)
        return report

    gen = generator()
    job = manager.start("segmentation_test", gen, next(gen),
                        lambda r, e: finished.append((r, e, threading.current_thread())))
    assert isinstance(job.handle, LandcoverSegmentationTask)
    return executor, manager, job, published, finished


def controlled_until_cancelled(entered):
    """Double de persist : progression réelle à 10 puis attente de l'annulation."""
    def controlled(*, control, **_kwargs):
        control.checkpoint(10)
        entered.set()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not STOP.is_set():
            control.check_cancelled()  # lève SegmentationCancelledError
            time.sleep(0.01)
        raise RuntimeError("annulation jamais reçue (test)")
    return controlled


# --- 10. Vraie tâche, vraie persistance --------------------------------------------------
def test_real_task_segmentation_success():
    sample = make_sample("cynogis_seg_ok_")
    source = snapshot(sample["prep"])
    layers = set(QgsProject.instance().mapLayers())
    workers = []
    real = persist.persist_segmentation

    def spy(**kwargs):
        workers.append(threading.current_thread())
        return real(**kwargs)

    with isolated(), patched(persist, "persist_segmentation", spy):
        executor, _, job, published, finished = start_job(sample)
        assert not guard_free()
        wait_done(job, executor)
        assert guard_free()

    assert job.status == "done" and len(finished) == 1
    report, error, callback_thread = finished[0]
    assert error is None and published == [report]
    run = Path(report["output_directory"])
    assert json.loads((run / "segmentation.json").read_text(encoding="utf-8")) == report
    assert sorted(p.name for p in run.iterdir()) == ["segmentation.json", "segments.tif"]
    assert snapshot(sample["prep"]) == source
    assert set(QgsProject.instance().mapLayers()) == layers  # aucune couche ajoutée
    assert callback_thread is MAIN_THREAD                      # finished() : thread principal
    assert workers and workers[0] is not MAIN_THREAD           # calcul hors thread principal


# --- 11. Progression intermédiaire puis annulation pendant run ---------------------------
def test_task_progress_then_cancel_during_run():
    sample = make_sample("cynogis_seg_cancel_")
    entered = threading.Event()
    with isolated(), patched(persist, "persist_segmentation",
                             controlled_until_cancelled(entered)):
        executor, manager, job, published, finished = start_job(sample)
        assert spin(entered.is_set)
        assert spin(lambda: manager.status(job)["progress"] == 10.0)
        manager.cancel(job, "Annulation demandée.")
        assert job.status == "running" and not guard_free()   # attente du vrai retour
        wait_done(job, executor)
        assert guard_free()

    assert job.status == "cancelled" and published == []
    (_, error, _), = finished
    assert error.code == ErrorCode.CANCELLED


# --- 12. Annulation en file d'attente -----------------------------------------------------
def test_task_cancel_while_queued():
    sample = make_sample("cynogis_seg_queued_")
    pool = QgsApplication.taskManager().threadPool()
    saved_threads = pool.maxThreadCount()
    blocker_running, blocker_release = threading.Event(), threading.Event()

    def block(_task):
        blocker_running.set()
        deadline = time.monotonic() + 20
        while not (blocker_release.is_set() or STOP.is_set()) and time.monotonic() < deadline:
            time.sleep(0.01)
        return True

    blocker = QgsTask.fromFunction("cynogis test : occupe le pool", block)
    try:
        with isolated(), patched(persist, "persist_segmentation",
                                 lambda **_kw: {"status": "complete"}):
            pool.setMaxThreadCount(1)
            assert QgsApplication.taskManager().addTask(blocker)
            assert spin(blocker_running.is_set)
            executor, manager, job, published, finished = start_job(sample)
            task = job.handle
            assert task.status() == QgsTask.TaskStatus.Queued
            assert not guard_free()                            # en file : déjà détenu
            deliveries = []
            real_done = task.done
            task.done = lambda v, e: (deliveries.append(e), real_done(v, e))

            manager.cancel(job, "Annulation en file.")
            synchronous = job.status != "running"              # callback éventuellement immédiat
            if not spin(lambda: job.status != "running", timeout=5):
                blocker_release.set()
            wait_done(job, executor)
            assert guard_free()
            spin(lambda: False, timeout=0.2)                   # aucun second callback tardif
            print(f"annulation en file : callback {'synchrone' if synchronous else 'différé'}")

        assert job.status == "cancelled" and published == []
        assert len(deliveries) == 1 and len(finished) == 1
        assert isinstance(deliveries[0], SegmentationCancelledError)
    finally:
        blocker_release.set()
        spin(lambda: blocker.status() in (QgsTask.TaskStatus.Complete,
                                          QgsTask.TaskStatus.Terminated))
        pool.setMaxThreadCount(saved_threads)


# --- 13. Suivi vidé et verrou libéré dans chaque terminaison ------------------------------
def _scenario_engine(kind, out, entered):
    def engine(*, control, **_kwargs):
        if kind == "success":
            return {"status": "complete", "output_directory": str(out)}
        if kind == "error":
            raise OSError("disque plein (test)")
        entered.set()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not STOP.is_set():
            if kind == "cancel":
                control.check_cancelled()
            elif control.is_cancelled():  # "late" : sortie complète malgré l'annulation
                return {"status": "complete", "output_directory": str(out / "complet")}
            time.sleep(0.01)
        raise RuntimeError("scénario non débloqué (test)")
    return engine


def test_task_every_termination_releases_tracking_and_guard():
    expected = {"success": "done", "error": "failed", "cancel": "cancelled", "late": "cancelled"}
    for kind, status in expected.items():
        sample = make_sample(f"cynogis_seg_{kind}_")
        entered = threading.Event()
        with isolated(), patched(persist, "persist_segmentation",
                                 _scenario_engine(kind, sample["out"], entered)):
            executor, manager, job, published, finished = start_job(sample)
            if kind in ("cancel", "late"):
                assert spin(entered.is_set)
                manager.cancel(job, "Annulation demandée.")
            wait_done(job, executor)
            assert executor._active == set() and guard_free(), kind

        assert job.status == status, kind
        assert len(finished) == 1, kind
        if kind == "late":
            (_, error, _), = finished
            assert error.details == {
                "retained_output_directory": str(sample["out"] / "complet"),
                "outputs_loaded": False}
            assert published == [] and job.generator.gi_frame is None
        elif kind != "success":
            assert published == [], kind


# --- 14. Échec de forget : FAILED, pas de libération forcée -------------------------------
def test_task_forget_failure_fails_without_forced_release():
    sample = make_sample("cynogis_seg_forget_")
    real_acquire = tasks_mod.acquire_landcover_guard

    def acquire_with_failing_release():
        real_acquire()                                     # vrai propriétaire posé

        def release():
            raise RuntimeError("libération du verrou impossible (double)")

        return release

    def failing(**_kwargs):
        raise OSError("calcul en échec (test)")

    with isolated(), patched(tasks_mod, "acquire_landcover_guard",
                             acquire_with_failing_release), \
            patched(persist, "persist_segmentation", failing):
        executor, manager, job, published, finished = start_job(sample)
        assert spin(lambda: job.status != "running"), "tâche non terminée"
        assert executor._active == set()                   # retrait du suivi effectué
        assert not guard_free()                            # aucun déverrouillage forcé
        expect_busy(lambda: new_executor().start(segment_step(sample), lambda _v, _e: None))

    assert job.status == "failed" and manager.running is None
    (_, error, _), = finished
    assert type(error) is RuntimeError and "libération du verrou impossible" in str(error)
    assert isinstance(error.__cause__, OSError)            # erreur initiale conservée
    assert published == []


# --- 15. Exclusion croisée préparation / segmentation -------------------------------------
def _blocking(entered, allow, result):
    def engine(*, control, **_kwargs):
        entered.set()
        deadline = time.monotonic() + 20
        while not (allow.is_set() or STOP.is_set()) and time.monotonic() < deadline:
            time.sleep(0.01)                               # ignore l'annulation un temps
        control.check_cancelled()
        return result
    return engine


def _run_other(executor, step):
    delivered = []
    executor.start(step, lambda value, error: delivered.append((value, error)))
    assert spin(lambda: delivered and not executor._active)
    return delivered


def test_task_preparation_and_segmentation_exclude_each_other():
    sample = make_sample("cynogis_seg_cross_")
    quick_prepare = {"status": "complete", "output_directory": str(sample["prep_parent"])}
    quick_segment = {"status": "complete", "output_directory": str(sample["out"])}

    # Segmentation en cours : la préparation d'un autre exécuteur est refusée.
    entered, allow = threading.Event(), threading.Event()
    with isolated(), patched(persist, "persist_segmentation",
                             _blocking(entered, allow, quick_segment)), \
            patched(preparation, "prepare_native_inputs", lambda **_kw: quick_prepare):
        executor, manager, job, _, _ = start_job(sample)
        other = new_executor()
        assert spin(entered.is_set)
        expect_busy(lambda: other.start(_prepare_step(sample), lambda _v, _e: None))
        manager.cancel(job, "Annulation demandée.")
        expect_busy(lambda: other.start(_prepare_step(sample), lambda _v, _e: None))
        assert other._active == set() and job.status == "running"
        allow.set()
        wait_done(job, executor)
        assert job.status == "cancelled" and guard_free()
        assert _run_other(other, _prepare_step(sample)) == [(quick_prepare, None)]

    # Préparation en cours : la segmentation d'un autre exécuteur est refusée.
    entered, allow = threading.Event(), threading.Event()
    with isolated(), patched(preparation, "prepare_native_inputs",
                             _blocking(entered, allow, quick_prepare)), \
            patched(persist, "persist_segmentation", lambda **_kw: quick_segment):
        first = new_executor()
        manager = JobManager(first)

        def prepare_job():
            yield _prepare_step(sample)

        gen = prepare_job()
        job = manager.start("preparation_test", gen, next(gen), lambda r, e: (r, e))
        other = new_executor()
        assert spin(entered.is_set)
        expect_busy(lambda: other.start(segment_step(sample), lambda _v, _e: None))
        manager.cancel(job, "Annulation demandée.")
        expect_busy(lambda: other.start(segment_step(sample), lambda _v, _e: None))
        assert other._active == set()
        allow.set()
        wait_done(job, first)
        assert job.status == "cancelled" and guard_free()
        assert _run_other(other, segment_step(sample)) == [(quick_segment, None)]


# --- 16. Refus du constructeur et de l'enregistrement -------------------------------------
class RefusingTaskManager:
    def __init__(self, mode):
        self.mode, self.calls = mode, 0

    def addTask(self, task, priority=0):
        self.calls += 1
        if self.mode == "raise":
            raise TypeError("argument refusé (double)")
        return 0


def test_double_constructor_and_registration_refusals_release_guard():
    sample = make_sample("cynogis_seg_refus_", prepared=False)
    step = SegmentLandcover(sample["root"], sample["out"], SlicConfig())

    def broken(*_args, **_kwargs):
        raise RuntimeError("constructeur refusé (double)")

    with isolated(), patched(tasks_mod, "LandcoverSegmentationTask", broken):
        executor = new_executor()
        try:
            executor.start(step, lambda _v, _e: None)
        except RuntimeError as exc:
            assert "constructeur refusé" in str(exc)
        else:
            raise AssertionError("échec attendu")
        assert guard_free() and executor._active == set()

    for mode in ("zero", "raise"):
        manager = RefusingTaskManager(mode)
        fake_app = SimpleNamespace(taskManager=lambda manager=manager: manager)
        with isolated(), patched(tasks_mod, "QgsApplication", fake_app):
            executor = new_executor()
            try:
                executor.start(step, lambda _v, _e: None)
            except (RuntimeError, TypeError):
                pass
            else:
                raise AssertionError("refus attendu")
            assert manager.calls == 1, mode
            assert guard_free() and executor._active == set(), mode


# --- 17. Détachement d'un vrai job de segmentation ----------------------------------------
def _req(method, **params):
    raw = {"v": PROTOCOL_VERSION, "id": "1", "method": method, "params": params, "token": "t"}
    return decode_request(json.dumps(raw).encode())


def make_dispatcher(name, body, audit_dir):
    body.__name__ = body.__qualname__ = name
    body.__doc__ = "Segmentation OBIA de test."
    registry = ToolRegistry()
    registry.register(tool(level=Level.CREATE)(body))
    executor = new_executor()
    audit = AuditLog(audit_dir)
    return Dispatcher(registry, audit=audit, executor=executor), executor, audit


def test_task_detached_segmentation_job():
    sample = make_sample("cynogis_seg_detach_")
    entered, allow = threading.Event(), threading.Event()
    old_published, new_published = [], []

    def old_tool():
        report = yield segment_step(sample)
        old_published.append(report)
        return report

    def new_tool():
        report = yield segment_step(sample)
        new_published.append(report)
        return report

    quick = {"status": "complete", "output_directory": str(sample["out"])}
    with isolated(), patched(persist, "persist_segmentation", _blocking(entered, allow, quick)):
        old, old_executor, old_audit = make_dispatcher("seg_ancien", old_tool,
                                                       sample["root"] / "audit_ancien")
        new, _, _ = make_dispatcher("seg_nouveau", new_tool, sample["root"] / "audit_nouveau")

        old_job_id = old.dispatch(_req("seg_ancien")).job_id
        assert old_job_id and spin(entered.is_set)
        old_job = old.jobs.get(old_job_id)
        old.jobs.detach_finishers()
        old.jobs.cancel_all("Déchargement du plugin.")
        for _ in range(3):
            assert new.dispatch(_req("seg_nouveau")).error["code"] == "BUSY"
            spin(lambda: False, timeout=0.1)
        assert old_job.status == "running" and not guard_free()

        allow.set()
        wait_done(old_job, old_executor)
        assert old_job.status == "cancelled" and guard_free()
        diagnostic = old.dispatch(_req("get_job_status", job_id=old_job_id))
        assert diagnostic.ok is False and diagnostic.error["code"] == "CANCELLED"
        assert old_published == [] and old_audit.recent(10) == []

        started = new.dispatch(_req("seg_nouveau"))
        assert started.job_id and spin(lambda: new.jobs.running is None)
        final = new.dispatch(_req("get_job_status", job_id=started.job_id))
        assert final.ok and new_published == [final.data]
        assert old_published == []


# --- 18. Préparation puis segmentation dans un même job -----------------------------------
def test_real_chained_preparation_then_segmentation():
    sample = make_sample("cynogis_seg_chain_", prepared=False)
    between, guard_after_start = [], []

    def chained():
        prepared = yield _prepare_step(sample)
        between.append(guard_free())                       # libéré entre les deux étapes
        report = yield segment_step(sample, Path(prepared["output_directory"]))
        run = Path(report["output_directory"])
        return ToolResult(report, outputs=[str(run / name) for name in report["files"]])

    with isolated():
        dispatcher, executor, audit = make_dispatcher("chaine_obia", chained,
                                                      sample["root"] / "audit")
        real_start = executor.start

        def recording_start(step, done):
            handle = real_start(step, done)
            guard_after_start.append((type(step).__name__, guard_free()))
            return handle

        executor.start = recording_start
        job_id = dispatcher.dispatch(_req("chaine_obia")).job_id
        assert job_id
        assert spin(lambda: dispatcher.jobs.running is None, timeout=60)
        assert spin(lambda: not executor._active)
        assert guard_free()
        first = dispatcher.dispatch(_req("get_job_status", job_id=job_id))
        second = dispatcher.dispatch(_req("get_job_status", job_id=job_id))

    assert guard_after_start == [("PrepareLandcover", False), ("SegmentLandcover", False)]
    assert between == [True]
    assert first.ok and first.error is None and second.data == first.data
    run = Path(first.data["output_directory"])
    assert json.loads((run / "segmentation.json").read_text(encoding="utf-8")) == first.data
    entries = audit.recent(10)
    assert len(entries) == 1 and entries[0]["ok"] is True  # une seule réponse finale
    assert sorted(Path(p).name for p in entries[0]["outputs"]) == [
        "segmentation.json", "segments.tif"]


# --- 19. Démarrage du plugin sans le moteur de segmentation -------------------------------
_IMPORT_SCRIPT = r"""
import sys
sys.path.insert(0, sys.argv[1])
from cynogis import plugin  # noqa: F401
import cynogis.tools.tasks  # noqa: F401
loaded = [name for name in ("cynogis.landcover_processing.persist",
                            "cynogis.landcover_processing.segment", "skimage")
          if name in sys.modules]
print("raccordement", "cynogis.tools.landcover_segmentation_tasks" in sys.modules)
print("chargés", loaded)
"""


def test_real_plugin_import_does_not_load_engine():
    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_SCRIPT, str(PLUGIN_DIR)], capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=300, check=False)
    assert result.returncode == 0, result.stderr[-2000:]
    assert "raccordement True" in result.stdout
    assert "chargés []" in result.stdout


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
