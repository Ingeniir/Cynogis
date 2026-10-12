"""Dérivés du modèle numérique de terrain : pente, exposition, ombrage, classes de pente."""
from __future__ import annotations

import math

import numpy
from osgeo import gdal, ogr
from qgis.core import QgsFeature, QgsFields, QgsMemoryProviderUtils

from ..core import terrain as relief
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.fields import unique_field_name
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    add_to_memory,
    feature_request,
    geometry_kind,
    get_raster_layer,
    get_vector_layer,
    iter_geometries,
    make_field,
)
from .geoprocessing import OUTPUT_NAME
from .outputs import run_to_project, save_to_project

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


# --- Échantillonnage du MNT -------------------------------------------------
MAX_WINDOW_PIXELS = 60_000_000
SECTORS = tuple(name for name, _, _ in relief.ASPECT_SECTORS)  # N, NE, … dans l'ordre
POINT_FIELDS = (("alt_m", "real"), ("pente_deg", "real"), ("pente_pct", "real"),
                ("pente_cl", "string"), ("expo_deg", "real"), ("expo_sect", "string"))
POLYGON_FIELDS = (("alt_moy", "real"), ("alt_min", "real"), ("alt_max", "real"),
                  ("pente_deg", "real"), ("pente_pct", "real"), ("pente_cl", "string"),
                  ("expo_dom", "string"), ("plat_pct", "real"), ("n_pixels", "integer"))


def _read_window(dem, geometries) -> tuple[numpy.ndarray, tuple, int, int]:
    """MNT (float64, NaN hors données) sur l'emprise des géométries + 2 pixels, géotransformée
    de la fenêtre et sa position dans le raster."""
    dataset = gdal.Open(dem.dataProvider().dataSourceUri().split("|")[0])
    if dataset is None:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{dem.name()} n'est pas lisible par GDAL "
                        "(MNT local attendu : GeoTIFF, VRT…).")
    x0, width, _, y0, _, height = dataset.GetGeoTransform()
    box = geometries[0].boundingBox()
    for geometry in geometries[1:]:
        box.combineExtentWith(geometry.boundingBox())
    col0 = max(math.floor((box.xMinimum() - x0) / width) - 2, 0)
    col1 = min(math.ceil((box.xMaximum() - x0) / width) + 2, dataset.RasterXSize)
    row0 = max(math.floor((box.yMaximum() - y0) / height) - 2, 0)
    row1 = min(math.ceil((box.yMinimum() - y0) / height) + 2, dataset.RasterYSize)
    if col1 <= col0 or row1 <= row0:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"La couche est hors de l'emprise de "
                        f"{dem.name()}.")
    if (col1 - col0) * (row1 - row0) > MAX_WINDOW_PIXELS:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Emprise trop grande pour la résolution du "
                        "MNT : traite la couche par secteurs (filtre) ou rééchantillonne le "
                        "MNT.")
    band = dataset.GetRasterBand(1)
    values = band.ReadAsArray(col0, row0, col1 - col0, row1 - row0).astype("float64")
    nodata = band.GetNoDataValue()
    if nodata is not None:
        values[values == nodata] = numpy.nan
    transform = (x0 + col0 * width, width, 0.0, y0 + row0 * height, 0.0, height)
    return values, transform, col1 - col0, row1 - row0


def _slope_aspect(z: numpy.ndarray, dx: float, dy: float):
    """Pente (degrés) et exposition (degrés depuis le nord, -1 si plat) par la méthode de
    Horn (fenêtre de 3 pixels sur 3), comme native:slope et native:aspect de QGIS."""
    p = numpy.pad(z, 1, mode="edge")
    a, b, c = p[:-2, :-2], p[:-2, 1:-1], p[:-2, 2:]
    d, f = p[1:-1, :-2], p[1:-1, 2:]
    g, h, i = p[2:, :-2], p[2:, 1:-1], p[2:, 2:]
    east = ((c + 2 * f + i) - (a + 2 * d + g)) / (8 * dx)   # dz/dx, vers l'est
    north = ((a + 2 * b + c) - (g + 2 * h + i)) / (8 * dy)  # dz/dy, vers le nord
    slope = numpy.degrees(numpy.arctan(numpy.hypot(east, north)))
    aspect = numpy.degrees(numpy.arctan2(-east, -north)) % 360.0  # sens de la descente
    aspect[(east == 0) & (north == 0)] = -1.0
    return slope, aspect


