"""Audit d'un projet QGIS : relevé des faits par PyQGIS, règles dans core/project_audit.py."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsCsException,
    QgsMapLayer,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.jobs import run_now
from ..core.project_audit import audit, build_sections, severity_counts, verdict
from ..core.registry import Level, tool
from ..core.report import build_html, build_markdown
from ..core.schema import Param
from ..core.shapefile import looks_like_mojibake, sidecar_messages, sidecar_report, size_messages
from ..core.territory import detect_territory
from .common import (
    enum_name,
    extent_wgs84,
    feature_request,
    file_format,
    geometry_kind,
    is_shapefile,
    layer_kind,
    rect_to_list,
    source_path,
)
from .export import REPORT_FORMATS, _output_path, render_map, write_document
from .features import geometry_report
from .shapefiles import _scan_sidecars, _text_sample

MAX_FINDINGS_RETURNED = 50
MAP_SIZE = QSize(1600, 1100)


def _vector_facts(layer: QgsVectorLayer, max_features: int) -> dict[str, Any]:
    count = layer.featureCount()
    count = count if count >= 0 else None
    geometry = geometry_kind(layer)
    presence = enum_name(layer.hasSpatialIndex())
    facts: dict[str, Any] = {
        "geometry": geometry, "feature_count": count, "modified": layer.isModified(),
        "spatial_index": None if "Unknown" in presence else "NotPresent" not in presence,
        "shapefile": is_shapefile(layer),
    }
    if geometry not in ("none", "unknown"):
        if count is not None and count <= max_features:
            facts["geometry_check"] = run_now(geometry_report(
                layer, feature_request(layer, None, [], True), 0))
        else:
            facts["geometry_skipped"] = True
    path = source_path(layer)
    if facts["shapefile"] and path and os.path.isfile(path):
        extensions, sizes = _scan_sidecars(path)
        facts["sidecar_messages"] = (sidecar_messages(sidecar_report(extensions))
                                     + size_messages(sizes))
        facts["mojibake"] = looks_like_mojibake(_text_sample(layer))
    return facts


def _raster_facts(layer: QgsRasterLayer) -> dict[str, Any]:
    provider = layer.dataProvider()
    facts: dict[str, Any] = {
        "size": f"{layer.width()} x {layer.height()}", "bands": layer.bandCount(),
        "pixel_size": f"{layer.rasterUnitsPerPixelX():.3g} x {layer.rasterUnitsPerPixelY():.3g}",
    }
    if layer.providerType() == "gdal" and layer.bandCount():
        facts["nodata"] = provider.sourceHasNoDataValue(1) or bool(provider.userNoDataValues(1))
    return facts


def _layer_facts(layer: QgsMapLayer, max_features: int) -> dict[str, Any]:
    facts: dict[str, Any] = {"id": layer.id(), "name": layer.name(), "kind": layer_kind(layer),
                             "valid": layer.isValid()}
    if not layer.isValid():
        return facts
    crs = layer.crs()
    territory = detect_territory(rect_to_list(extent_wgs84(layer)))
    path = source_path(layer)
    facts.update({
        "format": file_format(layer), "source": path,
        "source_missing": bool(path) and not os.path.exists(path),
        "crs": (crs.authid() or crs.description()) if crs.isValid() else None,
        "geographic": crs.isValid() and crs.isGeographic(),
        "territory": territory.code if territory else None,
        "reference_crs": territory.epsg if territory else None,
        "memory": layer.providerType() == "memory",
    })
    if isinstance(layer, QgsVectorLayer):
        facts.update(_vector_facts(layer, max_features))
    elif isinstance(layer, QgsRasterLayer):
        facts.update(_raster_facts(layer))
    return facts


def _project_facts(project: QgsProject, layers: list[dict[str, Any]]) -> dict[str, Any]:
    crs = project.crs()
    territories = {layer["territory"] for layer in layers if layer.get("territory")}
    storage = getattr(project, "filePathStorage", None)  # QGIS ≥ 3.22
    reference = None
    if len(territories) == 1:
        reference = next(layer["reference_crs"] for layer in layers if layer.get("territory"))
    return {
        "title": project.title() or None, "file": project.fileName() or None,
        "dirty": project.isDirty(),
        "crs": crs.authid() or None if crs.isValid() else None,
        "geographic": crs.isValid() and crs.isGeographic(),
        "territory": ", ".join(sorted(territories)) or None, "territories": len(territories),
        "reference_crs": reference,
        "absolute_paths": storage() == Qgis.FilePathType.Absolute if storage else None,
        "layer_count": len(layers),
    }


def _overview_map(project: QgsProject, path: Path) -> list[str]:
    """Carte d'ensemble des couches cochées. Cadrage sur les vecteurs et rasters fichiers : un
    fond web (emprise mondiale) est dessiné mais ne fixe pas l'emprise. Renvoie les warnings."""
    layers = [lyr for lyr in project.layerTreeRoot().checkedLayers() if lyr.isValid()]
    crs = project.crs()
    if not crs.isValid():
        crs = next((lyr.crs() for lyr in layers if lyr.crs().isValid()), crs)
    extent = None
    for layer in layers:
        if layer_kind(layer) != "vector" and layer.providerType() != "gdal":
            continue
        try:
            box = QgsCoordinateTransform(layer.crs(), crs, project).transformBoundingBox(
                layer.extent())
        except QgsCsException:
            continue
        if box.isEmpty():
            continue
        if extent is None:
            extent = box
        else:
            extent.combineExtentWith(box)
    if extent is None or not crs.isValid():
        return ["Carte d'ensemble omise : aucune couche cochée avec une emprise exploitable."]
    extent.scale(1.05)
    try:
        render_map(project, layers, crs, extent, MAP_SIZE, QColor("white"), path)
    except ToolError as exc:
        return [f"Carte d'ensemble omise : {exc}"]
    return []


