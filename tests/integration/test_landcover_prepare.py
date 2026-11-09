import json
from pathlib import Path
from threading import Event

import pytest

from cynogis.core.landcover import PreparationConfig
from cynogis.core.landcover_execution import PreparationCancelledError, PreparationControl

np = pytest.importorskip("numpy")
gdal = pytest.importorskip("osgeo.gdal")
ogr = pytest.importorskip("osgeo.ogr")
osr = pytest.importorskip("osgeo.osr")

from cynogis.landcover_processing import prepare as preparation  # noqa: E402

GRID = (341000.0, 0.5, 0.0, 7642400.0, 0.0, -0.5)


def _crs(epsg=2975):
    reference = osr.SpatialReference()
    assert reference.ImportFromEPSG(epsg) == 0
    return reference.ExportToWkt()


def _rectangle(xmin, ymin, xmax, ymax):
    return (
        f"POLYGON (({xmin} {ymin}, {xmax} {ymin}, "
        f"{xmax} {ymax}, {xmin} {ymax}, {xmin} {ymin}))"
    )


def _wkb(wkt):
    geometry = ogr.CreateGeometryFromWkt(wkt)
    assert geometry is not None
    return bytes(geometry.ExportToWkb())


@pytest.fixture
def sample(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "outputs"
    output.mkdir()

    values = np.empty((3, 4, 4), dtype=np.uint8)
    values[0].fill(10)
    values[1].fill(20)
    values[2].fill(30)

    values[0, 0, 0] = 255
    values[:, 1, 1] = 255
    values[2, 2, 2] = 0

    dataset = gdal.GetDriverByName("GTiff").Create(
        str(source), 4, 4, 3, gdal.GDT_Byte
    )
    assert dataset is not None
    try:
        dataset.SetGeoTransform(GRID)
        dataset.SetProjection(_crs())
        for index in range(3):
            band = dataset.GetRasterBand(index + 1)
            band.WriteArray(values[index])
            band.SetNoDataValue(255)
    finally:
        dataset.Close()

    full_aoi = _wkb(_rectangle(341000, 7642398, 341002, 7642400))

    return {
        "source": source,
        "output": output,
        "values": values,
        "wkb": full_aoi,
    }


def _run(sample, **overrides):
    arguments = {
        "raster_path": sample["source"],
        "aoi_wkb": sample["wkb"],
        "aoi_crs_wkt": _crs(),
        "rgb_bands": [1, 2, 3],
        "output_parent": sample["output"],
        "config": PreparationConfig(validity_policy="respect_source_masks"),
    }
    arguments.update(overrides)
    return preparation.prepare_native_inputs(**arguments)


def _read(path):
    dataset = gdal.OpenEx(str(path), gdal.OF_RASTER | gdal.OF_READONLY)
    assert dataset is not None
    try:
        return dataset.ReadAsArray()
    finally:
        dataset.Close()


def test_preparation_preserves_pixels_and_masks(sample):
    original = sample["source"].read_bytes()

    report = _run(sample)
    run = Path(report["output_directory"])

    assert sample["source"].read_bytes() == original
    np.testing.assert_array_equal(
        _read(run / "image_rgb.tif"), sample["values"]
    )

    expected_validity = np.all(sample["values"] != 255, axis=0)
    np.testing.assert_array_equal(
        _read(run / "validity_mask.tif"), expected_validity.astype(np.uint8)
    )
    np.testing.assert_array_equal(
        _read(run / "analysis_mask.tif"), expected_validity.astype(np.uint8)
    )

    assert report["counts"] == {
        "total_pixels": 16,
        "aoi_pixels": 16,
        "valid_pixels_whole_raster": 14,
        "invalid_pixels_whole_raster": 2,
        "analysis_pixels": 14,
        "invalid_pixels_inside_aoi": 2,
        "valid_pixels_outside_aoi": 0,
    }

    saved = json.loads((run / "preparation.json").read_text(encoding="utf-8"))
    assert saved == report
    assert sorted(report["files"]) == sorted(
        str(path.relative_to(run))
        for path in run.rglob("*")
        if path.is_file()
    )


def test_reordered_bands(sample):
    report = _run(sample, rgb_bands=[3, 2, 1])
    run = Path(report["output_directory"])

    np.testing.assert_array_equal(
        _read(run / "image_rgb.tif"), sample["values"][[2, 1, 0]]
    )


def test_output_metadata(sample):
    report = _run(sample)
    run = Path(report["output_directory"])

    for name in (
        "image_rgb.tif",
        "aoi_mask.tif",
        "validity_mask.tif",
        "analysis_mask.tif",
    ):
        dataset = gdal.Open(str(run / name))
        assert dataset is not None
        try:
            assert tuple(dataset.GetGeoTransform()) == GRID
            for index in range(1, dataset.RasterCount + 1):
                band = dataset.GetRasterBand(index)
                assert band.GetNoDataValue() is None

                if name == "image_rgb.tif":
                    assert band.GetMaskFlags() & gdal.GMF_PER_DATASET
                    np.testing.assert_array_equal(
                        band.GetMaskBand().ReadAsArray() != 0,
                        np.all(sample["values"] != 255, axis=0),
                    )
                else:
                    assert set(np.unique(band.ReadAsArray())) <= {0, 1}
                    assert np.all(band.GetMaskBand().ReadAsArray() != 0)
        finally:
            dataset.Close()


def test_polygon_hole(sample):
    aoi = _wkb(
        "POLYGON ("
        "(341000 7642398, 341002 7642398, 341002 7642400, "
        "341000 7642400, 341000 7642398),"
        "(341000.5 7642398.5, 341000.5 7642399.5, "
        "341001.5 7642399.5, 341001.5 7642398.5, 341000.5 7642398.5)"
        ")"
    )
    report = _run(sample, aoi_wkb=aoi)

    assert report["counts"]["aoi_pixels"] == 12
    assert report["counts"]["invalid_pixels_inside_aoi"] == 1


def test_multipolygon(sample):
    geometry = ogr.Geometry(ogr.wkbMultiPolygon)
    for bounds in (
        (341001.5, 7642399.5, 341002, 7642400),
        (341000, 7642398, 341000.5, 7642398.5),
    ):
        polygon = ogr.CreateGeometryFromWkt(_rectangle(*bounds))
        assert geometry.AddGeometry(polygon) == 0

    report = _run(sample, aoi_wkb=bytes(geometry.ExportToWkb()))

    assert report["counts"]["aoi_pixels"] == 2
    assert report["counts"]["analysis_pixels"] == 2


@pytest.mark.parametrize(
    ("bounds", "message"),
    [
        ((342000, 7642398, 342002, 7642400), "aucun pixel"),
        ((341000, 7642399.5, 341000.5, 7642400), "aucun pixel analysable"),
    ],
)
def test_empty_analysis_is_rejected(sample, bounds, message):
    with pytest.raises(ValueError, match=message):
        _run(sample, aoi_wkb=_wkb(_rectangle(*bounds)))

    assert list(sample["output"].iterdir()) == []


def test_different_crs_is_rejected(sample):
    with pytest.raises(ValueError, match="même SCR"):
        _run(sample, aoi_crs_wkt=_crs(4326))


def test_pixel_limit_is_enforced(sample):
    config = PreparationConfig(
        validity_policy="respect_source_masks", max_pixels=15
    )
    with pytest.raises(ValueError, match="max_pixels"):
        _run(sample, config=config)


def test_rotated_grid_is_rejected(sample):
    dataset = gdal.Open(str(sample["source"]), gdal.GA_Update)
    assert dataset is not None
    try:
        rotated = list(GRID)
        rotated[2] = 0.1
        dataset.SetGeoTransform(rotated)
    finally:
        dataset.Close()

    with pytest.raises(ValueError, match="sans rotation"):
        _run(sample)


def test_successive_runs_do_not_overwrite(sample):
    first = _run(sample)
    second = _run(sample)

    assert first["output_directory"] != second["output_directory"]
    assert Path(first["output_directory"], "preparation.json").is_file()
    assert Path(second["output_directory"], "preparation.json").is_file()


def test_failed_write_cleans_only_its_directory(sample, monkeypatch):
    sentinel = sample["output"] / "keep.txt"
    sentinel.write_text("conserver", encoding="utf-8")

    original_writer = preparation._write_raster

    def failing_writer(path, values, grid, *, validity=None):
        original_writer(path, values, grid, validity=validity)
        raise OSError("Échec simulé après écriture")

    monkeypatch.setattr(preparation, "_write_raster", failing_writer)

    with pytest.raises(OSError, match="Échec simulé"):
        _run(sample)

    assert sentinel.read_text(encoding="utf-8") == "conserver"
    assert list(sample["output"].iterdir()) == [sentinel]

def test_preparation_reports_progress(sample):
    received = []

    report = _run(
        sample,
        control=PreparationControl(on_progress=received.append),
    )

    assert received == [
        0.0,
        20.0,
        30.0,
        35.0,
        40.0,
        50.0,
        60.0,
        70.0,
        80.0,
        84.0,
        88.0,
        92.0,
        97.0,
        99.0,
    ]
    assert report["status"] == "complete"

    manifest = Path(report["output_directory"]) / "preparation.json"
    assert manifest.is_file()


@pytest.mark.parametrize(
    "cancel_at",
    [0, 20, 30, 35, 40, 50, 60, 70, 80, 84, 88, 92, 97, 99],
)
def test_cancellation_cleans_own_outputs(sample, cancel_at):
    cancelled = Event()
    received = []

    sentinel = sample["output"] / "keep.txt"
    sentinel.write_text("conserver", encoding="utf-8")
    original_source = sample["source"].read_bytes()

    def progress(value):
        received.append(value)
        if value >= cancel_at:
            cancelled.set()

    control = PreparationControl(
        on_progress=progress,
        is_cancelled=cancelled.is_set,
    )

    with pytest.raises(PreparationCancelledError):
        _run(sample, control=control)

    assert received[-1] == float(cancel_at)
    assert sample["source"].read_bytes() == original_source
    assert sentinel.read_text(encoding="utf-8") == "conserver"
    assert list(sample["output"].iterdir()) == [sentinel]


def test_progress_error_also_cleans_outputs(sample):
    sentinel = sample["output"] / "keep.txt"
    sentinel.write_text("conserver", encoding="utf-8")

    def progress(value):
        # Le premier raster a déjà été écrit et fermé.
        if value == 50:
            raise RuntimeError("Notification impossible")

    with pytest.raises(RuntimeError, match="Notification impossible"):
        _run(
            sample,
            control=PreparationControl(on_progress=progress),
        )

    assert sentinel.read_text(encoding="utf-8") == "conserver"
    assert list(sample["output"].iterdir()) == [sentinel]


def test_already_cancelled_preparation_creates_no_output(sample):
    cancelled = Event()
    cancelled.set()

    with pytest.raises(PreparationCancelledError):
        _run(
            sample,
            control=PreparationControl(
                is_cancelled=cancelled.is_set,
            ),
        )

    assert list(sample["output"].iterdir()) == []


def test_cancellation_with_failed_cleanup_is_a_technical_failure(sample, monkeypatch):
    """Une annulation laissant un dossier résiduel n'est pas une annulation propre."""
    cancelled = Event()

    def progress(value):
        if value >= 50:
            cancelled.set()

    def failing_rmtree(path, *args, **kwargs):
        raise OSError("Fichier verrouillé simulé")

    monkeypatch.setattr(preparation.shutil, "rmtree", failing_rmtree)

    with pytest.raises(RuntimeError, match="nettoyage incomplet") as caught:
        _run(
            sample,
            control=PreparationControl(
                on_progress=progress,
                is_cancelled=cancelled.is_set,
            ),
        )

    assert not isinstance(caught.value, PreparationCancelledError)
    assert isinstance(caught.value.__cause__, PreparationCancelledError)

    # Le dossier résiduel est signalé et reste présent.
    residual = [path for path in sample["output"].iterdir() if path.is_dir()]
    assert len(residual) == 1
    assert str(residual[0]) in str(caught.value)
