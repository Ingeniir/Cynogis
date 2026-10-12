"""Atlas PDF : une page par entité d'une couche de couverture (fiches, secteurs, parcelles)."""
from __future__ import annotations

from pathlib import Path

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsExpression,
    QgsFillSymbol,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutPoint,
    QgsPrintLayout,
    QgsProject,
    QgsReadWriteContext,
    QgsRectangle,
    QgsTextFormat,
)
from qgis.PyQt.QtCore import QRectF
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtXml import QDomDocument

from ..core import atlas as pages
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.naming import clean_name, unique_path
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.territory import detect_territory
from .common import (
    extent_wgs84,
    feature_request,
    get_layer,
    get_vector_layer,
    prepare_expression,
    rect_to_list,
    require_field,
)
from .outputs import output_dir

NORTH_ARROW = "arrows/NorthArrow_02.svg"
DEFAULT_TITLE = "[% @atlas_pagename %]"
PAGE_NUMBER = "Page [% @atlas_featurenumber %] / [% @atlas_totalfeatures %]"
DATE = "[% format_date(now(), 'dd/MM/yyyy') %]"
OVERVIEW_EXTENTS = ("territory", "coverage")
# Cadre de la page courante sur la carte de localisation.
OVERVIEW_FRAME = {"color": "255,0,0,60", "outline_color": "255,0,0,255", "outline_width": "0.7"}


def _label(layout, text: str, box: pages.Box, size: float, bold: bool = False):
    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    font = QFont("Arial")
    font.setBold(bold)
    text_format = QgsTextFormat()
    text_format.setFont(font)
    text_format.setSize(size)
    label.setTextFormat(text_format)
    layout.addLayoutItem(label)
    label.attemptSetSceneRect(QRectF(box.x, box.y, box.width, box.height))
    return label


def _north_arrow() -> str | None:
    for directory in QgsApplication.svgPaths():
        candidate = Path(directory) / NORTH_ARROW
        if candidate.is_file():
            return str(candidate)
    return None


def _build(layout, size: str, orientation: str, title: str, footer: str | None,
           legend: bool, extent, overview_extent=None,
           overview_layers: list | None = None) -> QgsLayoutItemMap:
    """Page générée : titre, carte, légende filtrée sur la carte, carte de localisation (si
    overview_extent), échelle, nord, pied."""
    layout.initializeDefaults()
    page_orientation = (QgsLayoutItemPage.Orientation.Landscape if orientation == "landscape"
                        else QgsLayoutItemPage.Orientation.Portrait)
    layout.pageCollection().page(0).setPageSize(size, page_orientation)
    boxes = pages.layout_boxes(size, orientation, legend, overview_extent is not None)
    _label(layout, title, boxes["title"], 16, bold=True)
    box = boxes["map"]
    item = QgsLayoutItemMap(layout)
    item.setFrameEnabled(True)
    item.setCrs(QgsProject.instance().crs())
    layout.addLayoutItem(item)
    item.attemptSetSceneRect(QRectF(box.x, box.y, box.width, box.height))
    # Emprise initiale : sans elle, QGIS redimensionne la carte à la première page (elle
    # déborde sur le pied) et l'échelle graphique, calculée trop tôt, reste vide.
    item.zoomToExtent(extent)
    if overview_extent is not None:
        box = boxes["overview"]
        overview = QgsLayoutItemMap(layout)
        overview.setFrameEnabled(True)
        overview.setCrs(QgsProject.instance().crs())
        if overview_layers:
            overview.setLayers(overview_layers)
            overview.setKeepLayerSet(True)
        layout.addLayoutItem(overview)
        overview.attemptSetSceneRect(QRectF(box.x, box.y, box.width, box.height))
        overview.zoomToExtent(overview_extent)
        frame = overview.overview()
        frame.setLinkedMap(item)  # rectangle de la page courante
        frame.setFrameSymbol(QgsFillSymbol.createSimple(OVERVIEW_FRAME))
    if legend:
        box = boxes["legend"]
        legend_item = QgsLayoutItemLegend(layout)
        legend_item.setTitle("Légende")
        legend_item.setLinkedMap(item)
        legend_item.setLegendFilterByMapEnabled(True)  # couches visibles sur la page
        legend_item.setResizeToContents(False)
        layout.addLayoutItem(legend_item)
        legend_item.attemptSetSceneRect(QRectF(box.x, box.y, box.width, box.height))
    scale_bar = QgsLayoutItemScaleBar(layout)
    scale_bar.setLinkedMap(item)
    scale_bar.applyDefaultSettings()
    scale_bar.applyDefaultSize()
    scale_bar.setStyle("Single Box")
    layout.addLayoutItem(scale_bar)
    map_box = boxes["map"]
    scale_bar.attemptMove(QgsLayoutPoint(map_box.x + 3, map_box.y + map_box.height - 15))
    arrow_path = _north_arrow()
    if arrow_path:
        arrow = QgsLayoutItemPicture(layout)
        arrow.setPicturePath(arrow_path)
        arrow.setLinkedMap(item)  # suit la rotation de la carte
        layout.addLayoutItem(arrow)
        arrow.attemptSetSceneRect(QRectF(map_box.x + map_box.width - 15, map_box.y + 3, 12, 12))
    parts = [p for p in (footer, f"Réalisation : Cynogis, {DATE}", PAGE_NUMBER) if p]
    _label(layout, "   —   ".join(parts), boxes["footer"], 8)
    return item


