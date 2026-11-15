"""Outils de préparation de la délimitation OBIA."""

from __future__ import annotations

import math
from pathlib import Path
from typing import NoReturn

from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProject,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.jobs import PrepareLandcover, Steps
from ..core.landcover import PreparationConfig, validate_rgb_bands
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    clean_number,
    crs_info,
    get_raster_layer,
    get_vector_layer,
    source_path,
)

# Garde-fou pour cette inspection synchrone.
# Les géométries plus complexes seront prises en charge par un job dédié.
MAX_INSPECTION_VERTICES = 50_000

def _reject(message: str) -> NoReturn:
    raise ToolError(ErrorCode.INVALID_PARAMS, message)

def _read_aoi_geometry(layer, feature_id: int) -> QgsGeometry:
    """Lit et contrôle une copie du périmètre, sans modifier la couche."""
    request = QgsFeatureRequest().setFilterFid(feature_id)
    request.setNoAttributes()

    feature = next(layer.getFeatures(request), None)
    if feature is None:
        _reject(f"Entité {feature_id} introuvable dans {layer.name()}.")

    geometry = QgsGeometry(feature.geometry())

    if geometry.isNull() or geometry.isEmpty():
        _reject("Le périmètre possède une géométrie vide.")

    if geometry.type() != Qgis.GeometryType.Polygon:
        _reject("Le périmètre doit être un polygone ou un multipolygone.")

    # Arrêt anticipé sans matérialiser tous les sommets en mémoire.
    for count, _vertex in enumerate(geometry.vertices(), start=1):
        if count > MAX_INSPECTION_VERTICES:
            _reject(
                "Périmètre trop complexe pour cette inspection synchrone : "
                f"plus de {MAX_INSPECTION_VERTICES} sommets."
            )

    if not geometry.isGeosValid():
        _reject(
            "Le périmètre possède une géométrie invalide. "
            "La corriger séparément avant de poursuivre."
        )

    return geometry

