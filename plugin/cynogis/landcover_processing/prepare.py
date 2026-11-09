"""Préparation des entrées OBIA sur la grille native.

Dépendances : NumPy et osgeo.
Aucun import QGIS ou Qt.
Version initiale réservée aux petits extraits, sans rééchantillonnage.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from osgeo import gdal, ogr, osr

from ..core.landcover import PreparationConfig, validate_rgb_bands
from ..core.landcover_execution import PreparationControl


def _check(code, operation: str) -> None:
    """Contrôle les codes de retour des opérations GDAL/OGR."""
    if code not in (None, 0):
        raise RuntimeError(f"{operation} : code d'erreur {code}.")


@contextmanager
def _dataset(dataset):
    """Ferme explicitement le dataset, même en cas d'erreur."""
    if dataset is None:
        raise RuntimeError("Impossible de créer ou d'ouvrir le dataset GDAL.")
    try:
        yield dataset
    finally:
        _check(dataset.Close(), "Fermeture du dataset")


def _srs(wkt: str):
    if not isinstance(wkt, str) or not wkt.strip():
        raise ValueError("SCR absent.")

    result = osr.SpatialReference()
    _check(result.ImportFromWkt(wkt), "Lecture du SCR")
    result.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return result


def _json_number(value):
    """Représente explicitement une éventuelle métadonnée non finie."""
    if value is None or math.isfinite(value):
        return value
    return str(value)


def _read_source(path: Path, bands: list[int], config: PreparationConfig):
    if not path.is_file():
        raise ValueError("Le fichier raster local est introuvable.")

    # On exige le géoréférencement intégré au GeoTIFF.
    opened = gdal.OpenEx(
        str(path),
        gdal.OF_RASTER | gdal.OF_READONLY,
        allowed_drivers=["GTiff"],
        open_options=["GEOREF_SOURCES=INTERNAL"],
    )

    with _dataset(opened) as source:
        if source.RasterCount != 3:
            raise ValueError("Cette version exige exactement trois bandes.")

        selected = validate_rgb_bands(bands, source.RasterCount)
        width, height = source.RasterXSize, source.RasterYSize

        if width <= 0 or height <= 0 or width * height > config.max_pixels:
            raise ValueError("Dimensions invalides ou limite max_pixels dépassée.")

        transform = source.GetGeoTransform(can_return_null=True)
        if transform is None or not all(math.isfinite(v) for v in transform):
            raise ValueError("Géotransformation absente ou non finie.")

        if (
            transform[1] <= 0
            or transform[5] >= 0
            or transform[2] != 0
            or transform[4] != 0
        ):
            raise ValueError("La grille doit être orientée nord, sans rotation.")

        # Tolérance relative de 1e-9 sur la taille des pixels.
        if not math.isclose(
            transform[1], -transform[5], rel_tol=1e-9, abs_tol=0
        ):
            raise ValueError("Cette version exige des pixels carrés.")

        projection = source.GetProjectionRef()
        reference = _srs(projection)

        if not reference.IsProjected() or not math.isclose(
            reference.GetLinearUnits(), 1.0, rel_tol=0, abs_tol=1e-12
        ):
            raise ValueError("Le SCR doit être projeté et exprimé en mètres.")

        arrays = []
        validity = np.ones((height, width), dtype=bool)
        metadata = []

        for index in selected:
            band = source.GetRasterBand(index)
            if band.DataType != gdal.GDT_Byte:
                raise ValueError("Toutes les bandes sélectionnées doivent être Byte.")

            values = band.ReadAsArray()
            mask = band.GetMaskBand().ReadAsArray()

            if (
                values is None
                or mask is None
                or values.shape != (height, width)
                or mask.shape != (height, width)
            ):
                raise RuntimeError("Lecture incomplète d'une bande ou de son masque.")

            arrays.append(values)
            validity &= mask != 0
            metadata.append({
                "band": index,
                "color_interpretation": gdal.GetColorInterpretationName(
                    band.GetColorInterpretation()
                ),
                "nodata": _json_number(band.GetNoDataValue()),
                "mask_flags": band.GetMaskFlags(),
            })

        grid = {
            "width": width,
            "height": height,
            "geotransform": list(transform),
            "crs_wkt": projection,
        }
        return np.stack(arrays), validity, grid, metadata


