"""Persistance des caractéristiques OBIA (landcover_processing/persist_features.py).

Nécessite le Python de QGIS (osgeo) et scikit-image : chaîne réelle préparation →
segmentation → caractéristiques sur GeoTIFF synthétiques. Dans le venv, suite ignorée.

    .venv/Scripts/python scripts/run_qgis_integration.py -- -q TEST
    (TEST = tests/integration/test_persist_features.py)

Les refus géométriques passent après les contrôles d'empreinte : les manifestes des
fixtures sont réécrits avec les nouvelles empreintes pour les atteindre.
"""
import json
import shutil
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
gdal = pytest.importorskip("osgeo.gdal")
pytest.importorskip("skimage", reason="scikit-image absent : suite ignorée")

from test_landcover_persist import (  # noqa: E402
    PIXEL,
    X0,
    Y0,
    _prepare,
    _read_bands,
    _rewrite,
    _texture,
    _wkt,
)

from cynogis.landcover_processing import persist  # noqa: E402
from cynogis.landcover_processing import persist_features as pf  # noqa: E402
from cynogis.landcover_processing.object_features import extract_object_features  # noqa: E402

UINT32_MAX = 4_294_967_295
FILES = ["edges.npy", "features.json", "objects.npy"]


def _chain(root, rgb, valid, labels=None, monkeypatch=None):
    """Préparation réelle puis segmentation réelle (ou labels imposés au noyau)."""
    root.mkdir(parents=True, exist_ok=True)
    prep = _prepare(root, rgb, valid)
    if labels is not None:
        monkeypatch.setattr(persist, "segment_rgb", lambda *a, **k: labels.copy())
    segs = root / "segmentations"
    segs.mkdir()
    seg = Path(persist.persist_segmentation(
        preparation_directory=prep, output_parent=segs)["output_directory"])
    if labels is not None:
        monkeypatch.undo()
    out = root / "features"
    out.mkdir()
    return {"prep": prep, "seg": seg, "out": out, "root": root}


def _run(case, **overrides):
    arguments = {"preparation_directory": case["prep"],
                 "segmentation_directory": case["seg"], "output_parent": case["out"]}
    arguments.update(overrides)
    return pf.persist_object_features(**arguments)


def _load(run):
    return {name: np.load(run / f"{name}.npy", allow_pickle=False)
            for name in ("objects", "edges")}


def _keep(case):
    keep = case["out"] / "keep.txt"
    keep.write_text("conserver", encoding="utf-8")
    return keep


@pytest.fixture
def sample(tmp_path):
    valid = np.ones((30, 30), bool)
    valid[0, :4] = False
    valid[20:23, 20:23] = False
    return _chain(tmp_path, _texture(30, 30), valid)


# --- Chaîne réelle ---------------------------------------------------------------------
def test_real_tables_identiques_au_noyau(sample):
    report = _run(sample)
    run = Path(report["output_directory"])

    assert sorted(p.name for p in run.iterdir()) == FILES == sorted(report["files"])
    assert run.parent == sample["out"].resolve() and run.name.startswith("features_")
    saved = json.loads((run / "features.json").read_text(encoding="utf-8"))
    assert saved == report and report["status"] == "complete"
    for name in ("objects", "edges"):
        assert report["tables"][name]["sha256"] == persist._sha256(run / f"{name}.npy")

    rgb, mask, _ = persist._load_inputs(sample["prep"])
    labels = persist._read_raster(sample["seg"] / "segments.tif", bands=1,
                                  data_type=gdal.GDT_UInt32)[0]
    expected = extract_object_features(rgb, labels, mask, pixel_size_m=PIXEL)
    loaded = _load(run)
    for name, table in (("objects", expected.objects), ("edges", expected.edges)):
        assert loaded[name].dtype == table.dtype
        assert report["tables"][name]["rows"] == len(table)
        for field in table.dtype.names:
            assert np.array_equal(loaded[name][field], table[field]), (name, field)
    assert report["diagnostics"]["object_count"] == len(expected.objects)
    assert report["diagnostics"]["analysis_pixels"] == int(mask.sum())


def test_real_sources_immuables_et_appels_successifs(sample):
    before = pf._snapshot(sample["prep"], sample["seg"])
    first, second = _run(sample), _run(sample)
    assert first["output_directory"] != second["output_directory"]
    assert pf._snapshot(sample["prep"], sample["seg"]) == before