def _open_project(project_path: str | None) -> QgsProject:
    if not project_path:
        return QgsProject.instance()
    if not os.path.isfile(project_path):
        raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Projet introuvable : {project_path}")
    project = QgsProject()  # lu à part : le projet ouvert dans QGIS n'est pas touché
    if not project.read(project_path):
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Projet illisible : {project.error()}")
    return project


@tool(level=Level.CREATE, params={
    "project_path": Param("string", "Fichier .qgz/.qgs à auditer sans l'ouvrir. Absent : "
                          "projet ouvert dans QGIS.", required=False),
    "max_features": Param("integer", "Au-delà de ce nombre d'entités, les géométries d'une "
                          "couche ne sont pas contrôlées (durée).", required=False,
                          default=50_000, minimum=0, maximum=1_000_000),
    "format": Param("string", "Format du rapport.", required=False, default="pdf",
                    enum=tuple(REPORT_FORMATS)),
    "output_name": Param("string", "Nom du fichier (défaut : audit_<projet>).", required=False),
})
def audit_project(project_path: str | None, max_features: int, format: str,
                  output_name: str | None) -> ToolResult:
    """Audit qualité complet d'un projet QGIS, livré en rapport PDF (mcp_outputs/) : projet
    (enregistrement, SCR, chemins), chaque couche (source, SCR vs territoire, couches
    temporaires, éditions en cours, géométries invalides, index spatial, shapefiles, NoData),
    anomalies classées par gravité avec recommandations. Renvoie aussi les anomalies."""
    project = _open_project(project_path)
    try:
        layers = [_layer_facts(layer, max_features) for layer in project.mapLayers().values()]
        info = _project_facts(project, layers)
        name = info["title"] or (Path(info["file"]).stem if info["file"]
                                 else "projet non enregistré")
        path, warnings = _output_path(output_name or f"audit_{name}", REPORT_FORMATS[format])
        map_path, _ = _output_path(f"{path.stem}_carte", ".png")
        map_warnings = _overview_map(project, map_path)  # avant clear() : couches requises
    finally:
        if project is not QgsProject.instance():
            project.clear()
    warnings += map_warnings
    outputs = [str(path)] + ([] if map_warnings else [str(map_path)])
    findings = audit(info, layers)
    title = f"Audit du projet {name}"
    metadata = {"Projet": name, "QGIS": Qgis.QGIS_VERSION, "Couches": len(layers)}
    builder = build_markdown if format == "markdown" else build_html
    sections = build_sections(info, layers, findings, None if map_warnings else map_path.name)
    write_document(builder(title, sections, metadata), path)
    counts = severity_counts(findings)
    if len(findings) > MAX_FINDINGS_RETURNED:
        warnings.append(f"{len(findings)} anomalies : seules les {MAX_FINDINGS_RETURNED} plus "
                        "graves sont renvoyées, toutes figurent dans le rapport.")
    return ToolResult({"path": str(path), "format": format, "verdict": verdict(counts),
                       "counts": counts, "layer_count": len(layers),
                       "map": outputs[1] if len(outputs) > 1 else None,
                       "findings": findings[:MAX_FINDINGS_RETURNED]},
                      warnings, outputs)