def _aoi_mask(wkb: bytes, crs_wkt: str, grid: dict):
    reference = _srs(grid["crs_wkt"])
    aoi_reference = _srs(crs_wkt)

    if not reference.IsSame(aoi_reference):
        raise ValueError("Le périmètre et le raster doivent avoir le même SCR.")

    geometry = ogr.CreateGeometryFromWkb(wkb)
    if geometry is None:
        raise ValueError("WKB du périmètre illisible.")

    if geometry.GetGeometryName() not in {"POLYGON", "MULTIPOLYGON"}:
        raise ValueError("Un polygone ou multipolygone linéaire est nécessaire.")

    if geometry.IsEmpty() or not geometry.IsValid():
        raise ValueError("Le périmètre est vide ou invalide.")

    driver_name = (
        "MEM"
        if int(gdal.VersionInfo("VERSION_NUM")) >= 3_110_000
        else "Memory"
    )
    vector_driver = ogr.GetDriverByName(driver_name)

    if vector_driver is None:
        raise RuntimeError(
            f"Pilote vectoriel en mémoire indisponible : {driver_name}."
        )
    vector = vector_driver.CreateDataSource("")
    if vector is None:
        raise RuntimeError("Création du périmètre en mémoire impossible.")

    layer = None
    feature = None
    try:
        layer = vector.CreateLayer(
            "aoi",
            srs=reference,
            geom_type=geometry.GetGeometryType(),
        )
        if layer is None:
            raise RuntimeError("Création de la couche en mémoire impossible.")

        feature = ogr.Feature(layer.GetLayerDefn())
        _check(feature.SetGeometry(geometry), "Affectation du périmètre")
        _check(layer.CreateFeature(feature), "Création de l'entité")

        created = gdal.GetDriverByName("MEM").Create(
            "", grid["width"], grid["height"], 1, gdal.GDT_Byte
        )
        with _dataset(created) as target:
            _check(target.SetGeoTransform(grid["geotransform"]), "Grille du masque")
            _check(target.SetProjection(grid["crs_wkt"]), "SCR du masque")
            _check(target.GetRasterBand(1).Fill(0), "Initialisation du masque")

            _check(
                gdal.RasterizeLayer(
                    target,
                    [1],
                    layer,
                    burn_values=[1],
                    options=["ALL_TOUCHED=FALSE"],
                ),
                "Rasterisation du périmètre",
            )
            values = target.GetRasterBand(1).ReadAsArray()
            if values is None:
                raise RuntimeError("Lecture du masque de périmètre impossible.")
            return values != 0
    finally:
        feature = None
        layer = None
        vector = None


def _write_raster(path: Path, values, grid: dict, *, validity=None) -> None:
    arrays = values if values.ndim == 3 else values[np.newaxis, ...]
    count = arrays.shape[0]

    options = ["COMPRESS=DEFLATE", "TILED=YES"]
    if count == 3:
        options.append("PHOTOMETRIC=RGB")

    created = gdal.GetDriverByName("GTiff").Create(
        str(path),
        grid["width"],
        grid["height"],
        count,
        gdal.GDT_Byte,
        options=options,
    )

    with _dataset(created) as target:
        _check(target.SetGeoTransform(grid["geotransform"]), "Écriture de la grille")
        _check(target.SetProjection(grid["crs_wkt"]), "Écriture du SCR")

        colors = (gdal.GCI_RedBand, gdal.GCI_GreenBand, gdal.GCI_BlueBand)
        for index, array in enumerate(arrays, start=1):
            band = target.GetRasterBand(index)
            _check(band.WriteArray(array.astype(np.uint8)), "Écriture des pixels")
            if count == 3:
                _check(
                    band.SetColorInterpretation(colors[index - 1]),
                    "Interprétation RGB",
                )

        # Ne pas appeler SetNoDataValue : 0 et 255 restent des valeurs RGB.
        if validity is not None:
            _check(
                target.CreateMaskBand(gdal.GMF_PER_DATASET),
                "Création du masque commun",
            )
            mask = validity.astype(np.uint8) * 255
            _check(
                target.GetRasterBand(1).GetMaskBand().WriteArray(mask),
                "Écriture du masque commun",
            )

        _check(target.FlushCache(), "Vidage des écritures")


