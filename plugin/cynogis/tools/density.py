"""Densité de points par noyau (carte de chaleur) et isoplèthes de concentration."""
from __future__ import annotations

from pathlib import Path

import numpy
from osgeo import gdal, ogr
from qgis.core import (
    Qgis,
    QgsColorRampShader,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsProject,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
)
from qgis.PyQt.QtGui import QColor

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    add_to_memory,
    area_m2,
    area_method,
    distance_area,
    geometry_kind,
    get_vector_layer,
    make_field,
    prepare_expression,
    require_field,
)
from .features import FILTER_HELP
from .geoprocessing import OUTPUT_NAME
from .outputs import Steps, run_in_memory, run_to_project, save_to_project

KERNELS = ("quartic", "triangular", "uniform", "triweight", "epanechnikov")  # ordre QGIS
MAX_CELLS = 25_000_000
# Isoplèthes (part de la densité totale contenue) : de la plus large au noyau.
ISOPLETHS = ((0.95, "#ffffb2"), (0.75, "#fd8d3c"), (0.50, "#bd0026"))


def _isopleths(path: str) -> tuple[list[tuple[float, float, float]], float]:
    """[(part, seuil de densité, surface en ha)] de chaque isoplèthe, et densité maximale.
    Le seuil est la densité au-dessus de laquelle les pixels contiennent cette part du
    total ; la surface est celle de ces pixels."""
    dataset = gdal.Open(path)
    band = dataset.GetRasterBand(1)
    values = band.ReadAsArray().astype("float64").ravel()
    nodata = band.GetNoDataValue()
    if nodata is not None:
        values = values[values != nodata]
    values = numpy.sort(values[values > 0])[::-1]
    _, width, _, _, _, height = dataset.GetGeoTransform()
    pixel_ha = abs(width * height) / 10_000.0
    if not values.size:
        return [], 0.0
    cumulative = numpy.cumsum(values) / values.sum()
    result = []
    for share, _ in ISOPLETHS:
        index = min(int(numpy.searchsorted(cumulative, share)), values.size - 1)
        result.append((share, float(values[index]), round((index + 1) * pixel_ha, 4)))
    return result, float(values[0])


def _isopleth_geometries(path: str, thresholds: list[tuple[float, float, float]]
                         ) -> list[tuple[float, QgsGeometry]]:
    """Polygones emboîtés de chaque isoplèthe : pixels dont la densité atteint son seuil.
    Le raster est classé (1 = 95 %, 2 = 75 %, 3 = 50 %) puis vectorisé par GDAL en mémoire."""
    source = gdal.Open(path)
    values = source.GetRasterBand(1).ReadAsArray().astype("float64")
    classes = numpy.zeros(values.shape, dtype="uint8")
    for number, (_, threshold, _) in enumerate(thresholds, start=1):
        classes[values >= threshold] = number
    raster = gdal.GetDriverByName("MEM").Create("", source.RasterXSize, source.RasterYSize, 1,
                                                gdal.GDT_Byte)
    raster.SetGeoTransform(source.GetGeoTransform())
    raster.SetProjection(source.GetProjection())
    band = raster.GetRasterBand(1)
    band.WriteArray(classes)
    band.SetNoDataValue(0)
    driver = ogr.GetDriverByName("MEM")  # vecteur depuis GDAL 3.11, « Memory » avant
    if driver is None or driver.GetMetadataItem(gdal.DCAP_VECTOR) != "YES":
        driver = ogr.GetDriverByName("Memory")
    vectors = driver.CreateDataSource("")
    layer = vectors.CreateLayer("iso")
    layer.CreateField(ogr.FieldDefn("classe", ogr.OFTInteger))
    gdal.Polygonize(band, band, layer, 0)
    parts: dict[int, list[QgsGeometry]] = {}
    for feature in layer:
        geometry = QgsGeometry()
        geometry.fromWkb(feature.GetGeometryRef().ExportToWkb())
        parts.setdefault(feature.GetField("classe"), []).append(geometry)
    result = []
    for number, (share, _, _) in enumerate(thresholds, start=1):
        pieces = [g for c, items in parts.items() if c >= number for g in items]
        if pieces:
            result.append((share, QgsGeometry.unaryUnion(pieces)))
    return result


def _save_isopleths(raster_layer, path: str, thresholds: list[tuple[float, float, float]],
                    name: str) -> ToolResult:
    fields = QgsFields()
    for spec in (("isoplethe", "integer", 0), ("libelle", "string", 40),
                 ("seuil", "real", 0), ("surface_ha", "real", 0)):
        fields.append(make_field(*spec))
    crs = raster_layer.crs()
    memory = QgsMemoryProviderUtils.createMemoryLayer("isoplethes", fields,
                                                      Qgis.WkbType.MultiPolygon, crs)
    da = distance_area(crs)
    features = []
    limits = {share: threshold for share, threshold, _ in thresholds}
    for share, geometry in _isopleth_geometries(path, thresholds):
        geometry.convertToMultiType()
        feature = QgsFeature(fields)
        feature.setGeometry(geometry)
        label = f"{share * 100:.0f} % de la densité" + (" (noyau)" if share == 0.5 else "")
        feature.setAttributes([round(share * 100), label, round(limits[share], 6),
                               round(area_m2(da, geometry) / 10_000.0, 4)])
        features.append(feature)
    notes = add_to_memory(memory, features)
    result = save_to_project(memory, name)
    result.warnings.extend(notes)
    return result


