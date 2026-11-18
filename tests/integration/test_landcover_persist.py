"""Persistance OBIA (landcover_processing/persist.py) : vrai GDAL, vrai SLIC.

Nécessite le Python de QGIS (osgeo) et obia-requirements.txt (scikit-image). Dans le
venv du dépôt, la suite est ignorée explicitement : ce n'est pas une validation.

Les entrées sont produites par prepare_native_inputs sur des GeoTIFF synthétiques.
Familles d'essais :
- vrais traitements : préparation + segmentation + écriture/relecture réelles ;
- doubles (monkeypatch) : noyau, écriture, relecture, JSON, replace, rmtree remplacés
  pour exercer les refus et nettoyages que le vrai code ne déclenche pas ;
- processus séparés : modes d'exceptions GDAL et import du plugin ;
- contrôle coopératif : progression et annulation aux checkpoints de persist.

Ces essais vérifient le contrat technique, pas la qualité géographique des segments ;
aucun nombre exact d'objets SLIC n'est exigé sur une image texturée.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
gdal = pytest.importorskip("osgeo.gdal")
ogr = pytest.importorskip("osgeo.ogr")
osr = pytest.importorskip("osgeo.osr")
pytest.importorskip("skimage", reason="scikit-image absent : suite de persistance ignorée")

import skimage.segmentation  # noqa: E402
from skimage.measure import label  # noqa: E402

from cynogis.core.landcover import PreparationConfig  # noqa: E402
from cynogis.core.landcover_execution import (  # noqa: E402
    PreparationControl,
    SegmentationCancelledError,
    SegmentationControl,
)
from cynogis.landcover_processing import persist  # noqa: E402
from cynogis.landcover_processing.prepare import prepare_native_inputs  # noqa: E402
from cynogis.landcover_processing.segment import SlicConfig  # noqa: E402

PLUGIN_DIR = Path(__file__).resolve().parents[2] / "plugin"
X0, Y0, PIXEL = 341000.0, 7642400.0, 0.5
GRID = (X0, PIXEL, 0.0, Y0, 0.0, -PIXEL)
INPUTS = persist._INPUT_NAMES


# --- Construction des entrées ----------------------------------------------------------
def _wkt(epsg=2975):
    reference = osr.SpatialReference()
    assert reference.ImportFromEPSG(epsg) == 0
    return reference.ExportToWkt()


def _full_aoi(height, width):
    xmax, ymin = X0 + PIXEL * width, Y0 - PIXEL * height
    wkt = f"POLYGON (({X0} {ymin}, {xmax} {ymin}, {xmax} {Y0}, {X0} {Y0}, {X0} {ymin}))"
    return bytes(ogr.CreateGeometryFromWkt(wkt).ExportToWkb())


def _texture(height, width, seed=20261118):
    rgb = np.random.default_rng(seed).integers(0, 255, (height, width, 3), dtype=np.uint8)
    rgb[: height // 2, :, 0] = 200  # deux régions de couleurs différentes
    return rgb


def _prepare(root, rgb, valid):
    """GeoTIFF RGB, NoData 255 sur les pixels invalides, préparé par le vrai code."""
    height, width = valid.shape
    source = root / "source.tif"
    values = np.where(valid[..., None], np.minimum(rgb, 254), 255).astype(np.uint8)
    dataset = gdal.GetDriverByName("GTiff").Create(str(source), width, height, 3, gdal.GDT_Byte)
    try:
        dataset.SetGeoTransform(GRID)
        dataset.SetProjection(_wkt())
        for index in range(3):
            band = dataset.GetRasterBand(index + 1)
            band.WriteArray(values[..., index])
            band.SetNoDataValue(255)
    finally:
        dataset.Close()
    parent = root / "preparations"
    parent.mkdir()
    report = prepare_native_inputs(
        raster_path=source, aoi_wkb=_full_aoi(height, width), aoi_crs_wkt=_wkt(),
        rgb_bands=[1, 2, 3], output_parent=parent,
        config=PreparationConfig(validity_policy="respect_source_masks"),
    )
    return Path(report["output_directory"])


def _islands_mask():
    """Trou, îlot, contact diagonal seul et pixel isolé."""
    valid = np.zeros((20, 20), bool)
    valid[2:12, 2:12] = True
    valid[5:8, 5:8] = False  # trou
    valid[15:18, 15:18] = True  # îlot
    valid[12, 12] = True  # touche (11, 11) par un coin seulement
    valid[0, 19] = True  # pixel isolé
    return valid


@pytest.fixture
def sample(tmp_path):
    valid = np.ones((40, 40), bool)
    valid[0, :5] = False
    valid[30:33, 30:33] = False
    preparation = _prepare(tmp_path, _texture(40, 40), valid)
    output = tmp_path / "segmentations"
    output.mkdir()
    return {"prep": preparation, "out": output, "valid": valid, "root": tmp_path}


@pytest.fixture
def islands(tmp_path):
    valid = _islands_mask()
    preparation = _prepare(tmp_path, _texture(20, 20), valid)
    output = tmp_path / "segmentations"
    output.mkdir()
    return {"prep": preparation, "out": output, "valid": valid, "root": tmp_path}


def _run(case, **overrides):
    arguments = {"preparation_directory": case["prep"], "output_parent": case["out"]}
    arguments.update(overrides)
    return persist.persist_segmentation(**arguments)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(directory):
    return {path.name: _sha(path) for path in directory.iterdir() if path.is_file()}


def _read_segments(directory):
    dataset = gdal.Open(str(directory / "segments.tif"))
    assert dataset is not None
    try:
        band = dataset.GetRasterBand(1)
        return {
            "values": band.ReadAsArray(),
            "type": band.DataType,
            "nodata": band.GetNoDataValue(),
            "mask_flags": band.GetMaskFlags(),
            "geotransform": dataset.GetGeoTransform(),
            "wkt": dataset.GetProjectionRef(),
            "count": dataset.RasterCount,
        }
    finally:
        dataset.Close()


# --- Réécriture des entrées pour les refus ---------------------------------------------
def _read_bands(path):
    dataset = gdal.Open(str(path))
    try:
        bands = [dataset.GetRasterBand(i + 1).ReadAsArray() for i in range(dataset.RasterCount)]
        return bands, dataset.GetGeoTransform(), dataset.GetProjectionRef()
    finally:
        dataset.Close()


def _rewrite(path, bands=None, *, data_type=gdal.GDT_Byte, rgb=False, mask=None,
             geotransform=None, wkt=None):
    old_bands, old_transform, old_wkt = _read_bands(path)
    bands = old_bands if bands is None else bands
    path.unlink()
    # Explicite : GTiff choisit RGB par défaut pour trois bandes Byte.
    options = ["PHOTOMETRIC=RGB" if rgb else "PHOTOMETRIC=MINISBLACK"]
    height, width = bands[0].shape
    dataset = gdal.GetDriverByName("GTiff").Create(
        str(path), width, height, len(bands), data_type, options=options)
    try:
        dataset.SetGeoTransform(geotransform or old_transform)
        dataset.SetProjection(wkt or old_wkt)
        for index, values in enumerate(bands, start=1):
            dataset.GetRasterBand(index).WriteArray(values)
        if mask is not None:
            assert dataset.CreateMaskBand(gdal.GMF_PER_DATASET) == 0
            dataset.GetRasterBand(1).GetMaskBand().WriteArray(mask.astype(np.uint8) * 255)
    finally:
        dataset.Close()


def _edit_manifest(prep, change):
    path = prep / "preparation.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    change(manifest)
    path.write_text(json.dumps(manifest), encoding="utf-8")


def _set_pixel(name, value):
    def mutate(case):
        path = case["prep"] / name
        bands, _, _ = _read_bands(path)
        bands[0][0, 0] = value
        _rewrite(path, bands)
    return mutate


def _zero_aoi_and_analysis(case):
    for name in ("aoi_mask.tif", "analysis_mask.tif"):
        bands, _, _ = _read_bands(case["prep"] / name)
        _rewrite(case["prep"] / name, [np.zeros_like(bands[0])])


def _analysis_outside_validity(case):
    bands, _, _ = _read_bands(case["prep"] / "analysis_mask.tif")
    bands[0][~case["valid"]] = 1
    _rewrite(case["prep"] / "analysis_mask.tif", bands)


def _uint16(name, rgb=False):
    def mutate(case):
        path = case["prep"] / name
        bands, _, _ = _read_bands(path)
        mask = case["valid"] if rgb else None
        _rewrite(path, [b.astype(np.uint16) for b in bands], data_type=gdal.GDT_UInt16,
                 rgb=rgb, mask=mask)
    return mutate


def _implicit_mask(case):
    mask = np.ones(case["valid"].shape, bool)
    mask[1, 1] = False
    _rewrite(case["prep"] / "aoi_mask.tif", mask=mask)


def _rgb_without_photometric(case):
    _rewrite(case["prep"] / "image_rgb.tif", mask=case["valid"])


def _rgb_mask_differs(case):
    _rewrite(case["prep"] / "image_rgb.tif", rgb=True)  # aucun masque : tout valide


def _shifted_mask_grid(case):
    shifted = (X0 + PIXEL, PIXEL, 0.0, Y0, 0.0, -PIXEL)
    _rewrite(case["prep"] / "validity_mask.tif", geotransform=shifted)


def _other_crs(case):
    _rewrite(case["prep"] / "aoi_mask.tif", wkt=_wkt(4471))


def _manifest(change):
    return lambda case: _edit_manifest(case["prep"], change)


def _add_count(manifest):
    manifest["counts"]["aoi_pixels"] += 1


def _shift_grid(manifest):
    manifest["grid"]["geotransform"][0] += 1.0


REFUSALS = {
    "masque non binaire": (_set_pixel("analysis_mask.tif", 2), "uniquement 0 et 1"),
    "masque d'analyse vide": (_zero_aoi_and_analysis, "vide"),
    "analysis différent de aoi AND validity": (_analysis_outside_validity, "n'est pas égal"),
    "masque UInt16": (_uint16("analysis_mask.tif"), "Type de bande incorrect"),
    "masque implicite": (_implicit_mask, "Masque implicite inattendu"),
    "comptages incohérents": (_manifest(_add_count), "Comptage de préparation incohérent"),
    "schéma inconnu": (_manifest(lambda m: m.update(schema_version=2)), "Schéma"),
    "schéma booléen": (_manifest(lambda m: m.update(schema_version=True)), "Schéma"),
    "statut incomplet": (_manifest(lambda m: m.update(status="running")), "non complète"),
    "RGB non Byte": (_uint16("image_rgb.tif", rgb=True), "Type de bande incorrect"),
    "interprétation RGB": (_rgb_without_photometric, "Interprétation RGB"),
    "grille du manifeste": (_manifest(_shift_grid), "Grilles incohérentes"),
    "grille d'un masque": (_shifted_mask_grid, "Grilles incohérentes"),
    "SCR d'un masque": (_other_crs, "SCR incohérents"),
    "masque RGB différent": (_rgb_mask_differs, "masques RGB"),
}


# --- 1, 2, 3 : vrai traitement complet --------------------------------------------------
def test_real_manifest_relu_identique_au_retour(sample):
    report = _run(sample)
    run = Path(report["output_directory"])

    saved = json.loads((run / "segmentation.json").read_text(encoding="utf-8"))
    assert saved == report
    assert report["status"] == "complete" and report["scope"] == "unclassified_segments"
    assert sorted(p.name for p in run.iterdir()) == sorted(report["files"])
    assert run.parent == sample["out"].resolve() and run.name.startswith("segmentation_")
    assert report["segments_sha256"] == _sha(run / "segments.tif")
    assert report["preparation"]["sha256"] == {name: _sha(sample["prep"] / name)
                                               for name in INPUTS}
    assert report["versions"]["scikit_image"] == skimage.__version__


def test_real_uint32_grille_scr_et_masque(sample):
    report = _run(sample)
    segments = _read_segments(Path(report["output_directory"]))
    analysis, _, _ = _read_bands(sample["prep"] / "analysis_mask.tif")
    analysis = analysis[0].astype(bool)

    assert segments["type"] == gdal.GDT_UInt32 and segments["count"] == 1
    assert segments["nodata"] is None
    assert segments["mask_flags"] == gdal.GMF_ALL_VALID
    assert tuple(segments["geotransform"]) == GRID
    assert persist._reference(segments["wkt"]).IsSame(persist._reference(_wkt()))
    values = segments["values"]
    assert np.all(values[~analysis] == 0) and np.all(values[analysis] > 0)
    assert report["diagnostics"]["objects"] == len(np.unique(values[analysis]))


def test_real_entrees_immuables(sample):
    before = _snapshot(sample["prep"])
    _run(sample)
    assert _snapshot(sample["prep"]) == before  # mêmes empreintes, aucun compagnon ajouté


# --- 4 : masques et connexité -------------------------------------------------------------
def test_real_trou_ilots_diagonale_pixel_isole(islands):
    report = _run(islands, config=SlicConfig(target_segment_area_m2=2.0))
    values = _read_segments(Path(report["output_directory"]))["values"]
    valid = islands["valid"]

    assert report["algorithm"]["slic_called"] is True
    assert np.all(values[~valid] == 0) and np.all(values[valid] > 0)
    assert np.all(values[5:8, 5:8] == 0)  # trou
    assert values[12, 12] != values[11, 11]  # la diagonale ne relie pas
    assert values[0, 19] not in set(np.unique(values[[0, 1], 18]).tolist()) - {0}
    island = set(np.unique(values[15:18, 15:18]).tolist())
    assert island.isdisjoint(np.unique(values[2:12, 2:12]).tolist())
    # Chaque identifiant forme une seule composante à quatre voisins.
    _, components = label(values, background=0, connectivity=1, return_num=True)
    assert components == len(np.unique(values[valid]))


# --- 5 : refus avant toute sortie --------------------------------------------------------
@pytest.mark.parametrize("case_name", list(REFUSALS))
def test_real_refus_des_entrees(sample, case_name):
    mutate, message = REFUSALS[case_name]
    mutate(sample)
    with pytest.raises(ValueError, match=message):
        _run(sample)
    assert list(sample["out"].iterdir()) == []


# --- 6 : refus du parent et de la taille -------------------------------------------------
def test_real_parent_absent(sample):
    with pytest.raises(FileNotFoundError):
        _run(sample, output_parent=sample["root"] / "absent")


def test_real_parent_fichier(sample):
    target = sample["root"] / "fichier.txt"
    target.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="dossiers existants"):
        _run(sample, output_parent=target)


@pytest.mark.parametrize("inside", [False, True])
def test_real_parent_dans_la_preparation(sample, inside):
    parent = sample["prep"] / "sous_dossier" if inside else sample["prep"]
    parent.mkdir(exist_ok=True)
    with pytest.raises(ValueError, match="extérieures"):
        _run(sample, output_parent=parent)
    if inside:
        assert list(parent.iterdir()) == []


def test_double_raster_trop_grand(sample, monkeypatch):
    # Double : limite abaissée ; la grille réelle (1 600 px) la dépasse alors.
    monkeypatch.setattr(persist, "MAX_PIXELS", 100)
    with pytest.raises(ValueError, match="limite du noyau"):
        _run(sample)
    assert list(sample["out"].iterdir()) == []


# --- 7 : noyau remplacé par un double ----------------------------------------------------
def _kernel(kind):
    def fake(rgb, mask, *, pixel_size_m, config):
        labels = np.zeros(mask.shape, np.uint32)
        labels[mask] = 1 + np.arange(int(mask.sum()), dtype=np.uint32)  # pixels uniques
        if kind == "type":
            return labels.astype(np.int64)
        if kind == "forme":
            return labels[:-1]
        if kind == "zéro intérieur":
            labels[tuple(np.argwhere(mask)[0])] = 0
        if kind == "positif extérieur":
            labels[tuple(np.argwhere(~mask)[0])] = 7
        if kind == "identifiant disjoint":
            labels = mask.astype(np.uint32)  # un seul identifiant pour plusieurs îlots
        return labels
    return fake


@pytest.mark.parametrize(("kind", "message"), [
    ("type", "uint32"),
    ("forme", "Dimensions"),
    ("zéro intérieur", "ne respectent pas le masque"),
    ("positif extérieur", "ne respectent pas le masque"),
    ("identifiant disjoint", "plusieurs objets disjoints"),
])
def test_double_noyau_refuse(islands, monkeypatch, kind, message):
    monkeypatch.setattr(persist, "segment_rgb", _kernel(kind))
    with pytest.raises(RuntimeError, match=message):
        _run(islands)
    assert list(islands["out"].iterdir()) == []


# --- 8 : diagnostics indépendants et concordance avec l'appel SLIC -----------------------
def test_diagnostics_valeurs_connues():
    mask = np.ones((4, 4), bool)
    labels = np.full((4, 4), 3, np.uint32)
    labels[0, 0] = 1  # 1 px
    labels[0, 1:] = 2  # 3 px
    labels[3, 0] = 4  # 1 px ; l'identifiant 3 garde 11 px
    diagnostics = persist._diagnostics(labels, mask, 0.5, SlicConfig(target_segment_area_m2=0.5))

    # Surfaces triées : 0.25, 0.25, 0.75, 2.75 m².
    assert diagnostics["area_m2"] == {
        "min": 0.25, "median": 0.5, "mean": 1.0, "p90": pytest.approx(2.15), "max": 2.75}
    assert diagnostics["requested_segments"] == 8  # ceil(4 m² / 0.5 m²)
    assert diagnostics["objects"] == 4
    assert diagnostics["objects_per_requested_segment"] == 0.5
    assert diagnostics["single_pixel_objects"] == 2
    assert diagnostics["single_pixel_object_fraction"] == 0.5  # par nombre
    assert diagnostics["single_pixel_area_fraction"] == 0.125  # par surface
    assert diagnostics["single_pixel_area_m2"] == 0.5
    assert diagnostics["largest_object_area_fraction"] == 11 / 16
    assert diagnostics["thresholds_applied"] is False


def test_diagnostics_une_seule_graine():
    mask = np.ones((3, 3), bool)
    labels = np.ones((3, 3), np.uint32)
    diagnostics = persist._diagnostics(labels, mask, 0.5, SlicConfig(target_segment_area_m2=1e6))
    assert diagnostics["requested_segments"] == 1


def test_real_une_seule_graine_sans_slic(islands, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("slic ne doit pas être appelée")

    monkeypatch.setattr(skimage.segmentation, "slic", forbidden)
    report = _run(islands, config=SlicConfig(target_segment_area_m2=1e6))
    assert report["algorithm"]["slic_called"] is False
    assert report["diagnostics"]["requested_segments"] == 1
    # Une région par composante à quatre voisins du masque.
    _, components = label(islands["valid"], connectivity=1, return_num=True)
    assert report["diagnostics"]["objects"] == components


def test_real_manifeste_concorde_avec_l_appel_slic(sample, monkeypatch):
    calls = []
    real_slic = skimage.segmentation.slic

    def spy(image, **kwargs):
        calls.append(kwargs)
        return real_slic(image, **kwargs)

    monkeypatch.setattr(skimage.segmentation, "slic", spy)
    config = SlicConfig(target_segment_area_m2=7.0, compactness=12.0, max_num_iter=8)
    report = _run(sample, config=config)

    assert len(calls) == 1
    call, algorithm = calls[0], report["algorithm"]
    # Formule identique : le nombre décrit est celui transmis à slic par segment.py.
    assert call["n_segments"] == report["diagnostics"]["requested_segments"]
    for key in ("enforce_connectivity", "sigma", "convert2lab", "min_size_factor",
                "max_size_factor", "slic_zero", "start_label", "channel_axis"):
        assert call[key] == algorithm[key], key
    assert call["compactness"] == report["configuration"]["compactness"]
    assert call["max_num_iter"] == report["configuration"]["max_num_iter"]
    # Le nombre final d'objets n'est pas exigé égal au nombre demandé.
    assert report["diagnostics"]["objects"] >= 1


# --- 9 : appels successifs --------------------------------------------------------------
def test_real_appels_successifs(sample):
    source = _snapshot(sample["prep"])
    first = _run(sample)
    first_files = _snapshot(Path(first["output_directory"]))
    second = _run(sample)

    assert first["output_directory"] != second["output_directory"]
    assert _snapshot(Path(first["output_directory"])) == first_files
    assert _snapshot(sample["prep"]) == source


# --- 10 : échecs injectés après création du dossier --------------------------------------
def _failing_write(monkeypatch):
    real = persist._write_segments

    def write(path, labels, grid):
        real(path, labels, grid)
        raise OSError("écriture simulée en échec")

    monkeypatch.setattr(persist, "_write_segments", write)
    return OSError, "écriture simulée"


def _failing_close(monkeypatch):
    real = persist._check
    state = {"writing": False}

    def check(code, operation):
        if operation == "écriture des segments":
            state["writing"] = True
        if state["writing"] and operation == "fermeture du dataset":
            state["writing"] = False
            raise RuntimeError("Close simulé en échec")
        real(code, operation)

    monkeypatch.setattr(persist, "_check", check)
    return RuntimeError, "Close simulé"


def _altered_reread(monkeypatch):
    real = persist._read_raster

    def read(path, **kwargs):
        values, grid, masks, colors = real(path, **kwargs)
        if path.name == "segments.tif":
            values = values.copy()
            values[values > 0] += 1
        return values, grid, masks, colors

    monkeypatch.setattr(persist, "_read_raster", read)
    return RuntimeError, "relus"


def _altered_json(monkeypatch):
    real = persist._read_json
    monkeypatch.setattr(persist, "_read_json",
                        lambda path: {} if path.name == "segmentation.tmp" else real(path))
    return RuntimeError, "manifeste temporaire"


def _failing_replace(monkeypatch):
    def replace(self, target):
        raise PermissionError("replace simulé en échec")

    monkeypatch.setattr(persist.Path, "replace", replace)
    return PermissionError, "replace simulé"


@pytest.mark.parametrize("inject", [
    _failing_write, _failing_close, _altered_reread, _altered_json, _failing_replace])
def test_double_echec_nettoie_seulement_son_dossier(sample, monkeypatch, inject):
    keep = sample["out"] / "keep.txt"
    keep.write_text("conserver", encoding="utf-8")
    source = _snapshot(sample["prep"])

    with monkeypatch.context() as patch:
        error_type, message = inject(patch)
        with pytest.raises(error_type, match=message):
            _run(sample)

    assert list(sample["out"].iterdir()) == [keep]
    assert keep.read_text(encoding="utf-8") == "conserver"
    assert _snapshot(sample["prep"]) == source


# --- 11 : nettoyage impossible -----------------------------------------------------------
def test_double_rmtree_en_echec(sample, monkeypatch):
    keep = sample["out"] / "keep.txt"
    keep.write_text("conserver", encoding="utf-8")
    real_rmtree = shutil.rmtree

    def blocked(path, *args, **kwargs):
        raise PermissionError("suppression bloquée pour le test")

    try:
        with monkeypatch.context() as patch:
            _failing_write(patch)
            patch.setattr(persist.shutil, "rmtree", blocked)
            with pytest.raises(RuntimeError, match="nettoyage incomplet") as caught:
                _run(sample)

        residual = [p for p in sample["out"].iterdir() if p.is_dir()]
        assert len(residual) == 1 and residual[0].name.startswith("segmentation_")
        assert str(residual[0]) in str(caught.value)
        assert isinstance(caught.value.__cause__, OSError)
        assert "écriture simulée" in str(caught.value.__cause__)
        assert not (residual[0] / "segmentation.json").exists()
        assert keep.read_text(encoding="utf-8") == "conserver"
    finally:
        # Retirer uniquement les résidus créés par ce test.
        for path in sample["out"].iterdir():
            if path.is_dir() and path.name.startswith("segmentation_"):
                real_rmtree(path)


# --- 12 : mutation des entrées par un double ---------------------------------------------
def _touch_manifest(prep):
    with (prep / "preparation.json").open("a", encoding="utf-8") as stream:
        stream.write("\n")  # mutation propre au test, sur sa copie temporaire


def test_double_mutation_pendant_le_calcul(sample, monkeypatch):
    real = persist.segment_rgb

    def mutating(*args, **kwargs):
        labels = real(*args, **kwargs)
        _touch_manifest(sample["prep"])
        return labels

    monkeypatch.setattr(persist, "segment_rgb", mutating)
    with pytest.raises(RuntimeError, match="pendant le calcul"):
        _run(sample)
    assert list(sample["out"].iterdir()) == []


def test_double_mutation_avant_publication(sample, monkeypatch):
    real = persist._write_segments

    def mutating(path, labels, grid):
        real(path, labels, grid)
        _touch_manifest(sample["prep"])

    monkeypatch.setattr(persist, "_write_segments", mutating)
    with pytest.raises(RuntimeError, match="avant publication"):
        _run(sample)
    assert list(sample["out"].iterdir()) == []


# --- 13 : modes d'exceptions GDAL, chacun dans son processus ------------------------------
_MODE_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from osgeo import gdal
(gdal.UseExceptions if sys.argv[2] == "on" else gdal.DontUseExceptions)()
from cynogis.landcover_processing.persist import persist_segmentation
prep, out = Path(sys.argv[3]), Path(sys.argv[4])
report = persist_segmentation(preparation_directory=prep, output_parent=out)
manifest = Path(report["output_directory"]) / "segmentation.json"
assert json.loads(manifest.read_text(encoding="utf-8")) == report
from cynogis.core.landcover_execution import (
    SegmentationCancelledError, SegmentationControl)
listing = sorted(p.name for p in out.iterdir())
received = []
control = SegmentationControl(on_progress=received.append,
                              is_cancelled=lambda: bool(received) and received[-1] == 90)
try:
    persist_segmentation(preparation_directory=prep, output_parent=out, control=control)
except SegmentationCancelledError:
    print("annulation SegmentationCancelledError")
assert sorted(p.name for p in out.iterdir()) == listing
(prep / "analysis_mask.tif").write_bytes(b"pas un GeoTIFF")
listing = sorted(p.name for p in out.iterdir())
try:
    persist_segmentation(preparation_directory=prep, output_parent=out)
except RuntimeError as exc:
    print("refus RuntimeError")
else:
    raise SystemExit("aucun refus")
assert sorted(p.name for p in out.iterdir()) == listing
print("exceptions", gdal.GetUseExceptions())
"""


