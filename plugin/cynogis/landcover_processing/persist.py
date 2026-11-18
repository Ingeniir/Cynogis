"""Persistance du prototype OBIA : segments et diagnostics, sans QGIS.

Ne pas importer ce module dans __init__.py et ne pas le raccorder au MCP.

Entrée : dossier de préparation native complète (schéma 1).
Sortie : nouveau dossier segmentation_* dans un parent existant, extérieur
au dossier de préparation. Aucun fichier préparé n'est réécrit.

Pas de classification, fusion ou vectorisation dans ce lot.
Annulation coopérative entre phases, jamais au milieu d'un appel SLIC ou GDAL.
L'appel est synchrone : ne pas l'exécuter sur le thread graphique de QGIS.

Le manifeste est le marqueur de succès, publié en dernier par replace.
Cela ne constitue pas une garantie de durabilité après coupure de courant.
Les empreintes avant/après détectent des changements persistants des entrées,
mais ne remplacent pas un verrou contre les écritures concurrentes externes.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
from osgeo import gdal, osr

from ..core.landcover_execution import SegmentationControl
from .segment import MAX_PIXELS, MAX_REQUESTED_SEGMENTS, SlicConfig, segment_rgb

_INPUT_NAMES = (
    "preparation.json",
    "image_rgb.tif",
    "aoi_mask.tif",
    "validity_mask.tif",
    "analysis_mask.tif",
)


def _check(code: int, operation: str) -> None:
    if code != gdal.CE_None:
        raise RuntimeError(f"Échec GDAL : {operation} (code {code}).")


@contextmanager
def _dataset(dataset):
    """Ferme explicitement ; une fermeture ratée conserve l'erreur initiale."""
    if dataset is None:
        raise RuntimeError("GDAL n'a pas fourni de dataset.")
    try:
        yield dataset
    except BaseException as original:
        try:
            _check(dataset.Close(), "fermeture après erreur")
        except Exception as closing:
            raise RuntimeError(
                f"Erreur initiale : {type(original).__name__}: {original} ; "
                f"fermeture impossible : {type(closing).__name__}: {closing}"
            ) from original
        raise
    else:
        _check(dataset.Close(), "fermeture du dataset")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fingerprints(directory: Path) -> dict[str, str]:
    return {name: _sha256(directory / name) for name in _INPUT_NAMES}


def _reject_constant(value: str) -> None:
    raise ValueError(f"Constante JSON non finie refusée : {value}.")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream, parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} doit contenir un objet JSON.")
    return value


