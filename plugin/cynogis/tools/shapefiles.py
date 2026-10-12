"""Prise en charge du format Shapefile : audit, chargement, encodage, export."""
from __future__ import annotations

import os

from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsFields,
    QgsMemoryProviderUtils,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.fields import FIELD_TYPES, unique_field_name
from ..core.naming import clean_name, unique_path
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.shapefile import (
    COMMON_ENCODINGS,
    export_plan,
    looks_like_mojibake,
    sidecar_messages,
    sidecar_report,
    size_messages,
)
from ..core.territory import detect_territory
from .common import (
    crs_from_text,
    extent_wgs84,
    geometry_kind,
    get_vector_layer,
    layer_field_types,
    make_field,
    rect_to_list,
    refresh_layer,
)
from .outputs import add_to_group, output_dir, save_to_project

FORMATS = {"gpkg": ("GPKG", ".gpkg"), "shp": ("ESRI Shapefile", ".shp"),
           "geojson": ("GeoJSON", ".geojson"), "csv": ("CSV", ".csv")}
SAMPLE_FEATURES = 50


def _scan_sidecars(shp_path: str) -> tuple[list[str], dict[str, int]]:
    """Extensions et tailles des fichiers qui partagent le nom du .shp."""
    folder = os.path.dirname(shp_path) or "."
    base = os.path.splitext(os.path.basename(shp_path))[0].lower()
    sizes: dict[str, int] = {}
    for entry in os.listdir(folder):
        name, extension = os.path.splitext(entry)
        if name.lower() == base:
            sizes[extension.lower()] = os.path.getsize(os.path.join(folder, entry))
    return list(sizes), sizes


def _text_sample(layer: QgsVectorLayer) -> list[str]:
    sample: list[str] = []
    for index, feature in enumerate(layer.getFeatures()):
        sample.extend(v for v in feature.attributes() if isinstance(v, str))
        if index >= SAMPLE_FEATURES:
            break
    return sample


def _mojibake_hint() -> str:
    return ("Accents mal lus : encodage déclaré probablement faux. Essaie set_layer_encoding "
            f"avec {', '.join(COMMON_ENCODINGS[:3])}.")


@tool(level=Level.READ, params={
    "path": Param("string", "Chemin complet du fichier .shp."),
})
def check_shapefile(path: str) -> ToolResult:
    """Audit d'un shapefile avant usage : fichiers compagnons (.shx, .dbf obligatoires ; .prj,
    .cpg recommandés), limite des 2 Go, SCR, accents mal encodés, noms de champs tronqués."""
    if not path.lower().endswith(".shp"):
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique le chemin du fichier .shp lui-même.")
    if not os.path.isfile(path):
        raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Fichier introuvable : {path}")
    extensions, sizes = _scan_sidecars(path)
    report = sidecar_report(extensions)
    warnings = sidecar_messages(report) + size_messages(sizes)
    data = {"path": path, "sidecars": report.to_dict(), "size_bytes": sum(sizes.values())}

    layer = QgsVectorLayer(path, os.path.basename(path), "ogr")
    if not layer.isValid():
        warnings.append("Fichier illisible par QGIS.")
        return ToolResult({**data, "readable": False}, warnings)
    fields = layer.fields().names()
    data.update({"readable": True, "feature_count": layer.featureCount(),
                 "geometry_type": geometry_kind(layer), "crs": layer.crs().authid() or None,
                 "encoding": layer.dataProvider().encoding(), "fields": fields})
    if not layer.crs().isValid():
        warnings.append("SCR inconnu : déclare-le (load_layer, paramètre crs) avant toute mesure.")
    elif layer.crs().isGeographic():
        territory = detect_territory(rect_to_list(extent_wgs84(layer)))
        target = f" vers {territory.epsg}" if territory else ""
        warnings.append(f"Couche en degrés : reprojette{target} avant toute mesure métrique.")
    if looks_like_mojibake(_text_sample(layer)):
        warnings.append(_mojibake_hint())
    truncated = [name for name in fields if len(name) == 10]
    if truncated:
        warnings.append(f"{len(truncated)} nom(s) de champ de 10 caractères, peut-être tronqués "
                        f"par un export antérieur : {', '.join(truncated[:10])}.")
    return ToolResult(data, warnings)