def _sector_index(aspect: numpy.ndarray) -> numpy.ndarray:
    return (((aspect + 22.5) % 360.0) // 45.0).astype("int64")


def _clean(value) -> float | None:
    return None if value is None or not numpy.isfinite(value) else round(float(value), 2)


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Points ou polygones à renseigner (layer_id) : relevés, "
                      "habitats, parcelles…"),
    "dem_layer_id": Param("string", "MNT raster (layer_id), ex. RGE ALTI, en SCR métrique "
                          "(EPSG:2975, EPSG:4471)."),
    "altitude_bands": Param("array", 'Tranches d\'altitude à attribuer (champ alt_classe), '
                            'ex. [{"max": 400, "label": "Étage littoral et bas"}, {"max": '
                            '1100, "label": "Étage mégatherme"}, {"label": "Au-delà"}] ; max '
                            "exclu, dernière tranche sans max. Les limites des étages varient "
                            "entre côte au vent et sous le vent : les faire valider.",
                            required=False, items="object"),
    "flat_slope_deg": Param("number", "Polygones : pente sous laquelle un pixel est plat "
                            "(exclu de l'exposition dominante).", required=False, default=2,
                            minimum=0, maximum=45),
    "output_name": OUTPUT_NAME,
})
def elevation_sample(layer_id: str, dem_layer_id: str, altitude_bands: list | None,
                     flat_slope_deg: float, output_name: str | None) -> ToolResult:
    """Copie de la couche enrichie par le MNT. Points : alt_m, pente_deg, pente_pct,
    pente_cl (classe d'aménagement), expo_deg, expo_sect (N, NE…, vide si plat). Polygones :
    alt_moy, alt_min, alt_max, pente_deg et pente_pct (moyennes), pente_cl, expo_dom
    (exposition dominante des pixels non plats), plat_pct, n_pixels ; un polygone plus petit
    qu'un pixel reçoit la valeur de son centre. Avec altitude_bands : alt_classe."""
    layer = get_vector_layer(layer_id)
    kind = geometry_kind(layer)
    if kind not in ("point", "polygon"):
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} doit contenir des points ou "
                        "des polygones.")
    dem = _metric_raster(dem_layer_id)
    try:
        bands = relief.parse_bands(altitude_bands)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    items = list(iter_geometries(layer, feature_request(layer), dem.crs()))
    if not items:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucune "
                        "géométrie.")
    z, transform, cols, rows = _read_window(dem, [g for _, g in items])
    x0, width, _, y0, _, height = transform
    slope, aspect = _slope_aspect(z, abs(width), abs(height))

    def pixel(x: float, y: float) -> tuple[int, int] | None:
        col, row = int((x - x0) // width), int((y - y0) // height)
        return (row, col) if 0 <= row < rows and 0 <= col < cols else None

    def at(cell) -> tuple:
        if cell is None or not numpy.isfinite(z[cell]):
            return None, None, None
        return z[cell], slope[cell], aspect[cell]

    labels = None
    if kind == "polygon":  # chaque pixel reçoit le n° du polygone qui le contient
        raster = gdal.GetDriverByName("MEM").Create("", cols, rows, 1, gdal.GDT_Int32)
        raster.SetGeoTransform(transform)
        raster.GetRasterBand(1).Fill(-1)
        driver = ogr.GetDriverByName("MEM")
        if driver is None or driver.GetMetadataItem(gdal.DCAP_VECTOR) != "YES":
            driver = ogr.GetDriverByName("Memory")
        source = driver.CreateDataSource("")
        vectors = source.CreateLayer("p")
        vectors.CreateField(ogr.FieldDefn("idx", ogr.OFTInteger))
        for index, (_, geometry) in enumerate(items):
            feature = ogr.Feature(vectors.GetLayerDefn())
            feature.SetField("idx", index)
            feature.SetGeometry(ogr.CreateGeometryFromWkb(bytes(geometry.asWkb())))
            vectors.CreateFeature(feature)
        gdal.RasterizeLayer(raster, [1], vectors, options=["ATTRIBUTE=idx"])
        flat_labels = raster.GetRasterBand(1).ReadAsArray().ravel()
        order = numpy.argsort(flat_labels, kind="stable")
        sorted_labels = flat_labels[order]
        labels = (order, sorted_labels)

    specs = POINT_FIELDS if kind == "point" else POLYGON_FIELDS
    specs = specs + ((("alt_classe", "string"),) if bands else ())
    fields = QgsFields(layer.fields())
    added = []
    for name, type_name in specs:
        added.append(unique_field_name(name, fields.names()))
        fields.append(make_field(added[-1], type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("mnt", fields, layer.wkbType(),
                                                      layer.crs())
    out, missing, centroid_used = [], 0, 0
    z_flat, slope_flat, aspect_flat = z.ravel(), slope.ravel(), aspect.ravel()
    for index, (feature, geometry) in enumerate(items):
        if kind == "point":
            point = geometry.asPoint() if not geometry.isMultipart() else \
                geometry.asMultiPoint()[0]
            alt, slp, asp = at(pixel(point.x(), point.y()))
            if slp is not None and not numpy.isfinite(slp):  # voisin sans donnée
                slp = asp = None
            pct = None if slp is None else relief.degrees_to_percent(slp)
            cls = relief.slope_class(pct) if pct is not None else None
            values = [_clean(alt), _clean(slp), _clean(pct), cls.label if cls else None,
                      _clean(asp) if asp is not None and asp >= 0 else None,
                      relief.aspect_sector(asp) if asp is not None else None]
            reference = alt
        else:
            order, sorted_labels = labels
            start, end = numpy.searchsorted(sorted_labels, [index, index + 1])
            cells = order[start:end]
            cells = cells[numpy.isfinite(z_flat[cells])]
            if not cells.size:  # polygone plus petit qu'un pixel : valeur au centre
                center = geometry.centroid().asPoint()
                cell = pixel(center.x(), center.y())
                if cell is not None and numpy.isfinite(z[cell]):
                    cells = numpy.array([cell[0] * cols + cell[1]])
                    centroid_used += 1
            if cells.size:
                alts, slopes, aspects = z_flat[cells], slope_flat[cells], aspect_flat[cells]
                valid = numpy.isfinite(slopes)  # pente inconnue au bord d'un trou du MNT
                mean_slope = float(slopes[valid].mean()) if valid.any() else math.nan
                pct = relief.degrees_to_percent(mean_slope) if valid.any() else None
                cls = relief.slope_class(pct) if pct is not None else None
                sloped = aspects[valid & (slopes >= flat_slope_deg) & (aspects >= 0)]
                counts = numpy.bincount(_sector_index(sloped), minlength=8)
                values = [_clean(alts.mean()), _clean(alts.min()), _clean(alts.max()),
                          _clean(mean_slope), _clean(pct), cls.label if cls else None,
                          SECTORS[int(counts.argmax())] if sloped.size else None,
                          _clean(100.0 * (1 - sloped.size / valid.sum()))
                          if valid.any() else None, int(cells.size)]
                reference = float(alts.mean())
            else:
                values = [None] * len(POLYGON_FIELDS)
                reference = None
        if reference is None:
            missing += 1
        if bands:
            values.append(relief.altitude_band(reference, bands))
        copy = QgsFeature(fields)
        copy.setGeometry(feature.geometry())
        copy.setAttributes([*feature.attributes(), *values])
        out.append(copy)
    notes = add_to_memory(memory, out)

    result = save_to_project(memory, output_name or f"{layer.name()}_mnt")
    result.warnings.extend(notes)
    altitudes = [v for v in (f[added[0]] for f in out) if v is not None]
    result.data.update({
        "dem": dem.name(), "pixel_size_m": round(abs(width), 3), "features": len(out),
        "fields": added, "altitude_min": min(altitudes, default=None),
        "altitude_max": max(altitudes, default=None),
    })
    if bands:
        counts: dict[str, int] = {}
        for f in out:
            key = str(f[added[-1]])
            counts[key] = counts.get(key, 0) + 1
        result.data["altitude_classes"] = counts
    if missing:
        result.warnings.append(f"{missing} entité(s) hors du MNT ou sur des pixels sans "
                               "donnée : champs vides.")
    if centroid_used:
        result.warnings.append(f"{centroid_used} polygone(s) plus petit(s) qu'un pixel : "
                               "valeurs prises au centre.")
    return result

