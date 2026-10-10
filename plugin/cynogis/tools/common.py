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
    QgsDistanceArea,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsFeatureRequest,
    QgsGeometry,
    QgsMapLayer,
    QgsProject,
    QgsProviderRegistry,
    QgsRasterLayer,
    QgsRectangle,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import Qt


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

# --- Valeurs ---------------------------------------------------------------
def to_json_value(value: Any) -> Any:
    """Convertit une valeur d'attribut QGIS (NULL, QDate…) en valeur JSON."""
    if value is None:
        return None
    if isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return clean_number(value)
    if isinstance(value, (list, tuple)):
        return [to_json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_json_value(v) for k, v in value.items()}
    if hasattr(value, "isNull") and value.isNull():  # NULL (QVariant), QDate nulle…
        return None
    if hasattr(value, "toString"):  # QDate, QDateTime, QTime
        try:
            return value.toString(Qt.DateFormat.ISODate)
        except TypeError:
            return value.toString()
    return str(value)


def group_key(value: Any) -> Any:
    """Valeur utilisable comme clé de regroupement (hashable)."""
    v = to_json_value(value)
    return v if v is None or isinstance(v, (str, int, float, bool)) else str(v)


# --- Champs et expressions --------------------------------------------------
def require_field(layer: QgsVectorLayer, name: str) -> str:
    """Renvoie le nom exact du champ (insensible à la casse) ou lève INVALID_PARAMS."""
    fields = layer.fields()
    idx = fields.lookupField(name)
    if idx < 0:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"Champ {name!r} introuvable dans {layer.name()}.",
                        {"available": fields.names()})
    return fields.at(idx).name()


def expression_context(layer: QgsVectorLayer) -> QgsExpressionContext:
    return QgsExpressionContext(QgsExpressionContextUtils.globalProjectLayerScopes(layer))


def prepare_expression(text: str, layer: QgsVectorLayer,
                       label: str = "expression") -> tuple[QgsExpression, QgsExpressionContext]:
    """Analyse et prépare une expression QGIS. Détecte la syntaxe invalide et les champs inconnus."""
    expression = QgsExpression(text)
    if expression.hasParserError():
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"{label} invalide : {expression.parserErrorString()}",
                        {"expression": text})
    context = expression_context(layer)
    if not expression.prepare(context):
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"{label} invalide : {expression.evalErrorString()}",
                        {"expression": text, "fields": layer.fields().names()})
    return expression, context


def feature_request(layer: QgsVectorLayer, filter_expression: str | None = None,
                    attributes: list[str] | None = None, geometry: bool = True) -> QgsFeatureRequest:
    """Requête optimisée. attributes=None : tous les champs ; [] : aucun champ."""
    request = QgsFeatureRequest()
    filter_needs_geometry = False
    if filter_expression:
        expression, context = prepare_expression(filter_expression, layer, "filter_expression")
        filter_needs_geometry = expression.needsGeometry()
        request.setFilterExpression(filter_expression)
        request.setExpressionContext(context)
    if attributes is not None:
        if attributes:
            request.setSubsetOfAttributes(list(dict.fromkeys(attributes)), layer.fields())
        else:
            request.setNoAttributes()
    if not geometry and not filter_needs_geometry:
        request.setFlags(Qgis.FeatureRequestFlag.NoGeometry)
    return request


# --- Mesures ---------------------------------------------------------------
def distance_area(crs: QgsCoordinateReferenceSystem, method: str = "ellipsoidal") -> QgsDistanceArea:
    """ellipsoidal : mesure sur l'ellipsoïde (GRS80 par défaut, celui du RGR92 et du RGM04).
    planar : mesure dans le SCR de la couche (qui doit être projeté)."""
    if not crs.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS, "SCR de la couche non défini : mesure impossible.")
    project = QgsProject.instance()
    da = QgsDistanceArea()
    da.setSourceCrs(crs, project.transformContext())
    if method == "ellipsoidal":
        ellipsoid = project.ellipsoid()
        da.setEllipsoid(ellipsoid if ellipsoid and ellipsoid != "NONE" else "GRS80")
    else:
        if crs.isGeographic():
            raise ToolError(ErrorCode.CRS_GEOGRAPHIC,
                            f"Mesure planaire impossible en SCR géographique ({crs.authid()}). "
                            "Utilise method='ellipsoidal' ou reprojette la couche.")
        da.setEllipsoid("NONE")
    return da


def area_m2(da: QgsDistanceArea, geometry: QgsGeometry) -> float:
    return da.convertAreaMeasurement(da.measureArea(geometry), Qgis.AreaUnit.SquareMeters)


def length_m(da: QgsDistanceArea, geometry: QgsGeometry) -> float:
    return da.convertLengthMeasurement(da.measureLength(geometry), Qgis.DistanceUnit.Meters)


def perimeter_m(da: QgsDistanceArea, geometry: QgsGeometry) -> float:
    return da.convertLengthMeasurement(da.measurePerimeter(geometry), Qgis.DistanceUnit.Meters)
