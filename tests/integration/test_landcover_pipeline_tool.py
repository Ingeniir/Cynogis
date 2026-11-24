"""Chaîne OBIA complète par les outils MCP : vrai Dispatcher, vrais jobs, vraies tâches.

segment_landcover → extract_landcover_features → delineate_landcover, puis couche des
unités ajoutée au projet. Harnais (environnement isolé, verrou, arrêt confirmé) repris de
test_segment_landcover_tool. Nécessite PyQGIS, GDAL et scikit-image ; ignoré sinon.

    .venv/Scripts/python scripts/run_qgis_integration.py -- -q TEST
    (TEST = tests/integration/test_landcover_pipeline_tool.py)
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
from _pyqgis_abi import skip_if_foreign_pyqgis

skip_if_foreign_pyqgis(pytest)
pytest.importorskip("qgis.core", exc_type=ImportError)
pytest.importorskip("skimage", reason="scikit-image absent : suite ignorée")

from qgis.core import QgsProject  # noqa: E402
from test_segment_landcover_tool import (  # noqa: E402
    STOP,
    environment,
    final_response,
    guard_free,
    patched,
    request,
    spin,
)

from cynogis.landcover_processing import persist_features  # noqa: E402


def _run(dispatcher, tool, **params):
    started = dispatcher.dispatch(request(tool, **params))
    assert started.ok and started.job_id, started.error
    final = final_response(dispatcher, started.job_id)
    assert final.ok, final.error
    return final


def _segmentation(env, dispatcher):
    final = _run(dispatcher, "segment_landcover", preparation_directory=str(env.prep))
    return Path(final.data["output_directory"])


def test_real_chaine_complete_jusqu_a_la_couche():
    with environment() as env:
        dispatcher, audit = env.dispatcher()
        seg = _segmentation(env, dispatcher)
        features = _run(dispatcher, "extract_landcover_features",
                        preparation_directory=str(env.prep), segmentation_directory=str(seg))
        feat = Path(features.data["output_directory"])
        assert feat.parent == env.obia and (feat / "features.json").is_file()

        project = QgsProject.instance()
        before = set(project.mapLayers())
        final = _run(dispatcher, "delineate_landcover", preparation_directory=str(env.prep),
                     segmentation_directory=str(seg), features_directory=str(feat),
                     min_mapping_area_m2=5.0)
        try:
            data = final.data
            layer = project.mapLayer(data["layer"]["layer_id"])
            assert set(project.mapLayers()) - before == {layer.id()}
            assert layer.featureCount() == data["diagnostics"]["units"] >= 1
            assert {"unit_id", "area_plan_m2", "red_mean"} <= set(layer.fields().names())
            areas = data["areas"]
            # 40 x 40 pixels de 0,5 m : 400 m² ; écart plan/ellipsoïdal < 0,1 % à La Réunion.
            assert areas["total_plan_m2"] == 400.0
            assert areas["total_ellipsoidal_m2"] == pytest.approx(400.0, rel=1e-3)
            assert "ellipso" in areas["total_ellipsoidal_method"]
            assert "plane" in areas["total_plan_method"]
            assert any("non classées" in w for w in final.warnings)
            entry = next(e for e in audit.recent(10)
                         if e["tool"] == "delineate_landcover" and e["ok"])
            assert any(o.endswith("delineation.gpkg") for o in entry["outputs"])
            assert guard_free()
        finally:
            project.removeMapLayers(list(set(project.mapLayers()) - before))


@pytest.mark.parametrize(("tool", "params", "message"), [
    ("extract_landcover_features", {"segmentation_directory": "relatif"}, "absolu"),
    ("extract_landcover_features", {"segmentation_directory": "PREP"}, "distincts"),
    ("delineate_landcover", {"color_distance_max": 500}, ""),
])
def test_prevalidation_sans_tache(tool, params, message):
    with environment() as env:
        dispatcher, _ = env.dispatcher()
        values = {"preparation_directory": str(env.prep),
                  "segmentation_directory": str(env.root),
                  "features_directory": str(env.output)}
        if tool == "extract_landcover_features":
            values.pop("features_directory")
        values.update({k: str(env.prep) if v == "PREP" else v for k, v in params.items()})
        response = dispatcher.dispatch(request(tool, **values))
        assert not response.ok and response.job_id is None
        assert response.error["code"] == "INVALID_PARAMS"
        assert message in response.error["message"]
        assert not env.executors[0]._active and guard_free()


def test_task_annulation_des_caracteristiques():
    entered = threading.Event()

    def engine(*, control, **_kwargs):
        control.checkpoint(10)
        entered.set()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not STOP.is_set():
            control.check_cancelled()
            time.sleep(0.01)
        raise RuntimeError("annulation jamais reçue (test)")

    with environment() as env:
        dispatcher, _ = env.dispatcher()
        seg = _segmentation(env, dispatcher)
        with patched(persist_features, "persist_object_features", engine):
            started = dispatcher.dispatch(request(
                "extract_landcover_features", preparation_directory=str(env.prep),
                segmentation_directory=str(seg)))
            assert started.job_id and spin(entered.is_set)
            busy = dispatcher.dispatch(request(
                "segment_landcover", preparation_directory=str(env.prep)))
            assert busy.error["code"] == "BUSY"
            dispatcher.dispatch(request("cancel_job", job_id=started.job_id))
            final = final_response(dispatcher, started.job_id)
        assert final.error["code"] == "CANCELLED"
        assert dispatcher.jobs.get(started.job_id).status == "cancelled"
        assert spin(lambda: not env.executors[0]._active) and guard_free()