@tool(level=Level.READ, params={
    "raster_layer_id": Param(
        "string",
        "Identifiant de l'orthophoto GeoTIFF locale chargée dans QGIS.",
    ),
    "aoi_layer_id": Param(
        "string",
        "Identifiant de la couche polygonale du périmètre.",
    ),
    "aoi_feature_id": Param(
        "integer",
        "Identifiant QGIS de l'entité à analyser, pas un attribut métier.",
    ),
    "rgb_bands": Param(
        "array",
        "Trois indices de bandes dans l'ordre rouge, vert, bleu, à partir de 1.",
        items="integer",
    ),
})
def inspect_landcover_inputs(
    raster_layer_id: str,
    aoi_layer_id: str,
    aoi_feature_id: int,
    rgb_bands: list[int],
) -> ToolResult:
    """Inspecte les entrées OBIA sans modifier le projet ni créer de fichiers.

    Version initiale : GeoTIFF local et une entité polygonale.
    Vérifie les métadonnées, les bandes, le périmètre et son intersection
    avec le rectangle d'emprise du raster. Ne lit pas les pixels et ne
    garantit ni leur validité, ni le contenu spectral des bandes.
    """
    raster = get_raster_layer(raster_layer_id)
    aoi = get_vector_layer(aoi_layer_id)

    for layer in (raster, aoi):
        if not layer.isValid():
            _reject(f"Couche invalide : {layer.name()}.")
        if not layer.crs().isValid():
            _reject(f"SCR absent ou invalide : {layer.name()}.")

    if aoi.geometryType() != Qgis.GeometryType.Polygon:
        _reject("La couche du périmètre doit être polygonale.")

    if raster.providerType() != "gdal":
        _reject("Cette version nécessite un raster local lu par GDAL.")

    path_text = source_path(raster)
    if not path_text:
        _reject("Impossible d'identifier le fichier local de l'orthophoto.")

    path = Path(path_text)
    if path.suffix.lower() not in {".tif", ".tiff"}:
        _reject("Cette première version accepte uniquement les fichiers TIFF.")

    if not path.is_file():
        _reject("Le fichier TIFF n'est pas accessible sur cette machine.")

    if raster.width() <= 0 or raster.height() <= 0:
        _reject("Les dimensions du raster sont invalides.")

    try:
        bands = validate_rgb_bands(rgb_bands, raster.bandCount())
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc

    pixel_x = abs(raster.rasterUnitsPerPixelX())
    pixel_y = abs(raster.rasterUnitsPerPixelY())
    if not all(math.isfinite(v) and v > 0 for v in (pixel_x, pixel_y)):
        _reject("La taille des pixels du raster est invalide.")

    geometry = _read_aoi_geometry(aoi, aoi_feature_id)

    # On transforme une copie, jamais la géométrie stockée dans la couche.
    if aoi.crs() != raster.crs():
        transform = QgsCoordinateTransform(
            aoi.crs(),
            raster.crs(),
            QgsProject.instance(),
        )
        try:
            status = geometry.transform(transform)
        except QgsCsException as exc:
            raise ToolError(
                ErrorCode.INVALID_PARAMS,
                "Impossible de transformer le périmètre vers le SCR du raster.",
            ) from exc

        if status != Qgis.GeometryOperationResult.Success:
            _reject("La transformation du périmètre a échoué.")

    if (
        geometry.isNull()
        or geometry.isEmpty()
        or not geometry.isGeosValid()
    ):
        _reject("Le périmètre est invalide après transformation.")

    raster_extent = raster.extent()
    if raster_extent.isEmpty():
        _reject("L'emprise du raster est vide.")

    footprint = QgsGeometry.fromRect(raster_extent)
    overlap = geometry.intersection(footprint)

    if overlap.lastError():
        _reject(f"Échec du contrôle de recouvrement : {overlap.lastError()}")

    if overlap.isNull() or overlap.isEmpty() or overlap.area() <= 0:
        _reject("Le périmètre ne recouvre pas l'emprise du raster en surface.")

    outside = geometry.difference(footprint)
    if outside.lastError():
        _reject(f"Échec du contrôle de couverture : {outside.lastError()}")

    extends_outside = not outside.isEmpty()
    metric_crs = (
        not raster.crs().isGeographic()
        and raster.crs().mapUnits() == Qgis.DistanceUnit.Meters
    )

    warnings = [
        "Le masque des pixels valides, les zones NoData internes et le canal "
        "alpha n'ont pas été analysés.",
        "L'ordre RGB est déclaré par l'utilisateur, pas reconnu automatiquement.",
        "Un SCR déclaré ne garantit pas l'exactitude du géoréférencement.",
    ]



    if extends_outside:
        warnings.append(
            "Une partie du périmètre dépasse le rectangle d'emprise du raster."
        )
    if not metric_crs:
        warnings.append(
            "Une grille de travail dans un SCR projeté métrique sera nécessaire."
        )
    if aoi.isEditable():
        warnings.append(
            "Le périmètre est en mode édition : l'inspection utilise son état courant."
        )

    provider = raster.dataProvider()

    return ToolResult({
        "inspection_passed": True,
        "scope": "metadata_and_geometry_only",
        "raster": {
            "layer_id": raster.id(),
            "name": raster.name(),
            "crs": crs_info(raster.crs()),
            "width": raster.width(),
            "height": raster.height(),
            "band_count": raster.bandCount(),
            "pixel_size_crs_units": [pixel_x, pixel_y],
            "pixel_size_m": [pixel_x, pixel_y] if metric_crs else None,
            "rgb_bands": list(bands),
            "selected_bands": [
                {
                    "band": band,
                    "name": raster.bandName(band),
                    "source_has_nodata": provider.sourceHasNoDataValue(band),
                    "source_nodata": (
                        clean_number(provider.sourceNoDataValue(band))
                        if provider.sourceHasNoDataValue(band)
                        else None
                    ),
                }
                for band in bands
            ],
        },
        "aoi": {
            "layer_id": aoi.id(),
            "feature_id": aoi_feature_id,
            "crs": crs_info(aoi.crs()),
            "geometry_valid": True,
            "overlaps_raster_extent": True,
            "extends_outside_raster_extent": extends_outside,
        },
        "requires_metric_working_crs": not metric_crs,
        "pixel_validity_checked": False,
        "model_checked": False,
    }, warnings)