def _from_template(layout, path: str) -> QgsLayoutItemMap:
    document = QDomDocument()
    try:
        content = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Modèle illisible : {exc}") from exc
    document.setContent(content)
    _, ok = layout.loadFromTemplate(document, QgsReadWriteContext())
    if not ok:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{Path(path).name} n'est pas un modèle de "
                        "mise en page QGIS (.qpt) valide.")
    maps = [i for i in layout.items() if isinstance(i, QgsLayoutItemMap)]
    if not maps:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Le modèle ne contient aucune carte.")
    return maps[0]


def _overview_extent(coverage, mode: str, coverage_extent: QgsRectangle,
                     notes: list[str]) -> QgsRectangle:
    """Emprise de la carte de localisation, dans le SCR du projet."""
    if mode == "territory":
        territory = detect_territory(rect_to_list(extent_wgs84(coverage)))
        if territory is not None:
            west, south, east, north = territory.bbox
            project = QgsProject.instance()
            return QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                                          project.crs(), project
                                          ).transformBoundingBox(QgsRectangle(west, south,
                                                                              east, north))
        notes.append("Île non détectée : la carte de localisation montre toute la couche "
                     "de couverture.")
    extent = QgsRectangle(coverage_extent)
    extent.scale(1.3)
    return extent