def _subprocess(*arguments):
    return subprocess.run(
        [sys.executable, "-c", *arguments], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=300, check=False)


@pytest.mark.parametrize(("mode", "flag"), [("on", 1), ("off", 0)])
def test_real_modes_d_exceptions_gdal(sample, mode, flag):
    result = _subprocess(_MODE_SCRIPT, str(PLUGIN_DIR), mode, str(sample["prep"]),
                         str(sample["out"]))
    assert result.returncode == 0, result.stderr[-2000:]
    assert "refus RuntimeError" in result.stdout
    assert "annulation SegmentationCancelledError" in result.stdout
    assert f"exceptions {flag}" in result.stdout
    assert len(list(sample["out"].iterdir())) == 1


# --- 14 : le plugin n'importe pas ce module au démarrage --------------------------------
_IMPORT_SCRIPT = r"""
import sys
sys.path.insert(0, sys.argv[1])
import cynogis
import cynogis.landcover_processing
from cynogis import plugin  # noqa: F401
loaded = [name for name in ("cynogis.landcover_processing.persist",
                            "cynogis.landcover_processing.segment", "skimage")
          if name in sys.modules]
print("chargés", loaded)
"""


def test_real_import_du_plugin_sans_persist():
    result = _subprocess(_IMPORT_SCRIPT, str(PLUGIN_DIR))
    assert result.returncode == 0, result.stderr[-2000:]
    assert "chargés []" in result.stdout