def _build_preparation_step(
        raster_layer_id: str,
        aoi_layer_id: str,
        aoi_feature_id: int,
        rgb_bands: list[int],
        output_parent: str,
        validity_policy: str,
) -> tuple[PrepareLandcover, list[str]]:
    """Capture les entrées sans transmettre d'objet QGIS à la tâche."""
    try:
        config = PreparationConfig(
            validity_policy=validity_policy,
            max_pixels=1_000_000,
        )
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc

    if not isinstance(output_parent, str) or not output_parent.strip():
        _reject("Un dossier parent de sortie est obligatoire.")

    try:
        parent = Path(output_parent).expanduser()
        if not parent.is_absolute():
            _reject("Le dossier parent de sortie doit être un chemin absolu.")
        parent = parent.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ToolError(
            ErrorCode.INVALID_PARAMS,
            "Impossible de résoudre le dossier parent de sortie.",
        ) from exc

    if not parent.is_dir():
        _reject("Le dossier parent de sortie doit être un dossier existant.")

    inspection = inspect_landcover_inputs(
        raster_layer_id=raster_layer_id,
        aoi_layer_id=aoi_layer_id,
        aoi_feature_id=aoi_feature_id,
        rgb_bands=rgb_bands,
    )

    raster = get_raster_layer(raster_layer_id)
    aoi = get_vector_layer(aoi_layer_id)

    if raster.crs() != aoi.crs():
        _reject(
            "Cette préparation native exige un périmètre déjà dans le "
            "même SCR que le raster. Aucune projection automatique."
        )

    if inspection.data["requires_metric_working_crs"]:
        _reject("Cette préparation exige un SCR projeté exprimé en mètres.")

    if raster.bandCount() != 3:
        _reject("Cette préparation exige exactement trois bandes raster.")

    if raster.width() * raster.height() > config.max_pixels:
        _reject(
            "Cette version est limitée à 1 000 000 pixels sur le raster "
            "entier, même si le périmètre est plus petit."
        )

    geometry = _read_aoi_geometry(aoi, aoi_feature_id)
    bands = validate_rgb_bands(rgb_bands, raster.bandCount())
    path_text = source_path(raster)
    if not path_text:
        _reject("Impossible de retrouver le fichier source du raster.")

    warnings = [
        "L'ordre RGB est déclaré par l'utilisateur.",
        "Le géoréférencement est contrôlé techniquement, "
        "pas validé par des points de contrôle terrain.",
        "Les masques source sont respectés : une valeur déclarée NoData "
        "peut exclure un pixel sans prouver une absence réelle de donnée.",
        "Préparation uniquement : aucune segmentation ni classification.",
    ]

    if inspection.data["aoi"]["extends_outside_raster_extent"]:
        warnings.append(
            "Une partie du périmètre est hors de l'emprise du raster ; "
            "elle ne sera pas représentée dans les masques produits."
        )

    if aoi.isEditable():
        warnings.append(
            "Le périmètre provient de l'état courant du tampon d'édition."
        )

    step = PrepareLandcover(
        raster_path=Path(path_text),
        aoi_wkb=bytes(geometry.asWkb()),
        aoi_crs_wkt=aoi.crs().toWkt(),
        rgb_bands=bands,
        output_parent=parent,
        config=config,
    )
    return step, warnings

@tool(level=Level.CREATE, params={
    "raster_layer_id": Param(
        "string",
        "Identifiant du GeoTIFF local chargé dans QGIS.",
    ),
    "aoi_layer_id": Param(
        "string",
        "Identifiant de la couche polygonale du périmètre.",
    ),
    "aoi_feature_id": Param(
        "integer",
        "Identifiant QGIS de l'entité polygonale à analyser.",
    ),
    "rgb_bands": Param(
        "array",
        "Trois indices distincts dans l'ordre rouge, vert, bleu.",
        items="integer",
    ),
    "output_parent": Param(
        "string",
        "Chemin absolu d'un dossier existant pour les sorties.",
    ),
    "validity_policy": Param(
        "string",
        "Politique explicite de validité des pixels.",
        enum=("respect_source_masks",),
    ),
})
def prepare_landcover_inputs(
    raster_layer_id: str,
    aoi_layer_id: str,
    aoi_feature_id: int,
    rgb_bands: list[int],
    output_parent: str,
    validity_policy: str,
) -> Steps:
    """Prépare les entrées OBIA dans un nouveau dossier, sans segmentation.

    GeoTIFF local à trois bandes, limité à un million de pixels.
    Le périmètre doit déjà partager le SCR projeté métrique du raster.
    Produit les rasters de préparation et leur manifeste, sans modifier
    la source ni charger de couche. Exécution par job avec annulation
    coopérative. Le dossier parent doit déjà exister.
    """
    step, warnings = _build_preparation_step(
        raster_layer_id=raster_layer_id,
        aoi_layer_id=aoi_layer_id,
        aoi_feature_id=aoi_feature_id,
        rgb_bands=rgb_bands,
        output_parent=output_parent,
        validity_policy=validity_policy,
    )

    report = yield step

    excluded = report["counts"]["invalid_pixels_inside_aoi"]
    if excluded:
        warnings.append(
            f"{excluded} pixels du périmètre sont exclus "
            "par les masques source."
        )

    directory = Path(report["output_directory"])
    outputs = [
        str(directory / filename)
        for filename in report["files"]
    ]


    return ToolResult(
        data=report,
        warnings=warnings,
        outputs=outputs,
    )
