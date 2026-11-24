"""Persistance des caractéristiques des segments OBIA, schéma 1.

Fichier : plugin/cynogis/landcover_processing/persist_features.py
API synchrone, sans QGIS, jobs, MCP, classification ni fusion. Ne pas importer
ce module depuis __init__.py. Les chemins historiques des manifestes ne sont
jamais suivis. La politique de destination d'un futur outil relève de l'appelant.
Les SHA-256 détectent les différences de contenu ; ils ne constituent ni une
signature, ni un instantané atomique. features.json est le marqueur de succès ;
le renommage final n'est pas une garantie de durabilité après panne électrique.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .object_features import extract_object_features


def _directory(path: Path) -> Path:
    if not isinstance(path, Path) or not path.is_absolute():
        raise ValueError("Un chemin Path absolu est requis.")
    resolved = path.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError(f"Dossier attendu : {resolved}")
    return resolved


def _snapshot(prep: Path, seg: Path) -> dict:
    # Helpers internes partagés avec la persistance de segmentation (schéma 1).
    from . import persist as io

    return {
        "preparation": io._fingerprints(prep),
        "segmentation": {
            name: io._sha256(seg / name) for name in ("segments.tif", "segmentation.json")
        },
    }


def _schema():
    import numpy as np

    return (
        np.dtype([
            ("segment_id", "u4"), ("pixel_count", "i8"), ("area_m2", "f8"),
            ("center_row", "f8"), ("center_col", "f8"), ("row_min", "i8"),
            ("row_max_exclusive", "i8"), ("col_min", "i8"), ("col_max_exclusive", "i8"),
            ("rgb_mean", "f8", (3,)), ("rgb_std", "f8", (3,)),
        ]),
        np.dtype([
            ("segment_a", "u4"), ("segment_b", "u4"),
            ("shared_pixel_sides", "i8"), ("shared_boundary_m", "f8"),
        ]),
    )


def _check_tables(objects, edges, labels, mask, resolution: float) -> None:
    import numpy as np

    for array, expected in zip((objects, edges), _schema(), strict=True):
        if not isinstance(array, np.ndarray) or array.ndim != 1 or array.dtype != expected:
            raise RuntimeError("Schéma de table de caractéristiques incorrect.")
    ids, counts = np.unique(labels[mask], return_counts=True)
    if not np.array_equal(objects['segment_id'], ids):
        raise RuntimeError("Identifiants des objets incompatibles avec les labels.")
    if not np.array_equal(objects['pixel_count'], counts):
        raise RuntimeError("Comptages par objet incompatibles avec le masque.")
    if not np.array_equal(objects['area_m2'], counts.astype('f8') * (resolution * resolution)):
        raise RuntimeError("Surfaces par objet incohérentes.")
    for key in ('rgb_mean', 'rgb_std', 'center_row', 'center_col', 'area_m2'):
        if not np.isfinite(objects[key]).all():
            raise RuntimeError(f"Valeur non finie : {key}.")
    for axis, limit in zip(('row', 'col'), mask.shape, strict=True):
        lo, hi = objects[f'{axis}_min'], objects[f'{axis}_max_exclusive']
        center = objects[f'center_{axis}']
        if not np.all((lo >= 0) &(lo < hi) & (hi <= limit)
                      & (lo + 0.5 <= center) & (center <= hi - 0.5)):
            raise RuntimeError(f"Emprise ou centre invalide : {axis}.")
    a, b = edges['segment_a'], edges['segment_b']
    if not (np.all(a < b) and np.isin(a, ids).all() and np.isin(b, ids).all()):
        raise RuntimeError("Arête en boucle ou objet inconnu.")
    if not np.all((a[1:] > a[:-1]) | ((a[1:] == a[:-1]) & (b[1:] > b[:-1]))):
        raise RuntimeError("Arêtes non triées ou dupliquées.")
    sides = edges['shared_pixel_sides']
    if not (np.all(sides > 0) and np.array_equal(edges['shared_boundary_m'], sides * resolution)):
        raise RuntimeError("Longueur de contact incohérente.")


def _save_table(path: Path, array) -> dict:
    import numpy as np

    from .persist import _sha256

    with path.open('xb') as stream:
        np.save(stream, array, allow_pickle=False)
    with path.open('rb') as stream:
        actual = np.load(stream, allow_pickle=False)
        if (actual.shape != array.shape or actual.dtype != array.dtype
            or not np.array_equal(actual, array) or stream.read(1)):
            raise RuntimeError(f"Table altérée à la relecture : {path.name}.")
    fields = []
    for name in array.dtype.names:
        dtype = array.dtype.fields[name][0]
        fields.append({'name': name, 'dtype': dtype.base.str, 'shape': list(dtype.shape)})
    return {'file': path.name, 'rows': len(array), 'fields': fields, 'sha256': _sha256(path)}


def persist_object_features(
    *, preparation_directory: Path, segmentation_directory: Path, output_parent: Path,
) -> dict[str, Any]:
    """Écrit objects.npy, edges.npy et features.json dans un nouveau features_*.

    Les deux sources doivent être des produits Cynogis complets de schéma 1.
    Leurs cinq + deux fichiers sont identifiés par contenu. Une préparation de
    même grille mais produite par une autre exécution n'est pas interchangeable.
    Aucun parcours de chemin ni nom de fichier n'est dicté par les manifestes.
    """
    import numpy as np
    from osgeo import gdal

    from . import persist as io

    prep = _directory(preparation_directory)
    seg = _directory(segmentation_directory)
    parent = _directory(output_parent)
    if prep == seg or any(parent.is_relative_to(src) for src in (prep, seg)):
        raise ValueError("Sources distinctes requises ; sortie interdite dans les sources.")

    before = _snapshot(prep, seg)
    manifest = io._read_json(seg / 'segmentation.json')
    version = manifest.get('schema_version')
    if (type(version) is not int or version != 1 or manifest.get('status') != 'complete'
        or manifest.get('scope') != 'unclassified_segments'):
        raise ValueError("Manifeste de segmentation incomplet ou incompatible.")
    provenance = manifest.get('preparation')
    if not isinstance(provenance, dict) or provenance.get('sha256') != before['preparation']:
        raise ValueError("La préparation fournie ne correspond pas à cette segmentation.")
    if manifest.get('segments_sha256') != before['segmentation']['segments.tif']:
        raise ValueError("L'empreinte de segments.tif diffère du manifeste.")
    if not isinstance(manifest.get('grid'), dict):
        raise ValueError("Grille de segmentation absente.")

    rgb, mask, grid = io._load_inputs(prep)
    labels, label_grid, label_masks, _ = io._read_raster(
        seg / 'segments.tif', bands=1, data_type=gdal.GDT_UInt32,
    )
    io._same_grid(label_grid, grid)
    io._same_grid(label_grid, manifest['grid'])
    if not np.all(label_masks[0]) or not np.array_equal(labels > 0, mask):
        raise ValueError("Les labels ou le masque implicite ne respectent pas analysis_mask.")
    resolution = float(grid['geotransform'][1])
    tables = extract_object_features(rgb, labels, mask, pixel_size_m=resolution)
    _check_tables(tables.objects, tables.edges, labels, mask, resolution)

    run = Path(tempfile.mkdtemp(prefix='features_', dir=parent))
    try:
        objects = _save_table(run / 'objects.npy', tables.objects)
        edges = _save_table(run / 'edges.npy', tables.edges)
        report = {
            'schema_version': 1, 'scope': 'unclassified_object_features', 'status': 'complete',
            'run_id': run.name, 'output_directory': str(run),
            'inputs_sha256': before, 'grid': grid, 'pixel_size_m': resolution,
            'versions': {'numpy': np.__version__, 'gdal': gdal.VersionInfo('RELEASE_NAME')},
            'tables': {'objects': objects, 'edges': edges},
            'diagnostics': {
                'analysis_pixels': int(mask.sum()), 'object_count': objects['rows'],
                'edge_count': edges['rows'],
                'shared_pixel_sides_total': int(tables.edges['shared_pixel_sides'].sum()),
            },
            'conventions': {
                'segment_id': 'original label; zero excluded', 'pixel_count': 'pixels',
                'area_m2': 'square metres', 'centers': 'grid row/column; first center at 0.5',
                'bounds': 'zero-based grid indices, upper bounds exclusive',
                'rgb_mean': 'RGB order, intensity units 0..255',
                'rgb_std': 'population standard deviation in intensity units, ddof=0',
                'edges': 'ordered undirected pairs; four-neighbour contact; no background',
                'shared_pixel_sides': 'count of shared pixel sides, each counted once',
                'shared_boundary_m': 'metres; not the full object perimeter',
            },
            'files': ['objects.npy', 'edges.npy', 'features.json'],
        }
        tmp = run / 'features.tmp'
        tmp.write_text(json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + '\n',
                       encoding='utf-8')
        if io._read_json(tmp) != report:
            raise RuntimeError("Le manifeste des caractéristiques n'est pas relu à l'identique.")
        if _snapshot(prep, seg) != before:
            raise RuntimeError("Les sources ont changé pendant l'extraction des caractéristiques.")
        tmp.replace(run / 'features.json')
        return report
    except BaseException as original:
        try:
            shutil.rmtree(run)
        except Exception as cleanup:
            raise RuntimeError(
                f"{original} ; nettoyage incomplet de {run} : {cleanup}"
            ) from original
        raise