@tool(level=Level.CREATE, params={
    "path": Param("string", "Chemin du fichier vecteur (.shp, .gpkg, .geojson…)."),
    "name": Param("string", "Nom de la couche dans le projet (défaut : nom du fichier).",
                  required=False),
    "encoding": Param("string", "Encodage des textes si les accents sont mal lus.",
                      required=False, enum=COMMON_ENCODINGS),
    "crs": Param("string", "SCR à déclarer si le .prj est absent, ex. EPSG:2975 (Réunion), "
                 "EPSG:4471 (Mayotte). Ne transforme pas les coordonnées.", required=False),
})
def load_layer(path: str, name: str | None, encoding: str | None, crs: str | None) -> ToolResult:
    """Ajoute un fichier vecteur au projet (groupe « Cynogis »). Rien n'est copié ni modifié :
    la couche pointe vers le fichier. Pour un shapefile, lance check_shapefile avant."""
    if not os.path.isfile(path):
        raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Fichier introuvable : {path}")
    layer = QgsVectorLayer(path, name or os.path.splitext(os.path.basename(path))[0], "ogr")
    if not layer.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS, f"QGIS ne parvient pas à lire : {path}")
    warnings: list[str] = []
    if encoding:
        layer.setProviderEncoding(encoding)
    if crs:
        layer.setCrs(crs_from_text(crs))
        warnings.append(f"SCR déclaré {crs} sans transformation des coordonnées : vérifie la "
                        "superposition avec les autres couches.")
    elif not layer.crs().isValid():
        warnings.append("SCR inconnu : recharge la couche avec le paramètre crs.")
    if looks_like_mojibake(_text_sample(layer)):
        warnings.append(_mojibake_hint())
    add_to_group(layer)
    return ToolResult({"layer_id": layer.id(), "name": layer.name(), "path": path,
                       "crs": layer.crs().authid() or None, "geometry_type": geometry_kind(layer),
                       "feature_count": layer.featureCount(), "fields": layer.fields().names(),
                       "encoding": layer.dataProvider().encoding()}, warnings)


_WKB_TYPES = {"point": Qgis.WkbType.Point, "multipoint": Qgis.WkbType.MultiPoint,
              "line": Qgis.WkbType.MultiLineString, "polygon": Qgis.WkbType.MultiPolygon,
              "none": Qgis.WkbType.NoGeometry}


@tool(level=Level.CREATE, params={
    "output_name": Param("string", "Nom de la nouvelle couche (et du GeoPackage)."),
    "geometry_type": Param("string", "Géométrie : point, multipoint, line, polygon (multi-"
                           "parties acceptées) ou none (table sans géométrie).",
                           enum=tuple(_WKB_TYPES)),
    "crs": Param("string", "SCR, ex. EPSG:2975 (Réunion), EPSG:4471 (Mayotte). Défaut : SCR "
                 "du projet.", required=False),
    "fields": Param("array", 'Champs : [{"name": "nom", "type": "string", "length": 50, '
                    f'"precision": 0}}]. Types : {", ".join(FIELD_TYPES)}. length et precision '
                    "facultatifs.", required=False, items="object"),
})
def create_layer(output_name: str, geometry_type: str, crs: str | None,
                 fields: list[dict] | None) -> ToolResult:
    """Crée une couche vide (GeoPackage neuf dans mcp_outputs/, groupe « Cynogis ») avec les
    champs demandés, prête à recevoir des entités (add_features) : relevé à numériser,
    couche de travail, table de suivi. Noms de champs nettoyés et rendus uniques."""
    target_crs = crs_from_text(crs) if crs else QgsProject.instance().crs()
    if geometry_type != "none" and not target_crs.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS, "Projet sans SCR : précise crs.")
    qfields = QgsFields()
    renamed = []
    for spec in fields or []:
        if not isinstance(spec, dict) or not spec.get("name") or not spec.get("type"):
            raise ToolError(ErrorCode.INVALID_PARAMS,
                            f"Champ mal décrit : {spec!r} (name et type obligatoires).")
        name = unique_field_name(spec["name"], qfields.names())
        if name != spec["name"]:
            renamed.append(f"{spec['name']} → {name}")
        qfields.append(make_field(name, spec["type"], spec.get("length") or 0,
                                  spec.get("precision") or 0))
    memory = QgsMemoryProviderUtils.createMemoryLayer(output_name, qfields,
                                                      _WKB_TYPES[geometry_type], target_crs)
    result = save_to_project(memory, output_name)
    result.warnings = [w for w in result.warnings if not w.endswith("est vide.")]
    if renamed:
        result.warnings.append("Champs renommés : " + ", ".join(renamed) + ".")
    if geometry_type != "none" and target_crs.isGeographic():
        result.warnings.append(f"SCR géographique ({target_crs.authid()}) : préfère EPSG:2975 "
                               "ou EPSG:4471 pour mesurer en mètres.")
    result.data.update(geometry_type=geometry_type, crs=target_crs.authid() or None,
                       fields=qfields.names())
    return result


