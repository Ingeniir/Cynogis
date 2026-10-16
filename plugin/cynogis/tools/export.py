"""Export des résultats : tableaux, notes de synthèse, images de carte et projet."""
from __future__ import annotations

import csv
import os
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFields,
    QgsMapRendererParallelJob,
    QgsMapSettings,
    QgsMemoryProviderUtils,
    QgsProject,
    QgsVectorFileWriter,
)
from qgis.PyQt.QtCore import QMarginsF, QSize, QUrl
from qgis.PyQt.QtGui import QColor, QPageLayout, QPageSize, QPdfWriter, QTextDocument

from ..core.colors import parse_color
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.naming import clean_name, unique_path
from ..core.registry import Level, tool
from ..core.report import build_html, build_markdown, normalize_table
from ..core.schema import Param
from ..ui.confirm import register_detail_provider
from .common import (
    add_to_memory,
    feature_request,
    get_layer,
    get_vector_layer,
    make_field,
    prepare_expression,
    to_json_value,
)
from .outputs import Steps, output_dir, run_in_memory

TABLE_FORMATS = {"csv": (".csv", None), "xlsx": (".xlsx", "XLSX"), "ods": (".ods", "ODS")}
REPORT_FORMATS = {"pdf": ".pdf", "html": ".html", "markdown": ".md"}
SEPARATORS = {";": ";", ",": ",", "tabulation": "\t"}
MAX_EXPORT_ROWS = 100_000


def _output_path(name: str, suffix: str) -> tuple[Path, list[str]]:
    """Fichier neuf dans mcp_outputs/ : nom nettoyé, jamais d'écrasement."""
    directory, warnings = output_dir()
    return unique_path(directory, clean_name(name), suffix), warnings


def _write_csv(path: Path, headers: list, rows: list, separator: str) -> None:
    """CSV UTF-8 avec BOM : accents corrects à l'ouverture dans Excel."""
    try:
        with open(path, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter=SEPARATORS[separator])
            writer.writerow(headers)
            writer.writerows(["" if cell is None else cell for cell in row] for row in rows)
    except OSError as exc:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Écriture impossible : {exc}") from exc


def write_table(name: str, headers: list, rows: list, format: str,
                separator: str = ";") -> tuple[Path, list[str]]:
    """Tableau calculé → fichier neuf de mcp_outputs/ (csv, xlsx ou ods)."""
    suffix, driver = TABLE_FORMATS[format]
    path, warnings = _output_path(name, suffix)
    if driver is None:
        _write_csv(path, headers, rows, separator)
        return path, warnings
    fields = QgsFields()
    for index, header in enumerate(headers):
        values = [row[index] for row in rows if row[index] is not None]
        numeric = values and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                 for v in values)
        fields.append(make_field(str(header), "real" if numeric else "string"))
    table = QgsMemoryProviderUtils.createMemoryLayer("table", fields, Qgis.WkbType.NoGeometry,
                                                     QgsCoordinateReferenceSystem())
    features = []
    for row in rows:
        feature = QgsFeature(fields)
        feature.setAttributes([v if v is None or isinstance(v, (int, float)) else str(v)
                               for v in row])
        features.append(feature)
    add_to_memory(table, features)
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = driver
    options.layerName = path.stem
    options.fileEncoding = "UTF-8"
    error, message, *_ = QgsVectorFileWriter.writeAsVectorFormatV3(
        table, str(path), QgsProject.instance().transformContext(), options)
    if error != QgsVectorFileWriter.WriterError.NoError:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Export {format} impossible ({message}) : "
                        "pilote peut-être absent, essaie format=csv.")
    return path, warnings


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur dont la table est exportée (layer_id).",
                      required=False),
    "table": Param("object", 'Tableau calculé à écrire tel quel : {"headers": [...], '
                   '"rows": [[...]]} ou {"rows": [{...}, ...]}. Prioritaire sur layer_id.',
                   required=False),
    "fields": Param("array", "Champs exportés (défaut : tous).", required=False,
                    items="string"),
    "expression": Param("string", "Ne garder que les entités vérifiant cette expression.",
                        required=False),
    "format": Param("string", "Format du fichier.", required=False, default="csv",
                    enum=tuple(TABLE_FORMATS)),
    "output_name": Param("string", "Nom du fichier (nettoyé, jamais écrasé).", required=False),
    "separator": Param("string", "Séparateur CSV (« ; » pour Excel en français).",
                       required=False, default=";", enum=tuple(SEPARATORS)),
})
def export_table(layer_id: str | None, table: dict | None, fields: list | None,
                 expression: str | None, format: str, output_name: str | None,
                 separator: str) -> Steps:
    """Exporte vers un tableur (mcp_outputs/) la table attributaire d'une couche ou un tableau
    de résultats déjà calculé (statistiques, coefficients, indices)."""
    suffix, driver = TABLE_FORMATS[format]
    if table:
        try:
            normalized = normalize_table(table)
        except ValueError as exc:
            raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
        path, warnings = write_table(output_name or "resultats", normalized["headers"],
                                     normalized["rows"], format, separator)
        return ToolResult({"path": str(path), "format": format,
                           "row_count": len(normalized["rows"])}, warnings, [str(path)])
    if not layer_id:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique layer_id ou table.")

    layer = get_vector_layer(layer_id)
    if expression:
        prepare_expression(expression, layer)
    names = layer.fields().names()
    unknown = [name for name in fields or [] if name not in names]
    if unknown:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Champs inconnus : {', '.join(unknown)}",
                        {"available": names})
    selected = list(fields or names)
    path, warnings = _output_path(output_name or layer.name(), suffix)

    if driver is None:
        rows = []
        for feature in layer.getFeatures(feature_request(layer, expression, selected, False)):
            if len(rows) >= MAX_EXPORT_ROWS:
                warnings.append(f"Export limité à {MAX_EXPORT_ROWS} lignes.")
                break
            rows.append([to_json_value(feature[name]) for name in selected])
        _write_csv(path, selected, rows, separator)
        row_count = len(rows)
    else:
        source = ((yield from run_in_memory("native:extractbyexpression",
                                            {"INPUT": layer, "EXPRESSION": expression}))
                  if expression else layer)
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = driver
        options.layerName = path.stem
        options.fileEncoding = "UTF-8"
        options.attributes = [source.fields().indexFromName(name) for name in selected]
        error, message, *_ = QgsVectorFileWriter.writeAsVectorFormatV3(
            source, str(path), QgsProject.instance().transformContext(), options)
        if error != QgsVectorFileWriter.WriterError.NoError:
            raise ToolError(ErrorCode.WRITE_FAILED, f"Export {format} impossible ({message}) : "
                            "pilote peut-être absent, essaie format=csv.")
        row_count = source.featureCount()
    return ToolResult({"path": str(path), "format": format, "columns": selected,
                       "row_count": row_count}, warnings, [str(path)])


