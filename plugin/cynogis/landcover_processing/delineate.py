"""Délimitation OBIA : fusion des objets puis unités vectorielles, schéma 1.

API synchrone, sans QGIS ni MCP ; ne pas importer depuis __init__.py.
Entrées : préparation, segmentation et caractéristiques complètes, identifiées par
contenu (SHA-256). Sortie : nouveau dossier delineation_* contenant regions.tif
(identifiant d'unité par pixel, 0 hors masque), delineation.gpkg (un polygone par
unité, limites en marches d'escalier sur la grille, non simplifiées) et
delineation.json, publié en dernier comme marqueur de succès.

Les unités sont des zones homogènes en couleur, pas des classes d'occupation du sol.
Surface : comptage de pixels fois surface d'un pixel, dans le SCR projeté de la grille
(surface plane projetée 2D) ; égale à l'aire des polygones produits.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..core.landcover import DelineationConfig
from ..core.landcover_execution import DelineationControl
from .merge import merge_segments
from .persist_features import _directory, _schema
from .persist_features import _snapshot as _source_snapshot

_FEATURE_FILES = ("objects.npy", "edges.npy", "features.json")
LAYER_NAME = "units"


def _snapshot(prep: Path, seg: Path, feat: Path) -> dict:
    from . import persist as io

    return {
        "sources": _source_snapshot(prep, seg),
        "features": {name: io._sha256(feat / name) for name in _FEATURE_FILES},
    }


def _load_features(feat: Path, before: dict):
    import numpy as np

    from . import persist as io

    manifest = io._read_json(feat / "features.json")
    version = manifest.get("schema_version")
    if (type(version) is not int or version != 1 or manifest.get("status") != "complete"
            or manifest.get("scope") != "unclassified_object_features"):
        raise ValueError("Manifeste des caractéristiques incomplet ou incompatible.")
    if manifest.get("inputs_sha256") != before["sources"]:
        raise ValueError("Les caractéristiques ne proviennent pas de ces sources.")
    tables = manifest.get("tables")
    if not isinstance(tables, dict):
        raise ValueError("Tables absentes du manifeste des caractéristiques.")
    arrays = []
    for key, dtype in zip(("objects", "edges"), _schema(), strict=True):
        name = f"{key}.npy"
        entry = tables.get(key)
        if not isinstance(entry, dict) or entry.get("sha256") != before["features"][name]:
            raise ValueError(f"L'empreinte de {name} diffère du manifeste.")
        with (feat / name).open("rb") as stream:
            array = np.load(stream, allow_pickle=False)
        if array.ndim != 1 or array.dtype != dtype:
            raise ValueError(f"Schéma de {name} incorrect.")
        arrays.append(array)
    return manifest, arrays[0], arrays[1]


def _write_units(path: Path, regions, grid: dict, stats: dict) -> int:
    """Vectorise regions dans un GeoPackage neuf ; renvoie le nombre de polygones."""
    from osgeo import gdal, ogr, osr

    from . import persist as io

    reference = osr.SpatialReference()
    io._check(reference.ImportFromWkt(grid["crs_wkt"]), "lecture du SCR")
    reference.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    memory = gdal.GetDriverByName("MEM")
    vector = gdal.GetDriverByName("GPKG")
    if memory is None or vector is None:
        raise RuntimeError("Pilote MEM ou GPKG indisponible.")
    with io._dataset(memory.Create("", grid["width"], grid["height"], 1,
                                   gdal.GDT_UInt32)) as raster, \
            io._dataset(vector.Create(str(path), 0, 0, 0, gdal.GDT_Unknown)) as output:
        io._check(raster.SetGeoTransform(grid["geotransform"]), "géotransformation")
        io._check(raster.SetProjection(grid["crs_wkt"]), "projection")
        band = raster.GetRasterBand(1)
        io._check(band.WriteArray(regions), "écriture des unités")

        layer = output.CreateLayer(LAYER_NAME, reference, ogr.wkbPolygon)
        if layer is None:
            raise RuntimeError("Création de la couche des unités impossible.")
        for name, kind in (("unit_id", ogr.OFTInteger64), ("pixel_count", ogr.OFTInteger64),
                           ("area_plan_m2", ogr.OFTReal), ("segment_count", ogr.OFTInteger),
                           ("red_mean", ogr.OFTReal), ("green_mean", ogr.OFTReal),
                           ("blue_mean", ogr.OFTReal)):
            io._check(layer.CreateField(ogr.FieldDefn(name, kind)), f"champ {name}")
        # La bande sert de masque : 0 (hors analyse) n'est pas vectorisé ; 4 voisins.
        io._check(gdal.Polygonize(band, band, layer, 0, [], callback=None), "vectorisation")
        band = None

        layer.ResetReading()
        fids = [feature.GetFID() for feature in layer]
        io._check(layer.StartTransaction(), "début de transaction")
        polygons = 0
        for fid in fids:
            feature = layer.GetFeature(fid)
            unit = feature.GetFieldAsInteger64("unit_id")
            pixel_count, area, segments, mean = stats[unit]
            feature.SetField("pixel_count", pixel_count)
            feature.SetField("area_plan_m2", area)
            feature.SetField("segment_count", segments)
            for name, value in zip(("red_mean", "green_mean", "blue_mean"), mean, strict=True):
                feature.SetField(name, value)
            io._check(layer.SetFeature(feature), "mise à jour d'une unité")
            polygons += 1
        io._check(layer.CommitTransaction(), "fin de transaction")
        layer = None
    return polygons


def persist_delineation(
    *, preparation_directory: Path, segmentation_directory: Path,
    features_directory: Path, output_parent: Path,
    config: DelineationConfig | None = None, control: DelineationControl | None = None,
) -> dict[str, Any]:
    """Fusionne les objets et publie les unités dans un nouveau dossier delineation_*.

    Les trois sources doivent être distinctes et complètes (schéma 1) ; le parent de
    sortie existe et n'est dans aucune d'elles. En cas d'échec, seul le dossier créé
    est supprimé. Annulation coopérative aux checkpoints (DelineationCancelledError) ;
    aucun callback après publication de delineation.json.
    """
    if control is None:
        control = DelineationControl()
    if not isinstance(control, DelineationControl):
        raise ValueError("control doit être un DelineationControl.")
    control.checkpoint(0)
    if config is None:
        config = DelineationConfig()
    if not isinstance(config, DelineationConfig):
        raise ValueError("config doit être une DelineationConfig.")

    import numpy as np
    from osgeo import gdal

    from . import persist as io

    prep = _directory(preparation_directory)
    seg = _directory(segmentation_directory)
    feat = _directory(features_directory)
    parent = _directory(output_parent)
    sources = (prep, seg, feat)
    if len(set(sources)) != 3 or any(parent.is_relative_to(src) for src in sources):
        raise ValueError("Sources distinctes requises ; sortie interdite dans les sources.")

    control.checkpoint(10)
    before = _snapshot(prep, seg, feat)
    manifest, objects, edges = _load_features(feat, before)
    labels, grid, label_masks, _ = io._read_raster(
        seg / "segments.tif", bands=1, data_type=gdal.GDT_UInt32,
    )
    io._same_grid(grid, manifest["grid"])
    resolution = float(grid["geotransform"][1])
    if manifest.get("pixel_size_m") != resolution:
        raise ValueError("Résolution des caractéristiques incohérente avec la grille.")
    mask = labels > 0
    if not np.all(label_masks[0]):
        raise ValueError("Masque implicite inattendu sur segments.tif.")
    ids = objects["segment_id"]
    if not np.array_equal(np.unique(labels[mask]), ids):
        raise ValueError("Les objets des caractéristiques ne correspondent pas aux labels.")
    control.checkpoint(30)

    pixel_area = resolution * resolution
    merged = merge_segments(
        objects, edges, pixel_area_m2=pixel_area,
        color_distance_max=float(config.color_distance_max),
        min_mapping_area_m2=float(config.min_mapping_area_m2),
    )
    roots = np.asarray(merged.roots, dtype=np.uint32)
    unique_roots, unit_index = np.unique(roots, return_inverse=True)
    unit_of_object = (unit_index.reshape(-1) + 1).astype(np.uint32)  # unités 1..U
    regions = np.zeros(labels.shape, dtype=np.uint32)
    regions[mask] = unit_of_object[np.searchsorted(ids, labels[mask])]
    units = len(unique_roots)

    weights = objects["pixel_count"].astype("f8")
    counts = np.bincount(unit_of_object, weights=weights, minlength=units + 1)
    segments = np.bincount(unit_of_object, minlength=units + 1)
    means = np.stack([
        np.bincount(unit_of_object, weights=objects["rgb_mean"][:, c] * weights,
                    minlength=units + 1)[1:] / counts[1:]
        for c in range(3)
    ], axis=1)
    stats = {
        unit: (int(counts[unit]), float(counts[unit] * pixel_area), int(segments[unit]),
               [float(v) for v in means[unit - 1]])
        for unit in range(1, units + 1)
    }
    areas = np.array([value[1] for value in stats.values()])
    control.checkpoint(60)

    run = Path(tempfile.mkdtemp(prefix="delineation_", dir=parent))
    try:
        raster_path = run / "regions.tif"
        io._write_segments(raster_path, regions, grid)
        reread, reread_grid, masks, _ = io._read_raster(
            raster_path, bands=1, data_type=gdal.GDT_UInt32)
        io._same_grid(reread_grid, grid)
        if not np.array_equal(reread, regions) or not np.all(masks[0]):
            raise RuntimeError("Les unités relues sont incorrectes.")
        control.checkpoint(75)

        vector_path = run / "delineation.gpkg"
        polygons = _write_units(vector_path, regions, grid, stats)
        if polygons != units:
            raise RuntimeError(
                f"{polygons} polygones pour {units} unités : une unité n'est pas d'un seul tenant.")
        control.checkpoint(90)

        report = {
            "schema_version": 1, "scope": "unclassified_delineation", "status": "complete",
            "run_id": run.name, "output_directory": str(run),
            "inputs_sha256": before, "configuration": asdict(config), "grid": grid,
            "pixel_size_m": resolution, "layer_name": LAYER_NAME,
            "versions": {"numpy": np.__version__, "gdal": gdal.VersionInfo("RELEASE_NAME")},
            "diagnostics": {
                "input_objects": len(ids), "units": units,
                "merged_by_similarity": merged.merged_by_similarity,
                "merged_by_area": merged.merged_by_area,
                "isolated_small_units": merged.isolated_small_units,
                "analysis_area_m2": float(mask.sum() * pixel_area),
                "unit_area_m2": {"min": float(areas.min()), "median": float(np.median(areas)),
                                 "max": float(areas.max())},
            },
            "area_method": "plane, surface projetée 2D dans le SCR de la grille "
                           "(pixels fois surface d'un pixel)",
            "regions_sha256": io._sha256(raster_path),
            "delineation_sha256": io._sha256(vector_path),
            "files": ["regions.tif", "delineation.gpkg", "delineation.json"],
        }
        tmp = run / "delineation.tmp"
        tmp.write_text(json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + "\n",
                       encoding="utf-8")
        if io._read_json(tmp) != report:
            raise RuntimeError("Le manifeste de délimitation n'est pas relu à l'identique.")
        if _snapshot(prep, seg, feat) != before:
            raise RuntimeError("Les sources ont changé pendant la délimitation.")
        control.checkpoint(99)
        tmp.replace(run / "delineation.json")
        return report
    except BaseException as original:
        try:
            shutil.rmtree(run)
        except Exception as cleanup:
            raise RuntimeError(
                f"{original} ; nettoyage incomplet de {run} : {cleanup}"
            ) from original
        raise
