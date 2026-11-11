"""LandcoverPreparationTask.finished() lorsque forget() échoue.

Nécessite PyQGIS. Sous pytest sans QGIS, le module est ignoré. Le Python de QGIS
n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" \
        tests/integration/test_landcover_task_finished.py

- test_double_* : vraie classe LandcoverPreparationTask, jamais enregistrée dans
  QgsTaskManager ; finished() appelé directement ; forget/done/isCanceled en doubles ;
- test_jobmanager_double_* : vrai JobManager, exécuteur double qui renvoie la tâche ;
- test_real_task_* : vraie tâche dans QgsTaskManager, vrai ProcessingExecutor,
  traitement contrôlé ; libération du verrou remplacée par un double qui échoue.

Processus QGIS de test isolé : propriété Qt du verrou restaurée et tâches arrêtées en
sortie, même après un échec. Ce correctif ne récupère pas le répertoire de sortie après
une erreur de finalisation ; aucun essai ne le prétend.
"""
from __future__ import annotations

import contextlib
import os
import sys
import time
import traceback
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plugin"))
else:
    import pytest

    pytest.importorskip("qgis.core", exc_type=ImportError)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication

_QGS = QgsApplication.instance()
if _QGS is None:
    _QGS = QgsApplication([], True)
    _QGS.initQgis()

from cynogis.core.errors import ErrorCode, ToolError  # noqa: E402
from cynogis.core.jobs import JobManager, PrepareLandcover  # noqa: E402
from cynogis.core.landcover import PreparationConfig  # noqa: E402
from cynogis.core.landcover_execution import PreparationCancelledError  # noqa: E402
from cynogis.landcover_processing import prepare as preparation  # noqa: E402
from cynogis.tools import landcover_guard as guard_mod  # noqa: E402
from cynogis.tools import tasks as tasks_mod  # noqa: E402
from cynogis.tools.landcover_tasks import LandcoverPreparationTask  # noqa: E402

GUARD = guard_mod._PROPERTY_NAME


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


def step():
    return PrepareLandcover(
        raster_path=Path("absent.tif"), aoi_wkb=b"", aoi_crs_wkt="",
        rgb_bands=(1, 2, 3), output_parent=Path("."),
        config=PreparationConfig(validity_policy="respect_source_masks"))


class Recorder:
    """forget/done en doubles ; forget lève forget_error s'il est fourni."""

    def __init__(self, forget_error=None):
        self.forget_error = forget_error
        self.forgotten, self.delivered = [], []

    def forget(self, task):
        self.forgotten.append(task)
        if self.forget_error is not None:
            raise self.forget_error

    def done(self, value, error):
        self.delivered.append((value, error))


def make_task(recorder, *, result=None, error=None, cancelled=False):
    task = LandcoverPreparationTask(step(), recorder.done, recorder.forget)
    task.result, task.error = result, error
    task.isCanceled = lambda: cancelled                    # double : pas de tâche lancée
    return task


# --- 1. forget() réussit : comportement inchangé -------------------------------------------
def test_double_forget_ok_paths_unchanged():
    report = {"status": "complete", "output_directory": "sortie"}

    rec = Recorder()
    task = make_task(rec, result=report)
    task.finished(True)
    assert rec.forgotten == [task] and rec.delivered == [(report, None)]

    rec = Recorder()
    task = make_task(rec, result=report, cancelled=True)
    task.finished(True)
    (value, error), = rec.delivered
    assert value is report and type(error) is PreparationCancelledError

    original = OSError("disque plein")
    rec = Recorder()
    task = make_task(rec, error=original)
    task.finished(False)
    assert rec.delivered == [(None, original)]

    rec = Recorder()
    task = make_task(rec)                                   # ni résultat ni erreur
    task.finished(False)
    (value, error), = rec.delivered
    assert value is None and type(error) is RuntimeError


# --- 2. forget() lève après un calcul réussi -----------------------------------------------
def test_double_forget_failure_after_success():
    cleanup = ValueError("libération impossible")
    rec = Recorder(cleanup)
    task = make_task(rec, result={"status": "complete", "output_directory": "sortie"})
    task.finished(True)

    assert len(rec.forgotten) == 1
    (value, error), = rec.delivered                         # exactement une fois
    assert value is None                                    # résultat non transmis
    assert type(error) is RuntimeError
    assert "libération impossible" in str(error) and "ValueError" in str(error)
    assert error.__cause__ is cleanup


# --- 3. forget() lève après PreparationCancelledError ----------------------------------------
def test_double_forget_failure_after_cancellation_error():
    cancelled = PreparationCancelledError("Préparation OBIA annulée.")
    cleanup = ValueError("libération impossible")
    rec = Recorder(cleanup)
    task = make_task(rec, error=cancelled, cancelled=True)
    task.finished(False)

    (value, error), = rec.delivered
    assert value is None
    assert type(error) is RuntimeError                      # pas une annulation propre
    assert not isinstance(error, PreparationCancelledError)
    assert error.__cause__ is cancelled                     # erreur initiale accessible
    assert "libération impossible" in str(error)


