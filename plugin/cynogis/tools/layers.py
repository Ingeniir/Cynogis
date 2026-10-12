from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import (
    Qgis,
    QgsMapLayer,
    QgsProject,
    QgsRasterBandStats,
    QgsRasterLayer,
    QgsRectangle,
    QgsVectorLayer,
    QgsWkbTypes,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    clean_number,
    crs_info,
    enum_name,
    extent_wgs84,
    file_format,
    geometry_kind,
    get_layer,
    get_raster_layer,
    layer_kind,
    rect_to_list,
    source_path,
    territory_info,
)


def _visible(layer: QgsMapLayer) -> bool | None:
    node = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
    return node.isVisible() if node else None


def _summary(layer: QgsMapLayer) -> dict[str, Any]:
    data: dict[str, Any] = {
        "layer_id": layer.id(), "name": layer.name(), "type": layer_kind(layer),
        "crs": layer.crs().authid() or None, "format": file_format(layer),
        "visible": _visible(layer),
    }
    if isinstance(layer, QgsVectorLayer):
        data.update(geometry_type=geometry_kind(layer),
                    wkb_type=QgsWkbTypes.displayString(layer.wkbType()),
                    feature_count=layer.featureCount(), is_editing=layer.isEditable())
    elif isinstance(layer, QgsRasterLayer):
        data.update(band_count=layer.bandCount(), width=layer.width(), height=layer.height())
    return data


@tool(level=Level.READ, params={
    "layer_type": Param("string", "Filtre par type de couche.", required=False, default="all",
                        enum=("all", "vector", "raster")),
    "geometry_type": Param("string", "Filtre par géométrie (couches vecteur uniquement).",
                           required=False, enum=("point", "line", "polygon", "none")),
})
def list_layers(layer_type: str, geometry_type: str | None) -> dict:
    """Liste les couches du projet dans l'ordre du panneau Couches : layer_id, nom, type
    (vector/raster), géométrie, SCR, format (shp, gpkg, tif…), nombre d'entités, visibilité,
    état d'édition. Utilise le layer_id renvoyé pour désigner une couche dans les autres outils."""
    layers = []
    for node in QgsProject.instance().layerTreeRoot().findLayers():
        layer = node.layer()
        if layer is None:
            continue
        summary = _summary(layer)
        if layer_type != "all" and summary["type"] != layer_type:
            continue
        if geometry_type and summary.get("geometry_type") != geometry_type:
            continue
        layers.append(summary)
    return {"count": len(layers), "layers": layers}


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Identifiant de la couche (layer_id renvoyé par list_layers)."),
})
def get_layer_info(layer_id: str) -> ToolResult:
    """Description détaillée d'une couche. Vecteur : champs (nom, type, longueur), encodage,
    filtre actif. Raster : bandes, type de données, nodata, taille de pixel. Pour les deux :
    SCR, emprise (SCR de la couche et WGS84), territoire détecté et SCR de référence."""
    return _info(get_layer(layer_id))


def _info(layer: QgsMapLayer) -> ToolResult:
    territory, warnings = territory_info(layer)
    path = source_path(layer)
    data = {
        **_summary(layer),
        "source_path": path,
        "crs_info": crs_info(layer.crs()),
        "extent": rect_to_list(layer.extent(), 3),
        "extent_wgs84": rect_to_list(extent_wgs84(layer)),
        "territory": territory,
    }
    if isinstance(layer, QgsVectorLayer):
        data.update(
            storage_type=layer.storageType(),
            encoding=layer.dataProvider().encoding() or None,
            subset_string=layer.subsetString() or None,
            fields=[{"name": f.name(), "type": f.typeName(), "length": f.length(),
                     "precision": f.precision(), "alias": f.alias() or None}
                    for f in layer.fields()],
        )
        if data["format"] == "shp" and path and not Path(path).with_suffix(".cpg").exists():
            warnings.append("Shapefile sans fichier .cpg : vérifier l'encodage des accents.")
    elif isinstance(layer, QgsRasterLayer):
        provider = layer.dataProvider()
        data.update(
            pixel_size=[layer.rasterUnitsPerPixelX(), layer.rasterUnitsPerPixelY()],
            bands=[{"band": b, "name": layer.bandName(b),
                    "data_type": enum_name(provider.dataType(b)),
                    "nodata": clean_number(provider.sourceNoDataValue(b))
                    if provider.sourceHasNoDataValue(b) else None}
                   for b in range(1, layer.bandCount() + 1)],
        )
    return ToolResult(data, warnings)


# QGIS >= 3.36 : Qgis.RasterBandStatistic ; avant : QgsRasterBandStats.All
_ALL_STATS = getattr(Qgis, "RasterBandStatistic", QgsRasterBandStats).All


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Identifiant de la couche raster (layer_id)."),
    "band": Param("integer", "Bande à analyser. Absent : toutes les bandes.",
                  required=False, minimum=1),
    "sample_size": Param("integer", "Nombre de pixels échantillonnés par bande pour les "
                         "statistiques. 0 : tous les pixels (lent sur un gros raster).",
                         required=False, default=250000, minimum=0),
})
def get_raster_info(layer_id: str, band: int | None, sample_size: int) -> ToolResult:
    """Description d'un raster (MNT, orthophoto, NDVI…) : SCR, emprise, taille, résolution,
    puis par bande type de données, nodata, min, max, moyenne et écart-type. Statistiques sur
    un échantillon de pixels par défaut (valeurs approchées) ; sample_size=0 pour un calcul
    exact. Pour vérifier l'ordre des bandes ou la plage de valeurs avant un calcul."""
    layer = get_raster_layer(layer_id)
    if band is not None and band > layer.bandCount():
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"{layer.name()} n'a que {layer.bandCount()} bande(s).")
    result = _info(layer)
    provider = layer.dataProvider()
    sampled = sample_size and layer.width() * layer.height() > sample_size
    bands = [b for b in result.data["bands"] if band is None or b["band"] == band]
    for b in bands:
        st = provider.bandStatistics(b["band"], _ALL_STATS, QgsRectangle(), sample_size)
        b.update(min=clean_number(st.minimumValue), max=clean_number(st.maximumValue),
                 mean=clean_number(st.mean), std_dev=clean_number(st.stdDev),
                 pixel_count=st.elementCount)
    result.data.update(bands=bands, stats_exact=not sampled)
    if sampled:
        result.warnings.append(f"Statistiques estimées sur environ {sample_size} pixels par "
                               "bande : relancer avec sample_size=0 pour des valeurs exactes.")
    return result