@tool(level=Level.MODIFY, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "encoding": Param("string", "Encodage de lecture des textes.", enum=COMMON_ENCODINGS),
})
def set_layer_encoding(layer_id: str, encoding: str) -> ToolResult:
    """Change l'encodage de lecture d'une couche (accents mal affichés d'un shapefile). Le
    fichier n'est pas modifié : seule la lecture change."""
    layer = get_vector_layer(layer_id)
    if layer.isEditable() and layer.isModified():
        raise ToolError(ErrorCode.PENDING_EDITS, f"« {layer.name()} » a des modifications non "
                        "enregistrées : request_commit ou rollback_edits d'abord.")
    before = layer.dataProvider().encoding()
    layer.setProviderEncoding(encoding)
    refresh_layer(layer)
    sample = _text_sample(layer)
    warnings = (["Accents toujours incorrects : essaie un autre encodage."]
                if looks_like_mojibake(sample) else [])
    return ToolResult({"layer": layer.name(), "encoding_before": before,
                       "encoding_after": encoding, "sample": sample[:5]}, warnings)


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur à exporter (layer_id)."),
    "format": Param("string", "Format du fichier produit.", required=False, default="gpkg",
                    enum=tuple(FORMATS)),
    "output_name": Param("string", "Nom du fichier produit (nettoyé, jamais écrasé). Défaut : "
                         "nom de la couche.", required=False),
    "target_crs": Param("string", "Reprojeter à l'export, ex. EPSG:2975.", required=False),
    "selected_only": Param("boolean", "N'exporter que la sélection courante.", required=False,
                           default=False),
    "encoding": Param("string", "Encodage des textes (Shapefile, CSV).", required=False,
                      default="UTF-8", enum=COMMON_ENCODINGS),
    "add_to_project": Param("boolean", "Ajouter le fichier produit au projet.", required=False,
                            default=True),
})
def export_layer(layer_id: str, format: str, output_name: str | None, target_crs: str | None,
                 selected_only: bool, encoding: str, add_to_project: bool) -> ToolResult:
    """Exporte une couche vers un nouveau fichier de mcp_outputs/, sans toucher à l'original.
    Vers Shapefile : noms de champs raccourcis à 10 caractères sans doublon (correspondance
    renvoyée dans field_mapping), .cpg écrit pour préserver les accents."""
    layer = get_vector_layer(layer_id)
    if layer.isEditable() and layer.isModified():
        raise ToolError(ErrorCode.PENDING_EDITS, f"« {layer.name()} » a des modifications non "
                        "enregistrées : request_commit ou rollback_edits avant d'exporter.")
    if selected_only and layer.selectedFeatureCount() == 0:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune entité sélectionnée dans QGIS.")
    driver, suffix = FORMATS[format]
    directory, warnings = output_dir()
    path = unique_path(directory, clean_name(output_name or layer.name()), suffix)

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = driver
    options.fileEncoding = encoding  # Shapefile : OGR écrit le .cpg correspondant
    options.layerName = path.stem
    options.onlySelectedFeatures = bool(selected_only)
    destination = crs_from_text(target_crs) if target_crs else layer.crs()
    if destination != layer.crs():
        options.ct = QgsCoordinateTransform(layer.crs(), destination, QgsProject.instance())
    field_mapping = None
    if format == "shp":
        names = layer.fields().names()
        plan = export_plan(names, layer_field_types(layer))
        field_mapping = plan["field_mapping"]
        options.attributes = list(range(len(names)))
        options.attributesExportNames = [field_mapping[name] for name in names]
        warnings.extend(plan["warnings"])
    elif format == "csv":
        options.layerOptions = ["GEOMETRY=AS_WKT", "SEPARATOR=SEMICOLON"]

    error, message, *_ = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer, str(path), QgsProject.instance().transformContext(), options)
    if error != QgsVectorFileWriter.WriterError.NoError:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Export impossible : {message or error}")

    data = {"layer": layer.name(), "path": str(path), "format": format,
            "crs": destination.authid() or None,
            "feature_count": layer.selectedFeatureCount() if selected_only
            else layer.featureCount(),
            "field_mapping": field_mapping}
    if add_to_project:
        exported = QgsVectorLayer(str(path), path.stem, "ogr")
        if exported.isValid():
            data["layer_id"] = add_to_group(exported).id()
        else:
            warnings.append("Fichier écrit mais illisible par QGIS : non ajouté au projet.")
    return ToolResult(data, warnings, [str(path)])
