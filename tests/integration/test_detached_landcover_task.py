"""Jobs détachés avec une vraie LandcoverPreparationTask dans QgsTaskManager.

Nécessite PyQGIS, GDAL et NumPy. Sous pytest sans QGIS, le module est ignoré. Le Python de
QGIS n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" \
        tests/integration/test_detached_landcover_task.py

Vrai ProcessingExecutor, vrai JobManager, vraie tâche QGIS ; seuls le finisseur et l'outil
(générateur) sont des doubles. Fichiers dans un dossier temporaire ; aucun projet ni
plugin de la session de travail n'est touché. Le pompage d'événements (spin) est propre
au test : QgsTask.finished() est livré sur le thread principal.

- test_real_task_success_* : vraie préparation raster sur un GeoTIFF temporaire ;
- test_real_task_cancel_* / test_real_task_error_* : vraie tâche, traitement contrôlé
  (prepare_native_inputs remplacé le temps de l'essai).
"""
from __future__ import annotations

import contextlib
import os
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

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication

_QGS = QgsApplication.instance()
if _QGS is None:
    _QGS = QgsApplication([], True)
    _QGS.initQgis()

import numpy as np  # noqa: E402
from osgeo import gdal, ogr, osr  # noqa: E402

from cynogis.core.jobs import DetachedJobOutcome, JobManager, PrepareLandcover  # noqa: E402
from cynogis.core.landcover import PreparationConfig  # noqa: E402
from cynogis.landcover_processing import prepare as preparation  # noqa: E402
from cynogis.tools.landcover_tasks import LandcoverPreparationTask  # noqa: E402
from cynogis.tools.tasks import ProcessingExecutor  # noqa: E402

GRID = (341000.0, 0.5, 0.0, 7642400.0, 0.0, -0.5)


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


def _crs_wkt():
    reference = osr.SpatialReference()
    assert reference.ImportFromEPSG(2975) == 0
    return reference.ExportToWkt()


def make_sample(root: Path) -> dict:
    source, output = root / "source.tif", root / "outputs"
    output.mkdir(parents=True)
    dataset = gdal.GetDriverByName("GTiff").Create(str(source), 4, 4, 3, gdal.GDT_Byte)
    try:
        dataset.SetGeoTransform(GRID)
        dataset.SetProjection(_crs_wkt())
        for index, value in enumerate((10, 20, 30)):
            dataset.GetRasterBand(index + 1).WriteArray(np.full((4, 4), value, np.uint8))
    finally:
        dataset.Close()
    wkt = ("POLYGON ((341000 7642398, 341002 7642398, 341002 7642400, "
           "341000 7642400, 341000 7642398))")
    return {"source": source, "output": output,
            "wkb": bytes(ogr.CreateGeometryFromWkt(wkt).ExportToWkb())}


def start_job(sample: dict):
    executor = ProcessingExecutor()
    manager = JobManager(executor)
    published, finisher_calls = [], []

    def tool():
        result = yield PrepareLandcover(
            raster_path=sample["source"], aoi_wkb=sample["wkb"], aoi_crs_wkt=_crs_wkt(),
            rgb_bands=(1, 2, 3), output_parent=sample["output"],
            config=PreparationConfig(validity_policy="respect_source_masks"))
        published.append(result)
        return result

    gen = tool()
    job = manager.start("obia_test", gen, next(gen),
                        lambda r, e: finisher_calls.append((r, e)))
    assert isinstance(job.handle, LandcoverPreparationTask)
    return executor, manager, job, published, finisher_calls


def wait_done(job, executor):
    assert spin(lambda: job.status != "running"), "la tâche réelle n'a pas terminé"
    assert spin(lambda: not executor._active), "la tâche n'a pas été libérée"


def test_real_task_success_after_detach_is_not_published():
    sample = make_sample(Path(tempfile.mkdtemp(prefix="cynogis_detach_ok_")))
    executor, manager, job, published, finisher_calls = start_job(sample)
    manager.detach_finishers()
    wait_done(job, executor)

    assert job.status == "cancelled"
    assert published == [] and finisher_calls == []
    assert job.generator.gi_frame is None and job.handle is None
    outcome = job.response
    assert isinstance(outcome, DetachedJobOutcome)
    assert outcome.error_code == "CANCELLED"
    retained = Path(outcome.retained_output_directory)
    assert retained.parent == sample["output"]
    assert (retained / "preparation.json").is_file()       # sortie complète conservée


def test_real_task_cancel_after_detach_confirms_on_callback():
    sample = make_sample(Path(tempfile.mkdtemp(prefix="cynogis_detach_cancel_")))
    entered = threading.Event()

    def controlled(*, control, **_kwargs):
        entered.set()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            control.check_cancelled()                       # lève à l'annulation
            time.sleep(0.01)
        raise RuntimeError("annulation jamais reçue (test)")

    with patched(preparation, "prepare_native_inputs", controlled):
        executor, manager, job, published, finisher_calls = start_job(sample)
        assert spin(entered.is_set)
        manager.detach_finishers()
        manager.cancel_all("Déchargement du plugin.")
        assert job.status == "running"                      # en attente du vrai callback
        wait_done(job, executor)

    assert job.status == "cancelled"
    assert published == [] and finisher_calls == []
    assert job.response.error_code == "CANCELLED"
    assert job.response.retained_output_directory is None


def test_real_task_error_after_detach_stays_failed():
    sample = make_sample(Path(tempfile.mkdtemp(prefix="cynogis_detach_error_")))

    def failing(**_kwargs):
        raise OSError("disque plein (test)")

    with patched(preparation, "prepare_native_inputs", failing):
        executor, manager, job, published, finisher_calls = start_job(sample)
        manager.detach_finishers()
        wait_done(job, executor)

    assert job.status == "failed"
    assert published == [] and finisher_calls == []
    assert job.response.error_type == "OSError"
    assert job.response.error_code is None


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
