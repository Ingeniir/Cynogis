"""Délimitation OBIA (landcover_processing/delineate.py) et contrôle des caractéristiques.

Chaîne réelle préparation → segmentation → caractéristiques → délimitation sur GeoTIFF
synthétiques. Nécessite le Python de QGIS (osgeo) et scikit-image ; ignorée sinon.

    .venv/Scripts/python scripts/run_qgis_integration.py -- -q TEST
    (TEST = tests/integration/test_landcover_delineate.py)
"""
import json
import shutil
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
gdal = pytest.importorskip("osgeo.gdal")
ogr = pytest.importorskip("osgeo.ogr")
pytest.importorskip("skimage", reason="scikit-image absent : suite ignorée")

from skimage.measure import label  # noqa: E402
from test_landcover_persist import _texture  # noqa: E402
from test_persist_features import _chain  # noqa: E402
from test_persist_features import _run as _run_features  # noqa: E402

from cynogis.core.landcover import DelineationConfig  # noqa: E402
from cynogis.core.landcover_execution import (  # noqa: E402
    DelineationCancelledError,
    DelineationControl,
    FeatureExtractionCancelledError,
    FeatureExtractionControl,
)
from cynogis.landcover_processing import delineate  # noqa: E402

FEATURE_CHECKPOINTS = [0, 10, 30, 50, 75, 85, 90, 95, 99]
DELINEATION_CHECKPOINTS = [0, 10, 30, 60, 75, 90, 99]


@pytest.fixture
def case(tmp_path):
    valid = np.ones((30, 30), bool)
    valid[0, :4] = False
    valid[20:23, 20:23] = False
    chained = _chain(tmp_path, _texture(30, 30), valid)
    features_parent = chained["out"]
    chained["feat"] = Path(_run_features(chained)["output_directory"])
    chained["out"] = tmp_path / "delineations"
    chained["out"].mkdir()
    chained["features_parent"] = features_parent
    return chained


def _delineate(case, **overrides):
    arguments = {"preparation_directory": case["prep"], "segmentation_directory": case["seg"],
                 "features_directory": case["feat"], "output_parent": case["out"]}
    arguments.update(overrides)
    return delineate.persist_delineation(**arguments)


def _units(run):
    dataset = ogr.Open(str(run / "delineation.gpkg"))
    try:
        layer = dataset.GetLayerByName(delineate.LAYER_NAME)
        rows = [(f.GetField("unit_id"), f.GetField("pixel_count"), f.GetField("area_plan_m2"),
                 f.GetGeometryRef().GetArea()) for f in layer]
        return rows
    finally:
        dataset = None


def _band(path):
    dataset = gdal.Open(str(path))
    try:
        return dataset.GetRasterBand(1).ReadAsArray()
    finally:
        dataset = None


class Recorder:
    def __init__(self, cancel_at=None):
        self.received, self.cancel_at, self.cancelled = [], cancel_at, False

    def progress(self, value):
        self.received.append(value)
        if value == self.cancel_at:
            self.cancelled = True

    def make(self, control_type):
        return control_type(on_progress=self.progress, is_cancelled=lambda: self.cancelled)


# --- Caractéristiques : contrôle coopératif ------------------------------------------------
def test_real_caracteristiques_sequence(case):
    recorder = Recorder()
    _run_features(case, control=recorder.make(FeatureExtractionControl))
    assert recorder.received == [float(v) for v in FEATURE_CHECKPOINTS]


@pytest.mark.parametrize("cancel_at", FEATURE_CHECKPOINTS)
def test_real_caracteristiques_annulation(case, cancel_at):
    out = case["root"] / "annulation"
    out.mkdir()
    with pytest.raises(FeatureExtractionCancelledError):
        _run_features(case, output_parent=out,
                      control=Recorder(cancel_at).make(FeatureExtractionControl))
    assert list(out.iterdir()) == []


def test_caracteristiques_controle_de_type_incorrect(case):
    with pytest.raises(ValueError, match="FeatureExtractionControl"):
        _run_features(case, control=DelineationControl())


