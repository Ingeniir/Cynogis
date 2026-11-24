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
from ..core.jobs import (
    DelineateLandcover,
    ExtractLandcoverFeatures,
    PrepareLandcover,
    SegmentLandcover,
    Steps,
)
from ..core.landcover import (
    DelineationConfig,
    PreparationConfig,
    resolve_output_parent,
    validate_rgb_bands,
)
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    area_m2,
    area_method,
    clean_number,
    crs_info,
    distance_area,
    get_raster_layer,
    get_vector_layer,
    source_path,
)
from .outputs import add_to_project, obia_output_root

_OUTPUT_PARENT_HELP = (
    "Facultatif. Omis : <projet>/mcp_outputs/obia/ choisi par Cynogis. Fourni : "
    "dossier existant dans cette racine ; une valeur extérieure est refusée."
)


def _output_parent(value: str | None) -> tuple[Path, list[str]]:
    """Destination imposée par Cynogis (voir core.landcover.resolve_output_parent)."""
    root, warnings = obia_output_root()
    try:
        return resolve_output_parent(value, root), warnings
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc

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
        output_parent: str | None,
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

    # En dernier : la racine n'est créée que pour un appel par ailleurs valide.
    parent, root_warnings = _output_parent(output_parent)
    warnings.extend(root_warnings)

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
    "validity_policy": Param(
        "string",
        "Politique explicite de validité des pixels.",
        enum=("respect_source_masks",),
    ),
    "output_parent": Param("string", _OUTPUT_PARENT_HELP, required=False),
})
def prepare_landcover_inputs(
    raster_layer_id: str,
    aoi_layer_id: str,
    aoi_feature_id: int,
    rgb_bands: list[int],
    validity_policy: str,
    output_parent: str | None = None,
) -> Steps:
    """Prépare les entrées OBIA dans un nouveau dossier, sans segmentation.

    GeoTIFF local à trois bandes, limité à un million de pixels.
    Le périmètre doit déjà partager le SCR projeté métrique du raster.
    Produit les rasters de préparation et leur manifeste, sans modifier
    la source ni charger de couche. Exécution par job avec annulation
    coopérative. Sorties dans <projet>/mcp_outputs/obia/ (repli
    ~/.cynogis/mcp_outputs/obia/ si le projet n'est pas enregistré).
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


def _segmentation_directory(value: str, name: str) -> Path:
    """Résout un dossier existant sans lire son contenu."""
    if not isinstance(value, str) or not value.strip():
        raise ToolError(
            ErrorCode.INVALID_PARAMS,
            f"{name} doit être un chemin non vide.",
        )

    try:
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise ToolError(
                ErrorCode.INVALID_PARAMS,
                f"{name} doit être un chemin absolu.",
            )
        resolved = path.resolve(strict=True)
        is_directory = resolved.is_dir()
    except (OSError, RuntimeError, ValueError) as exc:
        raise ToolError(
            ErrorCode.INVALID_PARAMS,
            f"{name} : dossier inaccessible ou chemin invalide.",
        ) from exc

    if not is_directory:
        raise ToolError(
            ErrorCode.INVALID_PARAMS,
            f"{name} doit désigner un dossier existant.",
        )
    return resolved


def _build_segmentation_step(
    preparation_directory: str,
    output_parent: str | None,
    target_segment_area_m2: float,
    compactness: float,
    max_num_iter: int,
) -> tuple[SegmentLandcover, list[str]]:
    """Valide les paramètres publics sans ouvrir de manifeste ou de raster."""
    # Import local : le catalogue ne doit pas charger le module de segmentation.
    # SlicConfig lui-même ne charge pas les dépendances de calcul.
    from ..landcover_processing.segment import SlicConfig

    try:
        config = SlicConfig(
            target_segment_area_m2=target_segment_area_m2,
            compactness=compactness,
            max_num_iter=max_num_iter,
        )
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc

    source = _segmentation_directory(
        preparation_directory, "preparation_directory"
    )
    parent, warnings = _output_parent(output_parent)

    # Même règle que le moteur, appliquée aux chemins résolus.
    # Le moteur refait ce contrôle et demeure responsable de la validité
    # des fichiers. Cette vérification n'est pas un verrou de fichiers.
    if parent == source or source in parent.parents:
        raise ToolError(
            ErrorCode.INVALID_PARAMS,
            "Le parent de sortie doit être extérieur au dossier de préparation.",
        )

    step = SegmentLandcover(
        preparation_directory=source,
        output_parent=parent,
        config=config,
    )
    return step, warnings


@tool(level=Level.CREATE, params={
    "preparation_directory": Param(
        "string",
        "Chemin absolu du dossier produit par prepare_landcover_inputs.",
    ),
    "output_parent": Param(
        "string",
        _OUTPUT_PARENT_HELP + " Toujours extérieur au dossier de préparation.",
        required=False,
    ),
    "target_segment_area_m2": Param(
        "number",
        "Surface cible strictement positive en m² ; pas un minimum garanti.",
        required=False,
        default=25.0,
    ),
    "compactness": Param(
        "number",
        "Compacité SLIC finie et strictement positive.",
        required=False,
        default=10.0,
    ),
    "max_num_iter": Param(
        "integer",
        "Nombre maximal d'itérations SLIC, entre 1 et 100.",
        required=False,
        default=10,
        minimum=1,
        maximum=100,
    ),
})
def segment_landcover(
    preparation_directory: str,
    output_parent: str | None = None,
    target_segment_area_m2: float = 25.0,
    compactness: float = 10.0,
    max_num_iter: int = 10,
) -> Steps:
    """Segmente une préparation OBIA en objets non classés, via un job.

    Produit segments.tif et segmentation.json dans un nouveau dossier,
    sous <projet>/mcp_outputs/obia/ (repli ~/.cynogis/mcp_outputs/obia/).
    Limites du moteur : un million de pixels et dix mille graines demandées.
    Aucun chargement de couche, classement de paysages ou vectorisation.
    Les contrôles des fichiers et le calcul s'exécutent dans la tâche.
    Annulation entre phases : un appel SLIC en cours n'est pas interrompu.
    Les valeurs par défaut sont expérimentales, pas une validation terrain.
    """
    step, root_warnings = _build_segmentation_step(
        preparation_directory=preparation_directory,
        output_parent=output_parent,
        target_segment_area_m2=target_segment_area_m2,
        compactness=compactness,
        max_num_iter=max_num_iter,
    )

    # Ne pas intercepter ici les erreurs de la tâche : préserver les règles
    # existantes d'annulation, d'erreur technique et de résultat tardif.
    report = yield step

    directory = Path(report["output_directory"])
    return ToolResult(
        data=report,
        warnings=[
            *root_warnings,
            "Les identifiants sont des objets non classés, pas des classes "
            "de paysage. Aucune couche n'a été ajoutée au projet.",
            "La surface cible ne garantit ni le nombre final d'objets "
            "ni une surface minimale.",
            "Le masque de la préparation est conservé ; les zones exclues "
            "ne sont ni complétées ni classées.",
            "Les diagnostics sont descriptifs : ils ne valident pas "
            "la qualité géographique des limites.",
        ],
        outputs=[str(directory / name) for name in report["files"]],
    )


def _sources(**paths: str) -> tuple[dict[str, Path], Path, list[str]]:
    """Dossiers sources résolus et parent de sortie, distincts et non imbriqués."""
    resolved = {name: _segmentation_directory(value, name) for name, value in paths.items()}
    if len(set(resolved.values())) != len(resolved):
        raise ToolError(ErrorCode.INVALID_PARAMS, "Les dossiers sources doivent être distincts.")
    return resolved, *_checked_parent(resolved.values())


def _checked_parent(sources) -> tuple[Path, list[str]]:
    # Le parent vient toujours de la racine imposée : pas de paramètre libre ici.
    parent, warnings = _output_parent(None)
    if any(parent == src or src in parent.parents for src in sources):
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        "La racine de sortie OBIA ne doit pas être dans un dossier source.")
    return parent, warnings


@tool(level=Level.CREATE, params={
    "preparation_directory": Param(
        "string", "Chemin absolu du dossier produit par prepare_landcover_inputs."),
    "segmentation_directory": Param(
        "string", "Chemin absolu du dossier produit par segment_landcover."),
})
def extract_landcover_features(
    preparation_directory: str,
    segmentation_directory: str,
) -> Steps:
    """Calcule les caractéristiques des objets segmentés (couleur, emprise, voisinage).

    Produit objects.npy, edges.npy et features.json dans un nouveau dossier, sous
    <projet>/mcp_outputs/obia/ (repli ~/.cynogis/mcp_outputs/obia/). Les sources
    sont vérifiées par empreinte : la préparation doit être celle de la segmentation.
    Exécution par job avec annulation coopérative. Aucune couche ajoutée au projet,
    aucune classification. Étape préalable à delineate_landcover.
    """
    sources, parent, warnings = _sources(
        preparation_directory=preparation_directory,
        segmentation_directory=segmentation_directory,
    )
    step = ExtractLandcoverFeatures(
        preparation_directory=sources["preparation_directory"],
        segmentation_directory=sources["segmentation_directory"],
        output_parent=parent,
    )
    report = yield step
    directory = Path(report["output_directory"])
    return ToolResult(
        data=report,
        warnings=[*warnings, "Caractéristiques descriptives d'objets non classés."],
        outputs=[str(directory / name) for name in report["files"]],
    )


def _ellipsoidal_total(layer) -> tuple[float, str]:
    da = distance_area(layer.crs())
    request = QgsFeatureRequest().setNoAttributes()
    # ponytail: parcours sur le thread principal, borné par le million de pixels du moteur
    total = sum(area_m2(da, feature.geometry()) for feature in layer.getFeatures(request))
    return total, area_method(da)


@tool(level=Level.CREATE, params={
    "preparation_directory": Param(
        "string", "Chemin absolu du dossier produit par prepare_landcover_inputs."),
    "segmentation_directory": Param(
        "string", "Chemin absolu du dossier produit par segment_landcover."),
    "features_directory": Param(
        "string", "Chemin absolu du dossier produit par extract_landcover_features."),
    "color_distance_max": Param(
        "number",
        "Écart de couleur RGB maximal (0 à 442, unités 0..255) pour fusionner deux "
        "unités voisines ; 0 désactive la fusion par similarité.",
        required=False, default=12.0, minimum=0, maximum=442),
    "min_mapping_area_m2": Param(
        "number",
        "Surface minimale de cartographie en m² : une unité plus petite rejoint sa "
        "voisine la plus proche en couleur ; 0 désactive.",
        required=False, default=150.0, minimum=0),
})
def delineate_landcover(
    preparation_directory: str,
    segmentation_directory: str,
    features_directory: str,
    color_distance_max: float = 12.0,
    min_mapping_area_m2: float = 150.0,
) -> Steps:
    """Délimite des unités homogènes en fusionnant les objets segmentés, via un job.

    Dernière étape OBIA : produit regions.tif, delineation.gpkg (un polygone par
    unité) et delineation.json sous <projet>/mcp_outputs/obia/, puis ajoute la
    couche des unités au groupe « Cynogis ». Les unités sont des zones homogènes en
    couleur, pas des classes d'occupation du sol. Surfaces : plane projetée 2D par
    unité (area_plan_m2) et total ellipsoïdal de référence.
    """
    try:
        config = DelineationConfig(color_distance_max=color_distance_max,
                                   min_mapping_area_m2=min_mapping_area_m2)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    sources, parent, warnings = _sources(
        preparation_directory=preparation_directory,
        segmentation_directory=segmentation_directory,
        features_directory=features_directory,
    )
    step = DelineateLandcover(
        preparation_directory=sources["preparation_directory"],
        segmentation_directory=sources["segmentation_directory"],
        features_directory=sources["features_directory"],
        output_parent=parent,
        config=config,
    )
    report = yield step

    directory = Path(report["output_directory"])
    layer = add_to_project(directory / "delineation.gpkg", f"Unités OBIA {report['run_id']}")
    total, method = _ellipsoidal_total(layer)
    diagnostics = report["diagnostics"]
    warnings = [
        *warnings,
        "Unités homogènes en couleur, non classées : ce ne sont pas des habitats ni des "
        "classes d'occupation du sol. Contrôle visuel et terrain indispensables.",
        "Limites en marches d'escalier sur la grille du raster, non simplifiées.",
        "Paramètres de fusion expérimentaux, pas une validation terrain.",
    ]
    if diagnostics["isolated_small_units"]:
        warnings.append(
            f"{diagnostics['isolated_small_units']} unités isolées restent plus petites "
            "que la surface minimale de cartographie.")
    return ToolResult(
        data={
            **report,
            "layer": {"layer_id": layer.id(), "name": layer.name(),
                      "feature_count": layer.featureCount()},
            "areas": {
                "total_plan_m2": diagnostics["analysis_area_m2"],
                "total_plan_method": report["area_method"],
                "total_ellipsoidal_m2": total,
                "total_ellipsoidal_method": method,
            },
        },
        warnings=warnings,
        outputs=[str(directory / name) for name in report["files"]],
    )