# --- Cas calculables -------------------------------------------------------------------
def _labels(rows):
    return np.array(rows, dtype=np.uint32)


@pytest.mark.parametrize(("labels", "objects", "edges"), [
    # [[2,2],[9,9]], 0,5 m : deux objets de 0,5 m², une arête de deux côtés = 1 m.
    (_labels([[2, 2], [9, 9]]), [(2, 0.5, 0.5, 1.0), (9, 0.5, 1.5, 1.0)], [(2, 9, 2, 1.0)]),
    (_labels([[1, 1], [1, 1]]), [(1, 1.0, 1.0, 1.0)], []),  # un seul objet, E = 0
    (_labels([[1, 1], [UINT32_MAX] * 2]),
     [(1, 0.5, 0.5, 1.0), (UINT32_MAX, 0.5, 1.5, 1.0)], [(1, UINT32_MAX, 2, 1.0)]),
], ids=["deux_objets", "objet_unique", "uint32_max"])
def test_real_valeurs_a_la_main(tmp_path, monkeypatch, labels, objects, edges):
    case = _chain(tmp_path, _texture(2, 2), np.ones((2, 2), bool), labels, monkeypatch)
    loaded = _load(Path(_run(case)["output_directory"]))

    got = [(int(o["segment_id"]), float(o["area_m2"]), float(o["center_row"]),
            float(o["center_col"])) for o in loaded["objects"]]
    assert got == objects
    assert [(int(e["segment_a"]), int(e["segment_b"]), int(e["shared_pixel_sides"]),
             float(e["shared_boundary_m"])) for e in loaded["edges"]] == edges
    assert loaded["edges"].dtype == pf._schema()[1]


# --- Provenance --------------------------------------------------------------------------
def test_real_copie_deplacee_acceptee(sample):
    moved = sample["root"] / "ailleurs"
    case = dict(sample,
                prep=Path(shutil.copytree(sample["prep"], moved / "prep")),
                seg=Path(shutil.copytree(sample["seg"], moved / "seg")))
    assert _run(case)["status"] == "complete"


def test_real_autre_preparation_meme_grille_refusee(sample):
    other_root = sample["root"] / "autre"
    other_root.mkdir()
    other = _prepare(other_root, _texture(30, 30, seed=7), np.ones((30, 30), bool))
    with pytest.raises(ValueError, match="ne correspond pas"):
        _run(sample, preparation_directory=other)
    assert list(sample["out"].iterdir()) == []


# --- Refus après adaptation des empreintes ----------------------------------------------
def _edit_seg_manifest(case, change):
    path = case["seg"] / "segmentation.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    change(manifest)
    manifest["preparation"]["sha256"] = persist._fingerprints(case["prep"])
    manifest.setdefault("segments_sha256", persist._sha256(case["seg"] / "segments.tif"))
    path.write_text(json.dumps(manifest), encoding="utf-8")


def _rehash_segments(manifest, case):
    manifest["segments_sha256"] = persist._sha256(case["seg"] / "segments.tif")


def _mask_non_binary(case):
    path = case["prep"] / "analysis_mask.tif"
    bands, _, _ = _read_bands(path)
    bands[0][5, 5] = 2
    _rewrite(path, bands)
    _edit_seg_manifest(case, lambda m: None)


def _segments(**kwargs):
    def mutate(case):
        path = case["seg"] / "segments.tif"
        bands, _, _ = _read_bands(path)
        if kwargs.pop("outside", False):
            bands[0][0, 0] = 1  # pixel hors masque d'analyse
        _rewrite(path, bands, data_type=gdal.GDT_UInt32, **kwargs)
        _edit_seg_manifest(case, lambda m: _rehash_segments(m, case))
    return mutate


def _manifest(change):
    return lambda case: _edit_seg_manifest(case, change)


