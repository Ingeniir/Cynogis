"""Dérivés du modèle numérique de terrain : pente, exposition, ombrage, classes de pente."""
from __future__ import annotations

from ..core import terrain as relief
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import get_raster_layer
from .geoprocessing import OUTPUT_NAME
from .outputs import run_to_project

DERIVATIVES = {
    "slope": ("native:slope", "pente",
              "Valeurs en degrés : classify_slope (unit=degrees) pour les classes en %."),
    "aspect": ("native:aspect", "exposition",
               "0 = nord, sens horaire ; valeurs négatives = terrain plat."),
    "hillshade": ("native:hillshade", "ombrage", "Ombrage destiné à l'habillage cartographique."),
}
# native:reclassifybytable : RANGE_BOUNDARIES 1 = « min <= valeur < max » ; DATA_TYPE 0 = Byte.
RANGE_MIN_INCLUSIVE = 1
BYTE = 0
NO_DATA = 0  # les classes vont de 1 à 5


def _metric_raster(layer_id: str):
    layer = get_raster_layer(layer_id)
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC,
                        f"{layer.name()} est en degrés ({layer.crs().authid()}) : pentes "
                        "fausses. Reprojette le MNT en EPSG:2975 (Réunion) ou EPSG:4471 "
                        "(Mayotte), ex. run_algorithm gdal:warpreproject.")
    return layer


@tool(level=Level.READ, params={})
def list_slope_classes() -> dict:
    """Classes de pente d'aménagement (0-5, 5-15, 15-30, 30-50, > 50 %) et secteurs
    d'exposition utilisés par classify_slope."""
    return {"classes": [item.to_dict() for item in relief.SLOPE_CLASSES],
            "aspect_sectors": [name for name, _, _ in relief.ASPECT_SECTORS]}


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "MNT raster (layer_id), en SCR métrique."),
    "derivative": Param("string", "slope (pente, degrés), aspect (exposition) ou hillshade "
                        "(ombrage).", required=False, default="slope", enum=tuple(DERIVATIVES)),
    "z_factor": Param("number", "Facteur vertical ; 1 si altitudes et coordonnées en mètres.",
                      required=False, default=1, minimum=0.0001, maximum=1000),
    "output_name": OUTPUT_NAME,
})
def derive_terrain(layer_id: str, derivative: str, z_factor: float,
                   output_name: str | None) -> ToolResult:
    """Calcule la pente, l'exposition ou l'ombrage d'un MNT (nouveau raster .tif dans
    mcp_outputs/). Le MNT doit être en SCR métrique (EPSG:2975, EPSG:4471)."""
    layer = _metric_raster(layer_id)
    algorithm, label, note = DERIVATIVES[derivative]
    result = run_to_project(algorithm, {"INPUT": layer, "Z_FACTOR": float(z_factor)},
                            output_name or f"{label}_{layer.name()}")
    result.data.update({"derivative": derivative, "note": note})
    return result


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Raster de pente (layer_id), produit par derive_terrain."),
    "unit": Param("string", "Unité des valeurs du raster de pente (derive_terrain : degrees).",
                  required=False, default="degrees", enum=("degrees", "percent")),
    "vectorize": Param("boolean", "Produire aussi des polygones par classe (champ classe).",
                       required=False, default=True),
    "output_name": OUTPUT_NAME,
})
def classify_slope(layer_id: str, unit: str, vectorize: bool,
                   output_name: str | None) -> ToolResult:
    """Reclasse un raster de pente en 5 classes d'aménagement (1 plat à faible … 5 escarpée,
    voir list_slope_classes) ; avec vectorize, polygones à croiser avec les parcelles
    (overlay) pour mesurer les surfaces par classe."""
    layer = get_raster_layer(layer_id)
    name = output_name or f"classes_pente_{layer.name()}"
    result = run_to_project("native:reclassifybytable", {
        "INPUT_RASTER": layer, "RASTER_BAND": 1,
        "TABLE": [value for row in relief.reclass_table(unit) for value in row],
        "NO_DATA": NO_DATA, "RANGE_BOUNDARIES": RANGE_MIN_INCLUSIVE, "DATA_TYPE": BYTE,
    }, name)
    result.data.update({"unit": unit,
                        "classes": [item.to_dict() for item in relief.SLOPE_CLASSES]})
    if vectorize:
        raster_path = result.data["outputs"][0]["path"]
        polygons = run_to_project("gdal:polygonize", {
            "INPUT": raster_path, "BAND": 1, "FIELD": "classe", "EIGHT_CONNECTEDNESS": False,
        }, f"{name}_poly")
        result.data["polygons"] = polygons.data["outputs"]
        result.warnings.extend(w for w in polygons.warnings if w not in result.warnings)
        result.outputs.extend(polygons.outputs)
    return result
