"""Import de relevés de terrain (GPX, CSV, KoboToolbox, QField) en couche de points standard."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)

from ..core import fielddata
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.fields import RESERVED_FIELDS, unique_field_name
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.territory import detect_territory
from .common import crs_from_text, geometry_kind, make_field, to_json_value
from .geoprocessing import OUTPUT_NAME
from .outputs import save_to_project

WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")
TABLE_SUFFIXES = (".csv", ".txt")


def _read(path: str, layer_name: str | None) -> tuple[list[str], list[tuple[dict, Any]], Any]:
    """Colonnes, [(attributs, géométrie ponctuelle ou None)], SCR des géométries."""
    if path.lower().endswith(TABLE_SUFFIXES):
        columns, rows = fielddata.read_csv(path)
        return columns, [(row, None) for row in rows], None
    if path.lower().endswith(".gpx"):
        layer_name = layer_name or "waypoints"
    uri = f"{path}|layername={layer_name}" if layer_name else path
    layer = QgsVectorLayer(uri, "terrain", "ogr")
    if not layer.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Lecture impossible : {uri} (format ou "
                        "layer_name incorrect ?)")
    points = geometry_kind(layer) == "point"
    columns = layer.fields().names()
    rows = []
    for feature in layer.getFeatures():
        geometry = feature.geometry()
        keep = points and not (geometry.isNull() or geometry.isEmpty())
        rows.append(({name: to_json_value(feature[name]) for name in columns},
                     QgsGeometry(geometry) if keep else None))
    return columns, rows, layer.crs() if points else None


@tool(level=Level.CREATE, params={
    "path": Param("string", "Fichier de relevés : .gpx, .csv, .xlsx (export KoboToolbox), "
                  ".gpkg (QField), .geojson, .shp."),
    "mapping": Param("object", 'Champ standard → colonne source, complète la détection '
                     'automatique, ex. {"taxon": "nom_espece", "lat": "Y", "lon": "X"}. Clés : '
                     'date_obs, observ, taxon, effectif, precis_m, lat, lon.', required=False),
    "layer_name": Param("string", "Sous-couche à lire (.gpkg QField, .xlsx ; .gpx : waypoints "
                        "par défaut, ou track_points).", required=False),
    "source_crs": Param("string", "SCR des colonnes de coordonnées (lat/lon).",
                        required=False, default="EPSG:4326"),
    "target_crs": Param("string", "SCR de la couche produite. Défaut : SCR de référence du "
                        "territoire détecté.", required=False),
    "max_precision_m": Param("number", "Précision GPS au-delà de laquelle un point est "
                             "signalé (m).", required=False, default=10, minimum=0),
    "output_name": OUTPUT_NAME,
})
def import_field_data(path: str, mapping: dict | None, layer_name: str | None, source_crs: str,
                      target_crs: str | None, max_precision_m: float,
                      output_name: str | None) -> ToolResult:
    """Importe des relevés de terrain en couche de points standardisée : date_obs (ISO),
    observ, taxon, effectif, precis_m (m), source (fichier) puis les autres colonnes du
    fichier. Colonnes reconnues automatiquement (synonymes, colonnes GPS KoboToolbox) :
    vérifie column_mapping dans la réponse et corrige avec mapping si besoin."""
    if not os.path.isfile(path):
        raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Fichier introuvable : {path}")
    columns, rows, geometry_crs = _read(path, layer_name)
    if not rows:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Aucune ligne lue dans {path}.")
    used = {**fielddata.suggest_columns(columns), **(mapping or {})}
    unknown = sorted(set(used.values()) - set(columns))
    invalid_keys = sorted(set(used) - {n for n, _ in fielddata.STANDARD_FIELDS}
                          - set(fielddata.COORDINATES))
    if unknown or invalid_keys:
        raise ToolError(ErrorCode.INVALID_PARAMS, "mapping incorrect.",
                        {"unknown_columns": unknown, "unknown_keys": invalid_keys,
                         "columns": columns})
    if geometry_crs is None and not {"lat", "lon"} <= set(used):
        raise ToolError(ErrorCode.INVALID_PARAMS, "Colonnes de coordonnées non trouvées : "
                        "indique mapping.lat et mapping.lon.", {"columns": columns})
    coord_crs = geometry_crs or crs_from_text(source_crs)

    # Géométries en WGS84 d'abord : sert à détecter le territoire.
    to_wgs84 = QgsCoordinateTransform(coord_crs, WGS84, QgsProject.instance())
    records, problems = [], {}
    skipped = 0
    for record, geometry in rows:
        values, bad = fielddata.standardize(record, used)
        for name in bad:
            problems[name] = problems.get(name, 0) + 1
        if geometry is None:
            if values.get("lon") is None or values.get("lat") is None:
                skipped += 1
                continue
            geometry = QgsGeometry.fromPointXY(QgsPointXY(values["lon"], values["lat"]))
        try:
            geometry.transform(to_wgs84)
        except QgsCsException:
            skipped += 1
            continue
        records.append((record, values, geometry))
    if not records:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucun point localisable : vérifie les "
                        "colonnes lat/lon et source_crs.", {"mapping": used})

    if target_crs is None:
        box = QgsGeometry.collectGeometry([g for _, _, g in records]).boundingBox()
        territory = detect_territory([box.xMinimum(), box.yMinimum(), box.xMaximum(),
                                      box.yMaximum()])
        target_crs = territory.epsg if territory else "EPSG:4326"
    crs = crs_from_text(target_crs)

    fields = QgsFields()
    for name, type_name in fielddata.STANDARD_FIELDS:
        fields.append(make_field(name, type_name))
    fields.append(make_field("source", "string", 254))
    mapped = set(used.values())
    extras: dict[str, str] = {}
    for column in columns:  # colonnes vides partout (GPX) et identifiants techniques : écartées
        if column not in mapped and column.lower() not in RESERVED_FIELDS and any(
                record.get(column) not in (None, "") for record, _, _ in records):
            extras[column] = unique_field_name(column, fields.names())
            fields.append(make_field(extras[column], "string"))
    memory = QgsMemoryProviderUtils.createMemoryLayer("terrain", fields, Qgis.WkbType.Point, crs)
    to_target = QgsCoordinateTransform(WGS84, crs, QgsProject.instance())
    source = Path(path).name
    features, imprecise = [], 0
    for record, values, geometry in records:
        geometry.transform(to_target)
        feature = QgsFeature(fields)
        feature.setGeometry(geometry)
        for name, _ in fielddata.STANDARD_FIELDS:
            feature[name] = values.get(name)
        feature["source"] = source
        for column, name in extras.items():
            value = record.get(column)
            feature[name] = None if value in (None, "") else str(value)
        if (values.get("precis_m") or 0) > max_precision_m:
            imprecise += 1
        features.append(feature)
    if not memory.dataProvider().addFeatures(features):
        raise ToolError(ErrorCode.INTERNAL_ERROR, "Création des points impossible.",
                        {"error": memory.dataProvider().lastError()})

    result = save_to_project(memory, output_name or f"terrain_{Path(path).stem}")
    missing = [n for n, _ in fielddata.STANDARD_FIELDS if n not in used]
    result.data.update({
        "source": path, "rows_read": len(rows), "imported": len(features),
        "column_mapping": used, "extra_fields": extras, "crs": crs.authid(),
        "preview": [{n: f[n] for n, _ in fielddata.STANDARD_FIELDS} for f in features[:3]],
    })
    if crs.authid() == "EPSG:4326" and target_crs == "EPSG:4326":
        result.warnings.append("Territoire non détecté : couche laissée en EPSG:4326, "
                               "précise target_crs.")
    if missing:
        result.warnings.append(f"Champs standard non trouvés (laissés vides) : "
                               f"{', '.join(missing)}. Indique-les dans mapping si la colonne "
                               "existe.")
    if skipped:
        result.warnings.append(f"{skipped} ligne(s) sans coordonnées valides ignorée(s).")
    for name, count in problems.items():
        result.warnings.append(f"{count} valeur(s) illisible(s) pour {name} (laissées vides).")
    if imprecise:
        result.warnings.append(f"{imprecise} point(s) avec une précision GPS au-delà de "
                               f"{max_precision_m:g} m.")
    return result