def _verify_raster(path: Path, expected, grid: dict, *, validity=None) -> None:
    arrays = expected if expected.ndim == 3 else expected[np.newaxis, ...]

    with _dataset(gdal.OpenEx(str(path), gdal.OF_RASTER | gdal.OF_READONLY)) as ds:
        if (
            ds.RasterXSize != grid["width"]
            or ds.RasterYSize != grid["height"]
            or ds.RasterCount != len(arrays)
            or tuple(ds.GetGeoTransform()) != tuple(grid["geotransform"])
            or not _srs(ds.GetProjectionRef()).IsSame(_srs(grid["crs_wkt"]))
        ):
            raise RuntimeError(f"Grille de sortie incorrecte : {path.name}.")

        colors = (gdal.GCI_RedBand, gdal.GCI_GreenBand, gdal.GCI_BlueBand)
        for index, array in enumerate(arrays, start=1):
            band = ds.GetRasterBand(index)

            if band.DataType != gdal.GDT_Byte or band.GetNoDataValue() is not None:
                raise RuntimeError(f"Type ou NoData incorrect : {path.name}.")

            if not np.array_equal(band.ReadAsArray(), array):
                raise RuntimeError(f"Valeurs modifiées : {path.name}.")

            mask = band.GetMaskBand().ReadAsArray()
            if mask is None:
                raise RuntimeError(f"Masque illisible : {path.name}.")

            if validity is None:
                if not np.all(mask != 0):
                    raise RuntimeError(f"Masque binaire mal interprété : {path.name}.")
            else:
                if not band.GetMaskFlags() & gdal.GMF_PER_DATASET:
                    raise RuntimeError("Le masque RGB doit être commun aux bandes.")
                if not np.array_equal(mask != 0, validity):
                    raise RuntimeError("Masque RGB différent de validity_mask.")
                if band.GetColorInterpretation() != colors[index - 1]:
                    raise RuntimeError("Interprétation RGB incorrecte.")