# --- Contrôle coopératif (SegmentationControl) -------------------------------------------
CHECKPOINTS = [0, 10, 20, 25, 70, 75, 80, 85, 90, 95, 99]


class Recorder:
    """Progression reçue ; annulation demandée au checkpoint choisi."""

    def __init__(self, cancel_at=None):
        self.received, self.cancel_at, self.cancelled = [], cancel_at, False

    def progress(self, value):
        self.received.append(value)
        if value == self.cancel_at:
            self.cancelled = True

    def control(self):
        return SegmentationControl(on_progress=self.progress,
                                   is_cancelled=lambda: self.cancelled)


def _keep(case):
    keep = case["out"] / "keep.txt"
    keep.write_text("conserver", encoding="utf-8")
    return keep


def test_real_controle_sequence_exacte(sample):
    recorder = Recorder()
    report = _run(sample, control=recorder.control())
    count = len(recorder.received)

    assert recorder.received == [float(value) for value in CHECKPOINTS]
    assert 100.0 not in recorder.received
    saved = json.loads((Path(report["output_directory"]) / "segmentation.json")
                       .read_text(encoding="utf-8"))
    assert saved == report
    assert len(recorder.received) == count  # aucun callback après le retour


def test_real_sans_controle_comportement_anterieur(sample):
    report = _run(sample)
    saved = json.loads((Path(report["output_directory"]) / "segmentation.json")
                       .read_text(encoding="utf-8"))
    assert saved == report and report["status"] == "complete"


