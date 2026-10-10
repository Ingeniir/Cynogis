"""Fonctions utilitaires PyQGIS partagées par les outils (compatibles QGIS 3.44 et 4.x)."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCsException,
    QgsMapLayer,
    QgsProject,
    QgsProviderRegistry,
    QgsRasterLayer,
    QgsRectangle,
    QgsUnitTypes,
    QgsVectorLayer,
)

from ..core.errors import ErrorCode, ToolError
from ..core.territory import UNKNOWN, detect_territory

WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")
_GEOMETRY_NAMES = {
    Qgis.GeometryType.Point: "point",
    Qgis.GeometryType.Line: "line",
    Qgis.GeometryType.Polygon: "polygon",
    Qgis.GeometryType.Null: "none",
    Qgis.GeometryType.Unknown: "unknown",
}


def enum_name(value: Any) -> str:
    return getattr(value, "name", str(value))


def clean_number(value: float | None) -> float | None:
    return None if value is None or math.isnan(value) or math.isinf(value) else value


def get_layer(layer_id: str) -> QgsMapLayer:
    project = QgsProject.instance()
    layer = project.mapLayer(layer_id)
    if layer is None:
        available = [{"layer_id": lyr.id(), "name": lyr.name()}
                     for lyr in list(project.mapLayers().values())[:30]]
        raise ToolError(ErrorCode.LAYER_NOT_FOUND,
                        f"Aucune couche avec l'identifiant {layer_id!r}. Utilise list_layers.",
                        {"available": available})
    return layer


def get_vector_layer(layer_id: str) -> QgsVectorLayer:
    layer = get_layer(layer_id)
    if not isinstance(layer, QgsVectorLayer):
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche vecteur.")
    return layer


def layer_kind(layer: QgsMapLayer) -> str:
    if isinstance(layer, QgsVectorLayer):
        return "vector"
    if isinstance(layer, QgsRasterLayer):
        return "raster"
    return "other"


def geometry_kind(layer: QgsVectorLayer) -> str:
    return _GEOMETRY_NAMES.get(layer.geometryType(), "unknown")


def source_path(layer: QgsMapLayer) -> str | None:
    """Chemin du fichier source (None pour mémoire, PostGIS…). N'expose jamais d'identifiants."""
    parts = QgsProviderRegistry.instance().decodeUri(layer.providerType(), layer.source())
    return parts.get("path") or None


def file_format(layer: QgsMapLayer) -> str:
    path = source_path(layer)
    if path and Path(path).suffix:
        return Path(path).suffix.lower().lstrip(".")
    return layer.providerType()  # memory, postgres, wms…


def rect_to_list(rect: QgsRectangle | None, ndigits: int = 6) -> list[float] | None:
    if rect is None or rect.isNull():
        return None
    return [round(v, ndigits) for v in
            (rect.xMinimum(), rect.yMinimum(), rect.xMaximum(), rect.yMaximum())]


def extent_wgs84(layer: QgsMapLayer) -> QgsRectangle | None:
    extent = layer.extent()
    if extent.isNull() or not layer.crs().isValid():
        return None
    try:
        transform = QgsCoordinateTransform(layer.crs(), WGS84, QgsProject.instance())
        return transform.transformBoundingBox(extent)
    except QgsCsException:
        return None


def crs_info(crs: QgsCoordinateReferenceSystem) -> dict[str, Any]:
    if not crs.isValid():
        return {"authid": None, "valid": False}
    try:
        units = QgsUnitTypes.toString(crs.mapUnits())
    except TypeError:
        units = enum_name(crs.mapUnits())
    return {"authid": crs.authid() or None, "description": crs.description(), "valid": True,
            "is_geographic": crs.isGeographic(), "map_units": units}


def territory_info(layer: QgsMapLayer) -> tuple[dict[str, Any], list[str]]:
    """Territoire détecté + avertissements sur le SCR."""
    warnings: list[str] = []
    territory = detect_territory(rect_to_list(extent_wgs84(layer)))
    crs = layer.crs()
    if not crs.isValid():
        warnings.append(f"{layer.name()} : SCR non défini.")
    elif crs.isGeographic():
        warnings.append(f"{layer.name()} : SCR géographique ({crs.authid()}), à reprojeter "
                        "avant toute mesure de surface ou de distance.")
    elif territory and crs.authid() != territory.epsg:
        warnings.append(f"{layer.name()} : SCR {crs.authid()} différent du SCR de référence "
                        f"{territory.epsg} ({territory.name}).")
    return (territory.as_dict() if territory else dict(UNKNOWN)), warnings