def _style(layer, thresholds: list[tuple[float, float, float]], maximum: float) -> None:
    """Classes discrètes : hors isoplèthe 95 % transparent, puis 95 %, 75 %, 50 % (noyau).
    Une classe discrète couvre les valeurs <= sa borne : chaque borne est juste sous le seuil
    de l'isoplèthe suivante."""
    below = [float(numpy.nextafter(t, 0)) for _, t, _ in thresholds] + [maximum]
    colors = [QColor(0, 0, 0, 0)] + [QColor(color) for _, color in ISOPLETHS]
    labels = ["Hors isoplèthe 95 %"] + [f"{share * 100:.0f} % de la densité"
                                        for share, _ in ISOPLETHS]
    labels[-1] += " (noyau)"
    ramp = QgsColorRampShader(0, maximum, None, QgsColorRampShader.Type.Discrete)
    ramp.setColorRampItemList([QgsColorRampShader.ColorRampItem(bound, color, label)
                               for bound, color, label in zip(below, colors, labels,
                                                              strict=True)])
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(ramp)
    layer.setRenderer(QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader))
    layer.setOpacity(0.8)
    layer.triggerRepaint()


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche de points (layer_id), en SCR projeté : observations, "
                      "contacts de chiroptères, points d'écoute…"),
    "radius_m": Param("number", "Rayon de lissage (m) : distance d'influence d'un point. "
                      "Plus grand = zones plus lisses et étendues.", required=False,
                      default=250, minimum=1, maximum=50000),
    "pixel_size_m": Param("number", "Taille des pixels (m). Défaut : rayon / 10.",
                          required=False, minimum=0.5),
    "weight_field": Param("string", "Champ de poids des points (ex. effectif, nombre de "
                          "contacts).", required=False),
    "kernel": Param("string", "Forme du noyau.", required=False, default="quartic",
                    enum=KERNELS),
    "filter_expression": Param("string", "Points retenus, ex. \"groupe\" = 'Chiroptères'. "
                               + FILTER_HELP, required=False),
    "isopleth_polygons": Param("boolean", "Produire aussi les isoplèthes en polygones "
                               "emboîtés (à croiser avec habitats ou enjeux).", required=False,
                               default=True),
    "output_name": OUTPUT_NAME,
})
def kernel_density_points(layer_id: str, radius_m: float, pixel_size_m: float | None,
                          weight_field: str | None, kernel: str, filter_expression: str | None,
                          isopleth_polygons: bool, output_name: str | None) -> Steps:
    """Carte de densité (noyau) d'observations : raster .tif dans mcp_outputs/, stylé par
    isoplèthes (part de la densité totale : 95 %, 75 %, 50 % = noyau de concentration),
    avec la surface et le seuil de chaque isoplèthe ; avec isopleth_polygons, couche de
    polygones emboîtés (isoplethe, libelle, seuil, surface_ha) à croiser avec les habitats
    (overlay) ou les enjeux. Valeurs du raster : densité relative (somme pondérée des
    noyaux), à comparer entre zones d'une même carte."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "point":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "points.")
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{layer.name()} est en degrés : "
                        "reprojette-la (reproject_layer) pour un rayon en mètres.")
    weight_field = require_field(layer, weight_field) if weight_field else None
    source = layer
    if filter_expression:
        prepare_expression(filter_expression, layer, "filter_expression")
        source = (yield from run_in_memory("native:extractbyexpression",
                                           {"INPUT": layer, "EXPRESSION": filter_expression}))
    count = source.featureCount()
    if count < 2:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{count} point(s) retenu(s) : au moins 2 "
                        "nécessaires.")
    pixel = float(pixel_size_m or max(radius_m / 10.0, 1.0))
    extent = source.extent()
    cells = ((extent.width() + 2 * radius_m) / pixel) * ((extent.height() + 2 * radius_m) / pixel)
    if cells > MAX_CELLS:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Raster de {cells:,.0f} pixels : augmente "
                        "pixel_size_m ou filtre les points.".replace(",", " "))

    result = (yield from run_to_project("native:heatmapkerneldensityestimation", {
        "INPUT": source, "RADIUS": float(radius_m), "PIXEL_SIZE": pixel,
        "WEIGHT_FIELD": weight_field, "KERNEL": KERNELS.index(kernel), "OUTPUT_VALUE": 0,
    }, output_name or f"densite_{layer.name()}"))
    base = Path(result.data["outputs"][0]["path"]).stem
    output = result.data["outputs"][0]
    thresholds, maximum = _isopleths(output["path"])
    raster = QgsProject.instance().mapLayer(output["layer_id"])
    if thresholds and raster is not None:
        _style(raster, thresholds, maximum)
        if isopleth_polygons:
            polygons = _save_isopleths(raster, output["path"], thresholds,
                                       f"{base}_isoplethes")
            result.data["isopleth_layer"] = polygons.data["outputs"][0]
            result.outputs.extend(polygons.outputs)
            result.warnings.extend(w for w in polygons.warnings if w not in result.warnings)
    result.data.update({
        "points": count, "radius_m": float(radius_m), "pixel_size_m": pixel, "kernel": kernel,
        "weight_field": weight_field, "max_density": round(maximum, 6),
        "area_method": area_method(distance_area(layer.crs(), "planar")) + ", par pixels",
        "isopleths": [{"share": f"{share * 100:.0f} %", "min_density": round(t, 6),
                       "area_ha": area}
                      for share, t, area in thresholds],
    })
    if not thresholds:
        result.warnings.append("Densité nulle partout : vérifie les points et le rayon.")
    return result