def write_pdf(html: str, path: Path) -> None:
    """PDF A4 rendu par Qt à partir du HTML de core/report.py (pas de dépendance externe)."""
    writer = QPdfWriter(str(path))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(18, 18, 18, 18), QPageLayout.Unit.Millimeter)
    writer.setTitle(path.stem)
    document = QTextDocument()
    document.setBaseUrl(QUrl.fromLocalFile(str(path.parent) + "/"))  # images relatives
    document.setHtml(html)
    # PyQt5 : print_ ; PyQt6 : print
    (getattr(document, "print_", None) or document.print)(writer)
    del writer  # termine le fichier
    if not path.is_file():
        raise ToolError(ErrorCode.WRITE_FAILED, f"PDF non écrit : {path}")


def write_document(content: str, path: Path) -> None:
    """Écrit le rapport : PDF (content est alors du HTML) ou texte selon l'extension."""
    try:
        if path.suffix == ".pdf":
            write_pdf(content, path)
        else:
            path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Écriture impossible : {exc}") from exc


@tool(level=Level.CREATE, params={
    "title": Param("string", "Titre de la note."),
    "sections": Param("array", 'Sections : [{"heading": "Contexte", "text": "...", "bullets": '
                      '["..."], "table": {"headers": [...], "rows": [[...]]}, "image": '
                      '"<chemin PNG de export_map_image>", "caption": "..."}]. Reprends les '
                      "chiffres renvoyés par les outils, sans les réécrire.", items="object"),
    "metadata": Param("object", 'En-tête, ex. {"Commune": "Saint-Paul", "Maître d\'ouvrage": '
                      '"..."}.', required=False),
    "format": Param("string", "pdf, html (imprimable) ou markdown.", required=False,
                    default="html", enum=tuple(REPORT_FORMATS)),
    "output_name": Param("string", "Nom du fichier (défaut : titre).", required=False),
})
def write_report(title: str, sections: list, metadata: dict | None, format: str,
                 output_name: str | None) -> ToolResult:
    """Rédige une note de synthèse (mcp_outputs/) à partir des résultats calculés : sections,
    listes et tableaux, nombres formatés à la française."""
    builder = build_markdown if format == "markdown" else build_html
    try:
        content = builder(title, sections, metadata or {})
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    path, warnings = _output_path(output_name or title, REPORT_FORMATS[format])
    write_document(content, path)
    return ToolResult({"path": str(path), "format": format, "section_count": len(sections),
                       "characters": len(content)}, warnings, [str(path)])