def test_double_forget_failure_with_cancel_flag_only():
    # Annulation signalée par isCanceled() seul : aucune PreparationCancelledError
    # n'existe encore, la cause est donc l'erreur de forget().
    cleanup = ValueError("libération impossible")
    rec = Recorder(cleanup)
    task = make_task(rec, result={"status": "complete"}, cancelled=True)
    task.finished(True)

    (value, error), = rec.delivered
    assert value is None and type(error) is RuntimeError
    assert error.__cause__ is cleanup


# --- 4. calcul et forget() échouent --------------------------------------------------------
def test_double_compute_and_forget_failures():
    original = OSError("disque plein")
    cleanup = ValueError("libération impossible")
    rec = Recorder(cleanup)
    task = make_task(rec, error=original)
    task.finished(False)

    (value, error), = rec.delivered
    assert value is None and type(error) is RuntimeError
    assert "disque plein" in str(error) and "OSError" in str(error)
    assert "libération impossible" in str(error) and "ValueError" in str(error)
    assert error.__cause__ is original


# --- 5. second appel à finished() ----------------------------------------------------------
def test_double_second_finished_is_ignored():
    for forget_error in (None, ValueError("libération impossible")):
        rec = Recorder(forget_error)
        task = make_task(rec, result={"status": "complete"})
        task.finished(True)
        task.finished(True)
        task.finished(False)
        assert len(rec.forgotten) == 1 and len(rec.delivered) == 1


# --- 6. vrai JobManager, exécuteur double --------------------------------------------------
class TaskExecutor:
    """Crée la vraie classe de tâche sans l'enregistrer ; le test appelle finished()."""

    def __init__(self, forget_error):
        self.forget_error, self.tasks, self.cancelled = forget_error, [], []

    def start(self, step, done):
        def forget(_task):
            raise self.forget_error

        task = LandcoverPreparationTask(step, done, forget)
        self.tasks.append(task)
        return task

    def progress(self, handle):
        return 0.0

    def cancel(self, handle):
        self.cancelled.append(handle)

    def pause(self, resume):
        raise AssertionError("inattendu")


def _obia_job(manager, published):
    def tool():
        result = yield step()
        published.append(result)
        return result

    gen = tool()
    return manager.start("obia_test", gen, next(gen), lambda r, e: (r, e))


def test_jobmanager_double_finalization_error_fails_job():
    for scenario in ("success", "cancel_requested", "detached"):
        executor = TaskExecutor(ValueError("libération impossible"))
        manager = JobManager(executor)
        published = []
        job = _obia_job(manager, published)
        task = executor.tasks[-1]
        task.isCanceled = lambda: False
        task.result = {"status": "complete", "output_directory": "sortie"}

        if scenario == "cancel_requested":
            manager.cancel(job, "Annulation demandée.")
            assert job.status == "running"
            task.result, task.error = None, PreparationCancelledError("annulée")
        elif scenario == "detached":
            manager.detach_finishers()

        task.finished(True)

        assert job.status == "failed", scenario
        assert manager.running is None, scenario
        assert published == [], scenario
        assert job.generator.gi_frame is None, scenario


# --- 7. vraie tâche : pas de déverrouillage forcé -------------------------------------------
@contextlib.contextmanager
def isolated_guard():
    app = QCoreApplication.instance()
    saved = app.property(GUARD)
    app.setProperty(GUARD, "")
    try:
        yield app
    finally:
        app.setProperty(GUARD, saved)


def test_real_task_release_failure_keeps_guard_busy():
    real_acquire = tasks_mod.acquire_landcover_guard

    def acquire_with_failing_release():
        real_acquire()                                      # vrai propriétaire posé

        def release():                                      # échec : rien n'est effacé
            raise RuntimeError("libération du verrou impossible (double)")

        return release

    executor = tasks_mod.ProcessingExecutor()
    with isolated_guard() as app:
        try:
            with patched(tasks_mod, "acquire_landcover_guard",
                         acquire_with_failing_release), \
                 patched(preparation, "prepare_native_inputs",
                         lambda **_kw: {"status": "complete", "output_directory": "x"}):
                manager = JobManager(executor)
                published = []
                job = _obia_job(manager, published)
                assert isinstance(job.handle, LandcoverPreparationTask)
                assert spin(lambda: job.status != "running"), "tâche non terminée"

            assert job.status == "failed" and manager.running is None
            assert published == []
            assert executor._active == set()                # retrait du suivi effectué
            assert app.property(GUARD) not in (None, "")    # verrou toujours occupé
            try:
                guard_mod.acquire_landcover_guard()
            except ToolError as exc:
                assert exc.code == ErrorCode.BUSY
            else:
                raise AssertionError("BUSY attendu : aucun déverrouillage forcé")
        finally:
            for task in list(executor._active):
                task.cancel()
            spin(lambda: not executor._active)


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