def _reference(wkt: str):
    if not isinstance(wkt, str) or not wkt.strip():
        raise ValueError("SCR absent ou invalide.")
    reference = osr.SpatialReference()
    _check(reference.ImportFromWkt(wkt), "lecture du SCR")
    reference.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    if not reference.IsProjected():
        raise ValueError("Un SCR projeté est requis.")
    if not math.isclose(reference.GetLinearUnits(), 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Le SCR doit être exprimé en mètres.")
    return reference


def _grid(dataset) -> dict[str, Any]:
    width, height = dataset.RasterXSize, dataset.RasterYSize
    if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
        raise ValueError("Grille vide ou supérieure à la limite du noyau SLIC.")
    transform = dataset.GetGeoTransform(can_return_null=True)
    if transform is None or not all(math.isfinite(v) for v in transform):
        raise ValueError("Géotransformation absente ou non finie.")
    if transform[2] != 0 or transform[4] != 0:
        raise ValueError("Les grilles tournées ne sont pas prises en charge.")
    if transform[1] <= 0 or transform[5] >= 0:
        raise ValueError("Une grille nord en haut est requise.")
    if not math.isclose(transform[1], -transform[5], rel_tol=1e-9, abs_tol=0):
        raise ValueError("Les pixels doivent être carrés.")
    area = transform[1] * transform[1]
    if not math.isfinite(area) or area <= 0:
        raise ValueError("Surface de pixel invalide.")
    wkt = dataset.GetProjectionRef()
    _reference(wkt)
    return {
        "width": width,
        "height": height,
        "geotransform": list(transform),
        "crs_wkt": wkt,
    }


def _same_grid(actual: dict, expected: dict) -> None:
    for key in ("width", "height", "geotransform"):
        if actual.get(key) != expected.get(key):
            raise ValueError(f"Grilles incohérentes : {key}.")
    if not _reference(actual.get("crs_wkt")).IsSame(
        _reference(expected.get("crs_wkt"))
    ):
        raise ValueError("SCR incohérents entre les entrées.")


def _read_raster(path: Path, *, bands: int, data_type: int):
    """Lecture bornée avant allocation, avec géoréférencement interne seul."""
    with _dataset(gdal.OpenEx(
        str(path),
        gdal.OF_RASTER | gdal.OF_READONLY,
        allowed_drivers=["GTiff"],
        open_options=["GEOREF_SOURCES=INTERNAL"],
    )) as dataset:
        grid = _grid(dataset)
        if dataset.RasterCount != bands:
            raise ValueError(f"Nombre de bandes incorrect : {path.name}.")
        arrays = []
        masks = []
        colors = []
        for index in range(1, bands + 1):
            band = dataset.GetRasterBand(index)
            if band.DataType != data_type:
                raise ValueError(f"Type de bande incorrect : {path.name}.")
            if band.GetNoDataValue() is not None:
                raise ValueError(f"NoData numérique interdit : {path.name}.")
            array = band.ReadAsArray()
            mask = band.GetMaskBand().ReadAsArray()
            shape = (grid["height"], grid["width"])
            if array is None or mask is None or array.shape != shape or mask.shape != shape:
                raise RuntimeError(f"Lecture raster incomplète : {path.name}.")
            arrays.append(array)
            masks.append(mask != 0)
            colors.append(band.GetColorInterpretation())
        # Plus aucun accès à un objet bande après la fermeture du dataset.
        band = None
    values = arrays[0] if bands == 1 else np.stack(arrays, axis=-1)
    return values, grid, masks, colors


def _load_inputs(directory: Path):
    manifest = _read_json(directory / "preparation.json")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("Schéma de préparation non pris en charge.")
    if manifest.get("status") != "complete":
        raise ValueError("Préparation non complète.")
    expected_grid = manifest.get("grid")
    if not isinstance(expected_grid, dict):
        raise ValueError("Grille absente du manifeste de préparation.")

    rgb, grid, rgb_masks, colors = _read_raster(
        directory / "image_rgb.tif", bands=3, data_type=gdal.GDT_Byte,
    )
    _same_grid(grid, expected_grid)
    if colors != [gdal.GCI_RedBand, gdal.GCI_GreenBand, gdal.GCI_BlueBand]:
        raise ValueError("Interprétation RGB incorrecte dans l'image préparée.")

    binary = {}
    for name in ("aoi_mask", "validity_mask", "analysis_mask"):
        values, mask_grid, masks, _ = _read_raster(
            directory / f"{name}.tif", bands=1, data_type=gdal.GDT_Byte,
        )
        _same_grid(mask_grid, grid)
        if not np.all((values == 0) | (values == 1)):
            raise ValueError(f"{name} doit contenir uniquement 0 et 1.")
        if not np.all(masks[0]):
            raise ValueError(f"Masque implicite inattendu sur {name}.")
        binary[name] = values.astype(bool)

    aoi = binary["aoi_mask"]
    validity = binary["validity_mask"]
    analysis = binary["analysis_mask"]
    if not np.array_equal(analysis, aoi & validity):
        raise ValueError("analysis_mask n'est pas égal à aoi_mask AND validity_mask.")
    if not all(np.array_equal(mask, validity) for mask in rgb_masks):
        raise ValueError("Les masques RGB ne correspondent pas à validity_mask.")

    total = int(analysis.size)
    aoi_count = int(np.count_nonzero(aoi))
    valid_count = int(np.count_nonzero(validity))
    analyzed = int(np.count_nonzero(analysis))
    if analyzed == 0:
        raise ValueError("Le masque d'analyse est vide.")
    observed = {
        "total_pixels": total,
        "aoi_pixels": aoi_count,
        "valid_pixels_whole_raster": valid_count,
        "invalid_pixels_whole_raster": total - valid_count,
        "analysis_pixels": analyzed,
        "invalid_pixels_inside_aoi": aoi_count - analyzed,
        "valid_pixels_outside_aoi": valid_count - analyzed,
    }
    counts = manifest.get("counts")
    if not isinstance(counts, dict):
        raise ValueError("Comptages absents du manifeste de préparation.")
    for key, value in observed.items():
        if type(counts.get(key)) is not int or counts[key] != value:
            raise ValueError(f"Comptage de préparation incohérent : {key}.")
    return rgb, analysis, grid


def _diagnostics(labels, mask, resolution: float, config: SlicConfig) -> dict:
    if not isinstance(labels, np.ndarray) or labels.dtype != np.dtype("uint32"):
        raise RuntimeError("Le noyau doit renvoyer un tableau uint32.")
    if labels.shape != mask.shape:
        raise RuntimeError("Dimensions des segments incorrectes.")
    if np.any(labels[~mask] != 0) or np.any(labels[mask] == 0):
        raise RuntimeError("Les segments ne respectent pas le masque.")

    ids, sizes = np.unique(labels[mask], return_counts=True)
    analyzed = int(np.count_nonzero(mask))
    if int(sizes.sum()) != analyzed:
        raise RuntimeError("Somme des surfaces en pixels incohérente.")
    # Contrôle supplémentaire du contrat de connexité du noyau.
    # label compare les identifiants, pas simplement le premier plan.
    from skimage.measure import label

    _, connected_count = label(labels, background=0, connectivity=1, return_num=True)
    if int(connected_count) != len(ids):
        raise RuntimeError("Un identifiant désigne plusieurs objets disjoints.")

    pixel_area = resolution * resolution
    area = analyzed * pixel_area
    estimate = area / config.target_segment_area_m2
    if not math.isfinite(area) or not math.isfinite(estimate):
        raise ValueError("Surface ou nombre de graines hors limites.")
    requested = max(1, min(analyzed, math.ceil(estimate)))
    if requested > MAX_REQUESTED_SEGMENTS:
        raise RuntimeError("Nombre de graines incohérent avec la limite du noyau.")
    areas = sizes.astype(np.float64) * pixel_area
    singles = int(np.count_nonzero(sizes == 1))
    objects = len(ids)
    return {
        "analysis_pixels": analyzed,
        "pixel_area_m2": pixel_area,
        "analysis_area_m2": area,
        "requested_segments": requested,
        "requested_segments_formula": "max(1, min(valid_pixels, ceil(area_m2 / target_m2)))",
        "objects": objects,
        "objects_per_requested_segment": objects / requested,
        "area_m2": {
            "min": float(areas.min()),
            "median": float(np.median(areas)),
            "mean": float(areas.mean()),
            "p90": float(np.percentile(areas, 90, method="linear")),
            "max": float(areas.max()),
        },
        "percentile_method": "linear",
        "single_pixel_objects": singles,
        "single_pixel_object_fraction": singles / objects,
        "single_pixel_area_m2": singles * pixel_area,
        "single_pixel_area_fraction": singles / analyzed,
        "largest_object_area_fraction": int(sizes.max()) / analyzed,
        "fraction_units": "proportion in [0, 1], not percent",
        "thresholds_applied": False,
    }


def _write_segments(path: Path, labels, grid: dict) -> None:
    driver = gdal.GetDriverByName("GTiff")
    if driver is None:
        raise RuntimeError("Pilote GTiff indisponible.")
    with _dataset(driver.Create(
        str(path), grid["width"], grid["height"], 1, gdal.GDT_UInt32,
        options=["TILED=YES", "COMPRESS=DEFLATE"],
    )) as dataset:
        _check(dataset.SetGeoTransform(grid["geotransform"]), "géotransformation")
        _check(dataset.SetProjection(grid["crs_wkt"]), "projection")
        band = dataset.GetRasterBand(1)
        _check(band.WriteArray(labels), "écriture des segments")
        band = None
        _check(dataset.FlushCache(), "vidage du cache")


def persist_segmentation(
    *,
    preparation_directory: Path,
    output_parent: Path,
    config: SlicConfig | None = None,
    control: SegmentationControl | None = None,
) -> dict[str, Any]:
    """Segmente une préparation complète et publie un nouveau dossier.

    Refuse un parent de sortie égal au dossier de préparation ou placé dedans.
    Ne crée pas le parent. Retourne exactement le manifeste JSON publié.
    En cas d'échec, supprime seulement le nouveau dossier de cette exécution.
    Un nettoyage impossible est une RuntimeError, chaînée à l'erreur initiale.
    control fournit des callbacks facultatifs de progression et d'annulation.
    Sans control, les appels existants conservent leur comportement.
    SegmentationCancelledError signale une annulation détectée à un checkpoint.
    Les callbacks s'exécutent dans le thread appelant ; leur erreur se propage.
    Les pourcentages indiquent des phases, pas une estimation du temps restant.
    SLIC, GDAL et le calcul des empreintes ne sont pas interrompus en cours.
    Une annulation après le dernier checkpoint peut arriver trop tard :
    le manifeste est alors publié et le résultat complet retourné.
    Aucun callback n'est exécuté après publication du manifeste.
    """
    if control is None:
        control = SegmentationControl()
    if not isinstance(control, SegmentationControl):
        raise ValueError("control doit être un SegmentationControl.")
    control.checkpoint(0)

    if config is None:
        config = SlicConfig()
    if not isinstance(config, SlicConfig):
        raise ValueError("config doit être une SlicConfig.")
    source = Path(preparation_directory).resolve(strict=True)
    parent = Path(output_parent).resolve(strict=True)
    if not source.is_dir() or not parent.is_dir():
        raise ValueError("La préparation et le parent doivent être des dossiers existants.")
    if parent == source or source in parent.parents:
        raise ValueError("Les sorties doivent être extérieures au dossier de préparation.")
    for name in _INPUT_NAMES:
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Fichier préparé absent ou lien symbolique refusé : {name}.")

    control.checkpoint(10)
    before = _fingerprints(source)
    control.checkpoint(20)
    rgb, mask, grid = _load_inputs(source)
    resolution = grid["geotransform"][1]
    control.checkpoint(25)
    labels = segment_rgb(rgb, mask, pixel_size_m=resolution, config=config)
    control.checkpoint(70)
    diagnostics = _diagnostics(labels, mask, resolution, config)
    control.checkpoint(75)
    if _fingerprints(source) != before:
        raise RuntimeError("Les entrées préparées ont changé pendant le calcul.")
    control.checkpoint(80)

    # Pas de dossier de sortie si les entrées ou le noyau sont refusés.
    run = Path(tempfile.mkdtemp(prefix="segmentation_", dir=str(parent)))
    try:
        control.checkpoint(85)
        raster_path = run / "segments.tif"
        _write_segments(raster_path, labels, grid)
        control.checkpoint(90)
        reread, reread_grid, masks, _ = _read_raster(
            raster_path, bands=1, data_type=gdal.GDT_UInt32,
        )
        _same_grid(reread_grid, grid)
        if not np.array_equal(reread, labels) or not np.all(masks[0]):
            raise RuntimeError("Les segments relus ou leur masque implicite sont incorrects.")
        if _diagnostics(reread, mask, resolution, config) != diagnostics:
            raise RuntimeError("Les diagnostics relus sont incohérents.")
        if {p.name for p in run.iterdir()} != {"segments.tif"}:
            raise RuntimeError("Fichiers compagnons inattendus après écriture/relecture.")
        if _fingerprints(source) != before:
            raise RuntimeError("Les entrées préparées ont changé avant publication.")
        control.checkpoint(95)

        import skimage

        report = {
            "schema_version": 1,
            "status": "complete",
            "scope": "unclassified_segments",
            "run_id": run.name,
            "output_directory": str(run),
            "preparation": {
                "directory": str(source),
                "sha256": before,
            },
            "grid": grid,
            "configuration": asdict(config),
            "algorithm": {
                "name": "masked_slic_then_connected_components",
                "enforce_connectivity": True,
                "sigma": 0,
                "convert2lab": True,
                "min_size_factor": 0.5,
                "max_size_factor": 3.0,
                "slic_zero": False,
                "start_label": 1,
                "channel_axis": -1,
                "final_connectivity": 4,
                "slic_called": diagnostics["requested_segments"] != 1,
                "single_seed_policy": "one_object_per_mask_component",
            },
            "versions": {
                "gdal": gdal.VersionInfo("RELEASE_NAME"),
                "numpy": np.__version__,
                "scikit_image": skimage.__version__,
            },
            "diagnostics": diagnostics,
            "label_semantics": {
                "outside_analysis_mask": 0,
                "inside_analysis_mask": "strictly_positive_object_id",
                "numeric_nodata": None,
                "semantic_classes": False,
            },
            "segments_sha256": _sha256(raster_path),
            "files": ["segments.tif", "segmentation.json"],
        }
        temporary = run / "segmentation.tmp"
        temporary.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        if _read_json(temporary) != report:
            raise RuntimeError("Le manifeste temporaire relu est incohérent.")
        control.checkpoint(99)
        temporary.replace(run / "segmentation.json")
        return report
    except BaseException as error:
        try:
            shutil.rmtree(run)
        except Exception as cleanup_error:
            raise RuntimeError(
                f"Segmentation échouée : {type(error).__name__}: {error} ; "
                f"nettoyage incomplet de {run} : {cleanup_error}"
            ) from error
        raise
