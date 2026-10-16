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
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsMapLayer,
    QgsProject,
    QgsProviderRegistry,
    QgsRasterLayer,
    QgsRectangle,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType, Qt

from ..core.errors import ErrorCode, ToolError
from ..core.fields import resolve_type
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


def get_raster_layer(layer_id: str) -> QgsRasterLayer:
    layer = get_layer(layer_id)
    if not isinstance(layer, QgsRasterLayer):
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche raster.")
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
    """Analyse et prépare une expression QGIS. Détecte la syntaxe invalide et les champs
    inconnus."""
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
                    attributes: list[str] | None = None,
                    geometry: bool = True) -> QgsFeatureRequest:
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


def iter_geometries(layer: QgsVectorLayer, request: QgsFeatureRequest,
                    crs: QgsCoordinateReferenceSystem | None = None):
    """(entité, copie de sa géométrie dans crs) pour chaque entité non vide.

    Les entités impossibles à reprojeter sont ignorées.
    """
    transform = None
    if crs is not None and crs != layer.crs():
        transform = QgsCoordinateTransform(layer.crs(), crs, QgsProject.instance())
    for feature in layer.getFeatures(request):
        geometry = feature.geometry()
        if geometry.isNull() or geometry.isEmpty():
            continue
        geometry = QgsGeometry(geometry)
        if transform is not None:
            try:
                geometry.transform(transform)
            except QgsCsException:
                continue
        yield feature, geometry


# --- Mesures ---------------------------------------------------------------
def distance_area(crs: QgsCoordinateReferenceSystem,
                  method: str = "ellipsoidal") -> QgsDistanceArea:
    """ellipsoidal : mesure sur l'ellipsoïde (GRS80 par défaut, celui du RGR92 et du RGM04).
    planar : mesure dans le SCR de la couche (qui doit être projeté)."""
    if not crs.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        "SCR de la couche non défini : mesure impossible.")
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

# --- Édition et champs -----------------------------------------------------
_META_TYPES = {
    "QString": QMetaType.Type.QString,
    "int": QMetaType.Type.Int,
    "qlonglong": QMetaType.Type.LongLong,
    "double": QMetaType.Type.Double,
    "bool": QMetaType.Type.Bool,
    "QDate": QMetaType.Type.QDate,
    "QDateTime": QMetaType.Type.QDateTime,
}


def crs_from_text(value: str) -> QgsCoordinateReferenceSystem:
    """SCR à partir d'un code : « EPSG:2975 », « 2975 »… INVALID_PARAMS si inconnu."""
    text = str(value).strip()
    crs = QgsCoordinateReferenceSystem(f"EPSG:{text}" if text.isdigit() else text)
    if not crs.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Système de coordonnées inconnu : {value}")
    return crs


def make_field(name: str, type_name: str, length: int = 0, precision: int = 0) -> QgsField:
    """QgsField à partir d'un type Cynogis (QMetaType : QGIS >= 3.38 et 4.x)."""
    try:
        spec = resolve_type(type_name)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    return QgsField(name, _META_TYPES[spec.qt_name], "", int(length) or spec.default_length,
                    int(precision) or spec.default_precision)


def polygon_parts(geometry: QgsGeometry | None) -> QgsGeometry | None:
    """Parties surfaciques d'une géométrie, None s'il n'y en a pas.

    Une intersection ou une différence peut renvoyer une collection mêlant polygones, lignes
    et points (bords en contact). convertToType(Polygon) renvoie alors une géométrie vide
    sous QGIS 4 : la surface serait perdue sans erreur."""
    if geometry is None or geometry.isNull() or geometry.isEmpty():
        return None
    if geometry.type() == Qgis.GeometryType.Polygon:
        return geometry
    parts = [part for part in geometry.asGeometryCollection()
             if part.type() == Qgis.GeometryType.Polygon and not part.isEmpty()]
    return QgsGeometry.collectGeometry(parts) if parts else None


def add_to_memory(layer: QgsVectorLayer, features: list[QgsFeature]) -> list[str]:
    """Ajoute des entités au fournisseur d'une couche (mémoire) et vérifie le résultat.

    addFeatures renvoie un tuple (ok, entités) : un test « if not … » ne détecte jamais
    l'échec, et la couche mémoire refuse en silence une entité dont un texte dépasse la
    longueur du champ. Ces textes sont donc tronqués (« … ») ; tout autre refus lève une
    erreur. Renvoie l'avertissement à ajouter au résultat si des textes ont été tronqués."""
    limits = {index: field.length() for index, field in enumerate(layer.fields())
              if field.type() == QMetaType.Type.QString and field.length() > 0}
    truncated = 0
    for feature in features:
        for index, limit in limits.items():
            value = feature.attribute(index)
            if isinstance(value, str) and len(value) > limit:
                feature.setAttribute(index, value[:limit - 1] + "…")
                truncated += 1
    ok, _ = layer.dataProvider().addFeatures(features)
    if not ok:
        raise ToolError(ErrorCode.INTERNAL_ERROR, "Création des entités impossible.",
                        {"error": layer.dataProvider().lastError()})
    return ([f"{truncated} texte(s) plus long(s) que leur champ, tronqué(s) (« … »)."]
            if truncated else [])