# --- Délimitation réelle -------------------------------------------------------------------
def test_real_delimitation_complete(case):
    recorder = Recorder()
    report = _delineate(case, control=recorder.make(DelineationControl))
    run = Path(report["output_directory"])

    assert recorder.received == [float(v) for v in DELINEATION_CHECKPOINTS]
    assert sorted(p.name for p in run.iterdir()) == sorted(report["files"])
    assert json.loads((run / "delineation.json").read_text(encoding="utf-8")) == report
    units = _units(run)
    diagnostics = report["diagnostics"]
    assert len(units) == diagnostics["units"] <= diagnostics["input_objects"]
    assert sorted(u[0] for u in units) == list(range(1, len(units) + 1))
    for _, pixels, area, geometry_area in units:
        assert area == pixels * 0.25
        assert geometry_area == pytest.approx(area, abs=1e-6)  # polygone = pixels
    assert sum(u[2] for u in units) == pytest.approx(diagnostics["analysis_area_m2"])

    regions = _band(run / "regions.tif")
    labels = _band(case["seg"] / "segments.tif")
    assert np.array_equal(regions > 0, labels > 0)
    _, components = label(regions, background=0, connectivity=1, return_num=True)
    assert components == len(units)  # chaque unité est d'un seul tenant
    # Une unité regroupe des segments entiers.
    for segment in np.unique(labels[labels > 0]):
        assert len(np.unique(regions[labels == segment])) == 1


def test_real_sans_fusion_unites_egales_aux_segments(case):
    report = _delineate(case, config=DelineationConfig(0, 0))
    assert report["diagnostics"]["units"] == report["diagnostics"]["input_objects"]
    assert report["diagnostics"]["merged_by_similarity"] == 0


def test_real_tout_fusionner(case):
    report = _delineate(case, config=DelineationConfig(442, 0))
    # Le masque est d'un seul tenant (4 voisins) : une seule unité.
    assert report["diagnostics"]["units"] == 1


def test_real_surface_minimale_respectee(case):
    report = _delineate(case, config=DelineationConfig(0, 20))
    run = Path(report["output_directory"])
    assert all(area >= 20 for _, _, area, _ in _units(run))
    assert report["diagnostics"]["isolated_small_units"] == 0


# --- Refus ---------------------------------------------------------------------------------
def test_refus_caracteristiques_d_autres_sources(case):
    other = case["root"] / "autre_seg"
    shutil.copytree(case["seg"], other)
    manifest = other / "segmentation.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        _delineate(case, segmentation_directory=other)
    assert list(case["out"].iterdir()) == []


def test_refus_table_alteree(case):
    path = case["feat"] / "edges.npy"
    path.write_bytes(path.read_bytes() + b"\0")
    with pytest.raises(ValueError, match=r"edges.npy"):
        _delineate(case)
    assert list(case["out"].iterdir()) == []


def test_refus_sources_identiques(case):
    with pytest.raises(ValueError, match="distinctes"):
        _delineate(case, features_directory=case["seg"])


# --- Annulation et échecs ------------------------------------------------------------------
@pytest.mark.parametrize("cancel_at", DELINEATION_CHECKPOINTS)
def test_real_annulation_a_chaque_checkpoint(case, cancel_at):
    with pytest.raises(DelineationCancelledError):
        _delineate(case, control=Recorder(cancel_at).make(DelineationControl))
    assert list(case["out"].iterdir()) == []


def test_double_echec_de_vectorisation_nettoie(case, monkeypatch):
    keep = case["out"] / "keep.txt"
    keep.write_text("conserver", encoding="utf-8")

    def failing(*args, **kwargs):
        raise OSError("vectorisation simulée en échec")

    monkeypatch.setattr(delineate, "_write_units", failing)
    with pytest.raises(OSError, match="vectorisation simulée"):
        _delineate(case)
    assert list(case["out"].iterdir()) == [keep]


def test_double_unite_morcelee_refusee(case, monkeypatch):
    real = delineate._write_units
    monkeypatch.setattr(delineate, "_write_units", lambda *a: real(*a) + 1)
    with pytest.raises(RuntimeError, match="seul tenant"):
        _delineate(case)
    assert list(case["out"].iterdir()) == []