REFUSALS = {
    "masque non binaire": (_mask_non_binary, "uniquement 0 et 1"),
    "emprise des segments": (
        _segments(geotransform=(X0 + PIXEL, PIXEL, 0.0, Y0, 0.0, -PIXEL)), "Grilles"),
    "SCR des segments": (_segments(wkt=_wkt(4471)), "SCR incohérents"),
    "labels hors masque": (_segments(outside=True), "analysis_mask"),
    "grille du manifeste": (
        _manifest(lambda m: m["grid"]["geotransform"].__setitem__(0, X0 + 1)), "Grilles"),
    "hash de segments faux": (_manifest(lambda m: m.update(segments_sha256="0" * 64)),
                              "diffère du manifeste"),
    "statut": (_manifest(lambda m: m.update(status="running")), "incompatible"),
    "schéma booléen": (_manifest(lambda m: m.update(schema_version=True)), "incompatible"),
    "grille absente": (_manifest(lambda m: m.pop("grid")), "Grille de segmentation"),
}


@pytest.mark.parametrize("name", list(REFUSALS))
def test_real_refus_des_sources(sample, name):
    mutate, message = REFUSALS[name]
    mutate(sample)
    with pytest.raises(ValueError, match=message):
        _run(sample)
    assert list(sample["out"].iterdir()) == []


@pytest.mark.parametrize("overrides", [
    lambda c: {"output_parent": Path("relatif")},
    lambda c: {"segmentation_directory": c["prep"]},
    lambda c: {"output_parent": c["seg"]},
], ids=["relatif", "sources_identiques", "sortie_dans_source"])
def test_refus_des_chemins(sample, overrides):
    with pytest.raises(ValueError):
        _run(sample, **overrides(sample))
    assert list(sample["out"].iterdir()) == []


# --- Échecs injectés après création du dossier -----------------------------------------
def _second_write(patch, case):
    real = pf._save_table

    def save(path, array):
        if path.name == "edges.npy":
            raise OSError("seconde écriture simulée en échec")
        return real(path, array)

    patch.setattr(pf, "_save_table", save)
    return OSError, "seconde écriture"


def _altered_reread(patch, case):
    real = np.load

    def load(*args, **kwargs):
        table = real(*args, **kwargs).copy()
        table["pixel_count"] += 1
        return table

    patch.setattr(np, "load", load)
    return RuntimeError, "altérée à la relecture"


def _altered_json(patch, case):
    real = persist._read_json
    patch.setattr(persist, "_read_json",
                  lambda path: {} if path.name == "features.tmp" else real(path))
    return RuntimeError, "relu à l'identique"


def _input_mutation(patch, case):
    real = pf.extract_object_features

    def extract(*args, **kwargs):
        with (case["prep"] / "preparation.json").open("a", encoding="utf-8") as stream:
            stream.write("\n")
        return real(*args, **kwargs)

    patch.setattr(pf, "extract_object_features", extract)
    return RuntimeError, "sources ont changé"


def _failing_replace(patch, case):
    def replace(self, target):
        raise PermissionError("replace simulé en échec")

    patch.setattr(pf.Path, "replace", replace)
    return PermissionError, "replace simulé"


@pytest.mark.parametrize("inject", [
    _second_write, _altered_reread, _altered_json, _input_mutation, _failing_replace])
def test_double_echec_nettoie_seulement_son_dossier(sample, monkeypatch, inject):
    keep = _keep(sample)
    with monkeypatch.context() as patch:
        error_type, message = inject(patch, sample)
        with pytest.raises(error_type, match=message):
            _run(sample)
    assert list(sample["out"].iterdir()) == [keep]
    assert keep.read_text(encoding="utf-8") == "conserver"


def test_double_rmtree_en_echec(sample, monkeypatch):
    keep = _keep(sample)
    real_rmtree = shutil.rmtree

    def blocked(path, *args, **kwargs):
        raise PermissionError("suppression bloquée pour le test")

    try:
        with monkeypatch.context() as patch:
            _second_write(patch, sample)
            patch.setattr(pf.shutil, "rmtree", blocked)
            with pytest.raises(RuntimeError, match="nettoyage incomplet") as caught:
                _run(sample)
        residual = [p for p in sample["out"].iterdir() if p.is_dir()]
        assert len(residual) == 1 and str(residual[0]) in str(caught.value)
        assert isinstance(caught.value.__cause__, OSError)
        assert "seconde écriture" in str(caught.value)
        assert not (residual[0] / "features.json").exists()
        assert keep.read_text(encoding="utf-8") == "conserver"
    finally:
        for path in sample["out"].iterdir():
            if path.is_dir() and path.name.startswith("features_"):
                real_rmtree(path)