@tool(level=Level.CREATE, params={
    "coverage_layer_id": Param("string", "Couche de couverture (layer_id) : une page par "
                               "entité (secteurs, parcelles, mailles, habitats…)."),
    "page_name_field": Param("string", "Champ du nom de page (titre par défaut, nom des "
                             "pages).", required=False),
    "title": Param("string", "Titre de chaque page ; expressions QGIS entre [% %], ex. "
                   "\"Enjeux - secteur [% \\\"nom\\\" %]\". Défaut : nom de la page.",
                   required=False),
    "footer": Param("string", "Pied de page (sources, maître d'ouvrage…), ex. \"Sources : "
                    "IGN BD ORTHO, INPN TAXREF v18\".", required=False),
    "filter_expression": Param("string", "Ne garder que ces entités.", required=False),
    "sort_field": Param("string", "Ordre des pages.", required=False),
    "page_size": Param("string", "Format.", required=False, default="A4",
                       enum=tuple(pages.PAGE_SIZES)),
    "orientation": Param("string", "Orientation.", required=False, default="landscape",
                         enum=pages.ORIENTATIONS),
    "margin_percent": Param("number", "Marge autour de chaque entité (%).", required=False,
                            default=10, minimum=0, maximum=200),
    "scale": Param("integer", "Échelle fixe (1:scale) au lieu de la marge, ex. 5000.",
                   required=False, minimum=100),
    "legend": Param("boolean", "Légende (couches visibles sur la page).", required=False,
                    default=True),
    "overview": Param("boolean", "Carte de localisation : l'île (ou toute la couverture) "
                      "avec le cadre de la page en rouge.", required=False, default=True),
    "overview_extent": Param("string", "territory : l'île détectée (La Réunion, Mayotte) ; "
                             "coverage : toute la couche de couverture.", required=False,
                             default="territory", enum=OVERVIEW_EXTENTS),
    "overview_layer_ids": Param("array", "Couches de la carte de localisation (layer_id), ex. "
                                "contour de l'île, fond de plan. Défaut : couches visibles.",
                                required=False, items="string"),
    "template_path": Param("string", "Modèle .qpt du bureau d'études (charte graphique) : sa "
                           "première carte suit l'atlas ; title, footer, page_size, "
                           "orientation, legend et overview sont alors ignorés.",
                           required=False),
    "max_pages": Param("integer", "Nombre maximal de pages (l'export bloque QGIS pendant sa "
                       "durée).", required=False, default=50, minimum=1, maximum=500),
    "output_name": Param("string", "Nom du PDF (nettoyé, jamais écrasé).", required=False),
})
def export_atlas_pdf(coverage_layer_id: str, page_name_field: str | None, title: str | None,
                     footer: str | None, filter_expression: str | None,
                     sort_field: str | None, page_size: str, orientation: str,
                     margin_percent: float, scale: int | None, legend: bool,
                     overview: bool, overview_extent: str, overview_layer_ids: list | None,
                     template_path: str | None, max_pages: int,
                     output_name: str | None) -> ToolResult:
    """Atlas PDF (un fichier, une page par entité de la couche de couverture) des couches
    visibles du projet, dans mcp_outputs/. Page générée : titre, carte cadrée sur l'entité,
    légende, carte de localisation, échelle, nord, pied de page (sources, date, n° de
    page) ; ou modèle .qpt du
    bureau d'études. La mise en page est aussi ajoutée au projet (« Atlas Cynogis … ») pour
    être retouchée dans le composeur de QGIS puis réexportée."""
    coverage = get_vector_layer(coverage_layer_id)
    page_name_field = require_field(coverage, page_name_field) if page_name_field else None
    sort_field = require_field(coverage, sort_field) if sort_field else None
    if filter_expression:
        prepare_expression(filter_expression, coverage, "filter_expression")
    if template_path and not Path(template_path).is_file():
        raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Modèle introuvable : {template_path}")
    count = sum(1 for _ in coverage.getFeatures(feature_request(coverage, filter_expression,
                                                                [], False)))
    if not count:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune entité à mettre en page.")
    if count > max_pages:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{count} pages : au-delà de max_pages "
                        f"({max_pages}). Filtre la couche ou augmente max_pages.")

    project = QgsProject.instance()
    notes: list[str] = []
    layout = QgsPrintLayout(project)
    manager = project.layoutManager()
    base = f"Atlas Cynogis - {coverage.name()}"
    name, number = base, 1
    while manager.layoutByName(name) is not None:
        number += 1
        name = f"{base} {number}"
    layout.setName(name)
    if template_path:
        map_item = _from_template(layout, template_path)
    else:
        try:
            extent = QgsCoordinateTransform(coverage.crs(), project.crs(), project
                                            ).transformBoundingBox(coverage.extent())
            located = None
            if overview:
                located = _overview_extent(coverage, overview_extent, extent, notes)
            layers = [get_layer(i) for i in overview_layer_ids or []]
            map_item = _build(layout, page_size, orientation, title or DEFAULT_TITLE, footer,
                              legend, extent, located, layers)
        except ValueError as exc:
            raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc

    atlas = layout.atlas()
    atlas.setCoverageLayer(coverage)
    atlas.setEnabled(True)
    atlas.setHideCoverage(False)
    atlas.setPageNameExpression(QgsExpression.quotedColumnRef(page_name_field)
                                if page_name_field else "@atlas_featureid")
    # Toujours redéfinis : un modèle .qpt peut porter le filtre ou le tri d'un autre atlas.
    atlas.setFilterFeatures(bool(filter_expression))
    atlas.setFilterExpression(filter_expression or "")
    atlas.setSortFeatures(bool(sort_field))
    atlas.setSortExpression(QgsExpression.quotedColumnRef(sort_field) if sort_field else "")
    map_item.setAtlasDriven(True)
    if scale:
        map_item.setAtlasScalingMode(QgsLayoutItemMap.AtlasScalingMode.Fixed)
        map_item.setScale(float(scale))
    else:
        map_item.setAtlasScalingMode(QgsLayoutItemMap.AtlasScalingMode.Auto)
        map_item.setAtlasMargin(float(margin_percent) / 100.0)

    count = atlas.updateFeatures()  # pages réellement produites
    directory, warnings = output_dir()
    warnings.extend(notes)
    path = unique_path(directory, clean_name(output_name or f"atlas_{coverage.name()}"),
                       ".pdf")
    settings = QgsLayoutExporter.PdfExportSettings()
    settings.dpi = 300
    status, error = QgsLayoutExporter.exportToPdf(atlas, str(path), settings)
    if status != QgsLayoutExporter.ExportResult.Success:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Export de l'atlas impossible : "
                        f"{error or status}")
    if not manager.addLayout(layout):  # le gestionnaire détruit une mise en page refusée
        name = None
        warnings.append("Mise en page non ajoutée au projet (le PDF est bien produit).")
    return ToolResult({
        "path": str(path), "pages": count, "layout": name,
        "template": Path(template_path).name if template_path else None,
        "page_size": None if template_path else page_size,
        "orientation": None if template_path else orientation,
        "scale": scale, "margin_percent": None if scale else margin_percent,
    }, warnings, [str(path)])