def field_type_name(field: QgsField) -> str:
    """Type Cynogis correspondant à un champ existant ('string' par défaut)."""
    type_name = field.typeName().lower()
    if "int64" in type_name or "long" in type_name:
        return "long"
    if "int" in type_name:
        return "integer"
    if any(token in type_name for token in ("real", "double", "float", "numeric", "decimal")):
        return "real"
    if "datetime" in type_name or "timestamp" in type_name:
        return "datetime"
    if "date" in type_name:
        return "date"
    if "bool" in type_name:
        return "boolean"
    return "string"


def layer_field_types(layer: QgsVectorLayer) -> dict[str, str]:
    """Table {nom de champ: type Cynogis} d'une couche."""
    return {field.name(): field_type_name(field) for field in layer.fields()}


def is_shapefile(layer: QgsVectorLayer) -> bool:
    return "shapefile" in (layer.storageType() or "").lower()


def begin_edit(layer: QgsVectorLayer, capability: Any, action: str) -> None:
    """Contrôle que la source accepte l'opération puis ouvre le tampon d'édition si besoin."""
    if not layer.dataProvider().capabilities() & capability:
        raise ToolError(ErrorCode.READ_ONLY,
                        f"« {layer.name()} » n'autorise pas {action} (service web, fichier "
                        "verrouillé…). Exporte-la d'abord avec export_layer.")
    if not layer.isEditable() and not layer.startEditing():
        raise ToolError(ErrorCode.EDIT_FAILED,
                        f"Impossible d'ouvrir l'édition sur « {layer.name()} » : fichier "
                        "peut-être ouvert dans un autre logiciel.")


def wkt_to_layer_crs(wkt: str, layer: QgsVectorLayer, source_crs: str | None = None
                     ) -> QgsGeometry:
    """Géométrie WKT lue puis reprojetée de source_crs vers le SCR de la couche."""
    geometry = QgsGeometry.fromWkt(str(wkt))
    if geometry.isNull():
        raise ToolError(ErrorCode.INVALID_GEOMETRY,
                        f"WKT illisible : {str(wkt)[:80]}… Attendu par ex. "
                        "POLYGON((x1 y1, x2 y2, x3 y3, x1 y1)).")
    if source_crs:
        origin = crs_from_text(source_crs)
        if origin != layer.crs():
            transform = QgsCoordinateTransform(origin, layer.crs(), QgsProject.instance())
            try:
                failed = geometry.transform(transform) != Qgis.GeometryOperationResult.Success
            except QgsCsException:
                failed = True
            if failed:
                raise ToolError(ErrorCode.INVALID_GEOMETRY,
                                f"Reprojection {origin.authid()} → {layer.crs().authid()} "
                                "impossible.")
    return geometry


def geometry_from_wkt(wkt: str, layer: QgsVectorLayer, source_crs: str | None = None
                      ) -> QgsGeometry:
    """Géométrie WKT contrôlée : reprojetée vers la couche, bon type, multi si besoin, valide."""
    geometry = wkt_to_layer_crs(wkt, layer, source_crs)
    expected = layer.geometryType()
    if geometry.type() != expected:
        raise ToolError(ErrorCode.INVALID_GEOMETRY,
                        f"La couche attend des géométries {_GEOMETRY_NAMES.get(expected, '?')}, "
                        f"reçu {_GEOMETRY_NAMES.get(geometry.type(), '?')}.")
    if QgsWkbTypes.isMultiType(layer.wkbType()):
        geometry.convertToMultiType()
    if not geometry.isGeosValid():
        fixed = geometry.makeValid()
        if not fixed.isEmpty():
            geometry = fixed
    return geometry


def select_ids(layer: QgsVectorLayer, expression: str | None, feature_ids: list | None = None,
               limit: int | None = None) -> list[int]:
    """fid visés par une liste d'identifiants (tous doivent exister) ou par une expression.

    Sans l'un ni l'autre : toute la couche. Avec limit, s'arrête à limit + 1 entités pour que
    l'appelant puisse détecter le dépassement sans tout parcourir.
    """
    if feature_ids:
        wanted = list(dict.fromkeys(int(value) for value in feature_ids))
        request = QgsFeatureRequest().setFilterFids(wanted)
        request.setNoAttributes()
        request.setFlags(Qgis.FeatureRequestFlag.NoGeometry)
        existing = {feature.id() for feature in layer.getFeatures(request)}
        missing = [fid for fid in wanted if fid not in existing]
        if missing:
            raise ToolError(ErrorCode.INVALID_PARAMS,
                            f"Entités introuvables dans « {layer.name()} » : {missing[:10]}")
        return wanted
    ids: list[int] = []
    for feature in layer.getFeatures(feature_request(layer, expression, [], False)):
        ids.append(feature.id())
        if limit is not None and len(ids) > limit:
            break
    return ids


def refresh_layer(layer: QgsVectorLayer) -> None:
    """Rafraîchit l'affichage après modification du tampon."""
    layer.updateExtents()
    layer.triggerRepaint()
