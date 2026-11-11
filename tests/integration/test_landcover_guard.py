"""Verrou inter-instances des préparations OBIA (tools/landcover_guard.py).

Nécessite PyQGIS. Sous pytest sans QGIS, le module est ignoré. Le Python de QGIS
n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" \
        tests/integration/test_landcover_guard.py

Processus QGIS de test isolé : la propriété Qt du verrou est sauvegardée puis restaurée
par chaque essai, même en cas d'échec. Aucune tâche réelle ici :
- test_guard_* : vrai verrou sur la vraie QCoreApplication du processus de test ;
- test_executor_* : vrai ProcessingExecutor, constructeur de tâche ou gestionnaire de
  tâches remplacé par un double qui n'enregistre rien ;
- test_reload_* : rechargement réel du module landcover_guard (importlib.reload) sans
  réinitialiser la propriété Qt. Valide le stockage partagé, pas Plugin Reloader.
"""
from __future__ import annotations

import contextlib
import importlib
import os
import sys
import threading
import traceback
from pathlib import Path
from types import SimpleNamespace

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
from cynogis.core.jobs import PrepareLandcover  # noqa: E402
from cynogis.core.landcover import PreparationConfig  # noqa: E402
from cynogis.tools import landcover_guard as guard_mod  # noqa: E402
from cynogis.tools import tasks as tasks_mod  # noqa: E402

NAME = guard_mod._PROPERTY_NAME


@contextlib.contextmanager
def isolated_property():
    """Part d'un verrou libre et restaure la valeur d'origine en sortie."""
    app = QCoreApplication.instance()
    saved = app.property(NAME)
    app.setProperty(NAME, "")
    try:
        yield app
    finally:
        app.setProperty(NAME, saved)


@contextlib.contextmanager
def patched(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)


def expect_busy(acquire):
    try:
        acquire()
    except ToolError as exc:
        assert exc.code == ErrorCode.BUSY
    else:
        raise AssertionError("BUSY attendu")


def is_free(app) -> bool:
    return app.property(NAME) in (None, "")


def in_thread(fn):
    """Exécute fn dans un thread Python ; renvoie l'exception levée (ou None)."""
    box = {}

    def run():
        try:
            fn()
        except BaseException as exc:  # renvoyée au test
            box["error"] = exc

    thread = threading.Thread(target=run)
    thread.start()
    thread.join(10)
    assert not thread.is_alive()
    return box.get("error")


def step():
    return PrepareLandcover(
        raster_path=Path("absent.tif"), aoi_wkb=b"", aoi_crs_wkt="",
        rgb_bands=(1, 2, 3), output_parent=Path("."),
        config=PreparationConfig(validity_policy="respect_source_masks"))


# --- Verrou seul ---------------------------------------------------------------------------
def test_guard_second_acquisition_is_busy_until_release():
    with isolated_property() as app:
        release = guard_mod.acquire_landcover_guard()
        assert not is_free(app)
        expect_busy(guard_mod.acquire_landcover_guard)
        release()
        assert is_free(app)
        again = guard_mod.acquire_landcover_guard()        # acquisition ultérieure
        again()
        assert is_free(app)


def test_guard_double_release_has_no_extra_effect():
    with isolated_property() as app:
        release = guard_mod.acquire_landcover_guard()
        release()
        newer = guard_mod.acquire_landcover_guard()
        owner = app.property(NAME)
        release()                                           # second appel : sans effet
        assert app.property(NAME) == owner
        newer()


def test_guard_old_release_cannot_clear_newer_owner():
    with isolated_property() as app:
        old = guard_mod.acquire_landcover_guard()
        app.setProperty(NAME, "")                           # verrou perdu hors du module
        newer = guard_mod.acquire_landcover_guard()
        owner = app.property(NAME)
        old()
        assert app.property(NAME) == owner
        expect_busy(guard_mod.acquire_landcover_guard)
        newer()
        assert is_free(app)


def test_guard_unexpected_value_is_never_overwritten():
    for value in (42, "valeur-inconnue", ["liste"]):
        with isolated_property() as app:
            app.setProperty(NAME, value)
            expect_busy(guard_mod.acquire_landcover_guard)
            assert app.property(NAME) == value


def test_guard_refused_outside_main_thread():
    with isolated_property() as app:
        error = in_thread(guard_mod.acquire_landcover_guard)
        assert isinstance(error, RuntimeError) and "thread principal" in str(error)
        assert is_free(app)

        release = guard_mod.acquire_landcover_guard()
        owner = app.property(NAME)
        error = in_thread(release)
        assert isinstance(error, RuntimeError) and "thread principal" in str(error)
        assert app.property(NAME) == owner                  # toujours détenu
        release()                                           # puis libérable ici
        assert is_free(app)


# --- ProcessingExecutor avec doubles (aucune tâche enregistrée) ---------------------------
def test_executor_constructor_failure_releases_guard():
    def broken(*_args, **_kwargs):
        raise RuntimeError("constructeur refusé (double)")

    with isolated_property() as app, patched(tasks_mod, "LandcoverPreparationTask", broken):
        executor = tasks_mod.ProcessingExecutor()
        try:
            executor.start(step(), lambda _v, _e: None)
        except RuntimeError as exc:
            assert "constructeur refusé" in str(exc)
        else:
            raise AssertionError("échec attendu")
        assert is_free(app) and executor._active == set()


class RefusingTaskManager:
    """Refuse sans enregistrer : addTask renvoie 0 (contrat documenté) ou lève avant
    tout enregistrement (conversion d'argument)."""

    def __init__(self, mode):
        self.mode, self.calls = mode, 0

    def addTask(self, task, priority=0):
        self.calls += 1
        if self.mode == "raise":
            raise TypeError("argument refusé (double)")
        return 0


def test_executor_addtask_refusal_releases_guard():
    for mode in ("zero", "raise"):
        manager = RefusingTaskManager(mode)
        fake_app = SimpleNamespace(taskManager=lambda manager=manager: manager)
        with isolated_property() as app, patched(tasks_mod, "QgsApplication", fake_app):
            executor = tasks_mod.ProcessingExecutor()
            try:
                executor.start(step(), lambda _v, _e: None)
            except (RuntimeError, TypeError):
                pass
            else:
                raise AssertionError("refus attendu")
            assert manager.calls == 1
            assert is_free(app) and executor._active == set()


def test_executor_instances_share_the_guard():
    with isolated_property():
        release = guard_mod.acquire_landcover_guard()
        try:
            for executor in (tasks_mod.ProcessingExecutor(), tasks_mod.ProcessingExecutor()):
                try:
                    executor.start(step(), lambda _v, _e: None)
                except ToolError as exc:
                    assert exc.code == ErrorCode.BUSY
                else:
                    raise AssertionError("BUSY attendu")
                assert executor._active == set()
        finally:
            release()


# --- Rechargement réel du module -----------------------------------------------------------
def test_reload_shares_property_between_generations():
    global guard_mod
    with isolated_property() as app:
        old_acquire = guard_mod.acquire_landcover_guard
        old_release = old_acquire()
        try:
            new_mod = importlib.reload(guard_mod)           # landcover_guard uniquement
            guard_mod = new_mod
            assert new_mod.acquire_landcover_guard is not old_acquire
            assert not is_free(app)                         # propriété non réinitialisée
            expect_busy(new_mod.acquire_landcover_guard)
        finally:
            old_release()                                   # fonction de la 1re génération
        assert is_free(app)
        release = new_mod.acquire_landcover_guard()
        release()
        assert is_free(app)


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