@tool(level=Level.CREATE, params={
    "output_name": Param("string", "Nom de l'image (défaut : carte).", required=False),
    "extent_layer_id": Param("string", "Couche définissant l'emprise (layer_id). Absent : "
                             "emprise affichée.", required=False),
    "width": Param("integer", "Largeur (px).", required=False, default=1600, minimum=200,
                   maximum=8000),
    "height": Param("integer", "Hauteur (px).", required=False, default=1200, minimum=200,
                    maximum=8000),
    "background": Param("string", "Couleur de fond.", required=False, default="#ffffff"),
    "margin_percent": Param("number", "Marge autour de l'emprise (%).", required=False,
                            default=5, minimum=0, maximum=50),
})
def export_map_image(output_name: str | None, extent_layer_id: str | None, width: int,
                     height: int, background: str, margin_percent: float) -> ToolResult:
    """Image PNG (mcp_outputs/) des couches visibles de la carte, pour illustrer une note.
    Pour une carte avec cadre, échelle et légende : composeur d'impression de QGIS."""
    try:
        from qgis.utils import iface
        canvas = iface.mapCanvas() if iface else None
    except ImportError:
        canvas = None
    if canvas is None:
        raise ToolError(ErrorCode.INTERNAL_ERROR, "Aucune carte QGIS disponible.")
    layers = canvas.layers()
    if not layers:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune couche visible : l'image serait vide.")
    try:
        background_color = QColor(*parse_color(background))
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    project = QgsProject.instance()
    destination = canvas.mapSettings().destinationCrs()
    if extent_layer_id:
        layer = get_layer(extent_layer_id)
        extent = layer.extent()
        if layer.crs() != destination:
            extent = QgsCoordinateTransform(layer.crs(), destination,
                                            project).transformBoundingBox(extent)
    else:
        extent = canvas.extent()
    if extent.isEmpty():
        raise ToolError(ErrorCode.INVALID_PARAMS, "Emprise vide.")
    extent.scale(1.0 + float(margin_percent) / 100.0)
    path, warnings = _output_path(output_name or "carte", ".png")
    render_map(project, layers, destination, extent, QSize(width, height), background_color,
               path)
    return ToolResult({"path": str(path), "width": width, "height": height,
                       "layer_count": len(layers)}, warnings, [str(path)])


def render_map(project: QgsProject, layers: list, crs: QgsCoordinateReferenceSystem,
               extent, size: QSize, background: QColor, path: Path) -> None:
    """Rendu PNG des couches (la première dessinée au-dessus) sur l'emprise donnée."""
    settings = QgsMapSettings()
    settings.setLayers(layers)
    settings.setDestinationCrs(crs)
    settings.setTransformContext(project.transformContext())
    settings.setExtent(extent)
    settings.setOutputSize(size)
    settings.setBackgroundColor(background)
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    if not job.renderedImage().save(str(path), "PNG"):
        raise ToolError(ErrorCode.WRITE_FAILED, f"Image non enregistrée : {path}")


def _project_target(path: str | None) -> str:
    target = path or QgsProject.instance().fileName()
    if target and not target.lower().endswith((".qgz", ".qgs")):
        target += ".qgz"
    return target


@tool(level=Level.DESTROY, params={
    "path": Param("string", "Chemin du .qgz. Absent : enregistre le projet en place (écrase "
                  "le fichier courant).", required=False),
})
def save_project(path: str | None) -> ToolResult:
    """Enregistre le projet QGIS (couches, styles, mise en page). Confirmation humaine : un
    fichier existant est écrasé."""
    target = _project_target(path)
    if not target:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Projet jamais enregistré : indique path "
                        "(fichier .qgz).")
    project = QgsProject.instance()
    if not project.write(target):
        raise ToolError(ErrorCode.WRITE_FAILED, f"Enregistrement impossible : {target} "
                        f"({project.error()})")
    return ToolResult({"path": target, "layer_count": len(project.mapLayers())}, [], [target])


def _save_project_details(params: dict) -> list[str]:
    target = _project_target(params.get("path"))
    lines = [f"Fichier : {target or '(non défini)'}"]
    if target and os.path.exists(target):
        lines.append("Ce fichier existe et sera écrasé.")
    lines.append(f"{len(QgsProject.instance().mapLayers())} couche(s) dans le projet.")
    return lines


register_detail_provider("save_project", _save_project_details)