@pytest.mark.parametrize("control", [PreparationControl(), object(), "x"],
                         ids=["PreparationControl", "object", "str"])
def test_real_controle_de_type_incorrect(sample, control):
    with pytest.raises(ValueError, match="SegmentationControl"):
        _run(sample, control=control)
    assert list(sample["out"].iterdir()) == []


def test_double_annulation_initiale_sans_lecture(sample, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("aucune lecture des entrées attendue")

    monkeypatch.setattr(persist, "_fingerprints", forbidden)
    monkeypatch.setattr(persist, "_load_inputs", forbidden)
    received = []
    control = SegmentationControl(on_progress=received.append, is_cancelled=lambda: True)
    with pytest.raises(SegmentationCancelledError):
        _run(sample, control=control)
    assert received == [] and list(sample["out"].iterdir()) == []


@pytest.mark.parametrize("cancel_at", CHECKPOINTS)
def test_real_annulation_a_chaque_checkpoint(sample, cancel_at):
    keep = _keep(sample)
    source = _snapshot(sample["prep"])
    recorder = Recorder(cancel_at)

    with pytest.raises(SegmentationCancelledError):
        _run(sample, control=recorder.control())

    assert recorder.received[-1] == float(cancel_at)
    assert list(sample["out"].iterdir()) == [keep]
    assert keep.read_text(encoding="utf-8") == "conserver"
    assert _snapshot(sample["prep"]) == source


def test_real_annulation_a_99_supprime_le_temporaire(sample):
    seen = []
    recorder = Recorder(99)

    def progress(value):
        if value == 99:
            run = next(p for p in sample["out"].iterdir() if p.is_dir())
            seen.extend(sorted(p.name for p in run.iterdir()))
        recorder.progress(value)

    control = SegmentationControl(on_progress=progress, is_cancelled=lambda: recorder.cancelled)
    with pytest.raises(SegmentationCancelledError):
        _run(sample, control=control)

    assert seen == ["segmentation.tmp", "segments.tif"]
    assert list(sample["out"].iterdir()) == []


@pytest.mark.parametrize("fail_at", [85, 90, 95, 99])
def test_real_callback_en_erreur_apres_creation(sample, fail_at):
    keep = _keep(sample)

    def progress(value):
        if value == fail_at:
            raise RuntimeError(f"callback en échec à {value}")

    with pytest.raises(RuntimeError, match=f"callback en échec à {float(fail_at)}") as caught:
        _run(sample, control=SegmentationControl(on_progress=progress))
    assert not isinstance(caught.value, SegmentationCancelledError)
    assert list(sample["out"].iterdir()) == [keep]


def test_double_nettoyage_impossible_apres_annulation(sample, monkeypatch):
    keep = _keep(sample)
    real_rmtree = shutil.rmtree

    def blocked(path, *args, **kwargs):
        raise PermissionError("suppression bloquée pour le test")

    try:
        with monkeypatch.context() as patch:
            patch.setattr(persist.shutil, "rmtree", blocked)
            with pytest.raises(RuntimeError, match="nettoyage incomplet") as caught:
                _run(sample, control=Recorder(90).control())

        residual = [p for p in sample["out"].iterdir() if p.is_dir()]
        assert len(residual) == 1 and str(residual[0]) in str(caught.value)
        assert isinstance(caught.value.__cause__, SegmentationCancelledError)
        assert not (residual[0] / "segmentation.json").exists()
        assert keep.read_text(encoding="utf-8") == "conserver"
    finally:
        # rmtree restauré par monkeypatch ; retirer seulement les dossiers de ce test.
        for path in sample["out"].iterdir():
            if path.is_dir() and path.name.startswith("segmentation_"):
                real_rmtree(path)


def test_double_slic_demande_l_annulation(sample, monkeypatch):
    recorder = Recorder()
    real_slic = skimage.segmentation.slic

    def cancelling_slic(image, **kwargs):
        labels = real_slic(image, **kwargs)
        recorder.cancelled = True  # labels valides malgré tout
        return labels

    def forbidden_write(*args, **kwargs):
        raise AssertionError("aucune écriture attendue")

    monkeypatch.setattr(skimage.segmentation, "slic", cancelling_slic)
    monkeypatch.setattr(persist, "_write_segments", forbidden_write)
    with pytest.raises(SegmentationCancelledError):
        _run(sample, control=recorder.control())

    assert recorder.received == [0.0, 10.0, 20.0, 25.0]  # arrêt au checkpoint 70
    assert list(sample["out"].iterdir()) == []


def test_double_slic_annule_puis_echoue(sample, monkeypatch):
    recorder = Recorder()

    def failing_slic(image, **kwargs):
        recorder.cancelled = True
        raise RuntimeError("panne SLIC simulée")

    monkeypatch.setattr(skimage.segmentation, "slic", failing_slic)
    with pytest.raises(RuntimeError, match="panne SLIC simulée") as caught:
        _run(sample, control=recorder.control())
    assert not isinstance(caught.value, SegmentationCancelledError)
    assert list(sample["out"].iterdir()) == []


def test_double_annulation_tardive_apres_99(sample, monkeypatch):
    recorder = Recorder()
    real_replace = Path.replace

    def late_replace(self, target):
        recorder.cancelled = True  # trop tard : plus aucun checkpoint
        return real_replace(self, target)

    monkeypatch.setattr(persist.Path, "replace", late_replace)
    report = _run(sample, control=recorder.control())

    run = Path(report["output_directory"])
    assert json.loads((run / "segmentation.json").read_text(encoding="utf-8")) == report
    assert sorted(p.name for p in run.iterdir()) == ["segmentation.json", "segments.tif"]
    assert recorder.cancelled
    assert recorder.received == [float(value) for value in CHECKPOINTS]