def prepare_native_inputs(
    *,
    raster_path: Path,
    aoi_wkb: bytes,
    aoi_crs_wkt: str,
    rgb_bands: list[int],
    output_parent: Path,
    config: PreparationConfig,
    control: PreparationControl | None = None,
) -> dict:
    """Prépare un petit extrait sans modifier ses valeurs ni sa grille.

    Aucun objet QGIS n'est accepté ou manipulé.
    Le dossier parent doit déjà exister.

    control permet de transmettre des notifications de progression et de
    détecter une annulation entre les phases. Les callbacks s'exécutent
    dans le thread appelant ; ils ne doivent pas manipuler l'interface.

    Une annulation détectée lève PreparationCancelledError. Si un dossier
    d'exécution a été créé, son nettoyage est tenté avant propagation.
    Un échec du nettoyage lève RuntimeError, avec l'exception initiale
    conservée comme cause.

    L'annulation est coopérative : elle n'interrompt pas un appel GDAL
    déjà en cours.

    Le dernier contrôle intervient avant publication du manifeste.
    Une demande reçue après ce contrôle peut arriver trop tard pour
    empêcher le retour d'un résultat complet. L'adaptateur de job devra
    gérer cette annulation tardive avant de publier le résultat à l'utilisateur.

    Aucun callback n'est appelé après publication du manifeste.
    """

    if control is None:
        control = PreparationControl()
    elif not isinstance(control, PreparationControl):
        raise ValueError("control doit être une PreparationControl.")

    control.checkpoint(0)

    if not isinstance(config, PreparationConfig):
        raise ValueError("Une PreparationConfig est nécessaire.")

    raster_path = Path(raster_path).resolve()
    output_parent = Path(output_parent).resolve()

    if not output_parent.is_dir():
        raise ValueError("Le dossier parent de sortie doit déjà exister.")

    rgb, validity, grid, band_metadata = _read_source(
        raster_path, rgb_bands, config
    )
    control.checkpoint(20)
    aoi = _aoi_mask(aoi_wkb, aoi_crs_wkt, grid)
    control.checkpoint(30)

    if not np.any(aoi):
        raise ValueError("Le périmètre ne sélectionne aucun pixel.")

    analysis = aoi & validity
    if not np.any(analysis):
        raise ValueError("Le périmètre ne contient aucun pixel analysable.")

    counts = {
        "total_pixels": int(validity.size),
        "aoi_pixels": int(np.count_nonzero(aoi)),
        "valid_pixels_whole_raster": int(np.count_nonzero(validity)),
        "invalid_pixels_whole_raster": int(np.count_nonzero(~validity)),
        "analysis_pixels": int(np.count_nonzero(analysis)),
        "invalid_pixels_inside_aoi": int(np.count_nonzero(aoi & ~validity)),
        "valid_pixels_outside_aoi": int(np.count_nonzero(validity & ~aoi)),
    }

    if (
        counts["aoi_pixels"]
        != counts["analysis_pixels"] + counts["invalid_pixels_inside_aoi"]
        or counts["total_pixels"]
        != counts["valid_pixels_whole_raster"] + counts["invalid_pixels_whole_raster"]
    ):
        raise RuntimeError("Comptages incohérents.")

    control.checkpoint(35)

    run = Path(tempfile.mkdtemp(prefix="obia_", dir=output_parent))

    try:
        products = {
            "image_rgb.tif": rgb,
            "aoi_mask.tif": aoi.astype(np.uint8),
            "validity_mask.tif": validity.astype(np.uint8),
            "analysis_mask.tif": analysis.astype(np.uint8),
        }

        for index, (name, values) in enumerate(products.items()):
            control.checkpoint(40 + 10 * index)
            _write_raster(
                run / name,
                values,
                grid,
                validity=validity if name == "image_rgb.tif" else None,
            )


        for index, (name, values) in enumerate(products.items()):
            control.checkpoint(80 + 4 * index)
            _verify_raster(
                run / name,
                values,
                grid,
                validity=validity if name == "image_rgb.tif" else None,
            )

        control.checkpoint(97)

        files = sorted(
            str(path.relative_to(run))
            for path in run.rglob("*")
            if path.is_file()
        )

        report = {
            "schema_version": 1,
            "status": "complete",
            "run_id": run.name,
            "output_directory": str(run),
            "source": {
                "path": str(raster_path),
                "rgb_bands": list(rgb_bands),
                "bands": band_metadata,
                "georeferencing": "internal_geotiff",
            },
            "configuration": config.to_dict(),
            "grid": grid,
            "aoi": {
                "wkb_sha256": hashlib.sha256(aoi_wkb).hexdigest(),
                "crs_wkt": aoi_crs_wkt,
                "rasterization": "GDAL standard, ALL_TOUCHED=FALSE",
            },
            "versions": {
                "gdal": gdal.VersionInfo("RELEASE_NAME"),
                "numpy": np.__version__,
            },
            "counts": counts,
            "mask_semantics": {
                "binary_masks": "0=false, 1=true; no numeric NoData",
                "image_rgb_mask": "validity_mask",
                "processing_mask": "analysis_mask = aoi_mask AND validity_mask",
            },
            "files": sorted([*files, "preparation.json"]),
        }

        temporary = run / "preparation.tmp"
        temporary.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False),
            encoding="utf-8",
        )

        control.checkpoint(99)

        temporary.replace(run / "preparation.json")
        return report

    except BaseException as error:
        try:
            shutil.rmtree(run)
        except OSError as cleanup_error:
            raise RuntimeError(
                f"Préparation échouée ; nettoyage incomplet de {run} : "
                f"{cleanup_error}"
            ) from error
        raise
