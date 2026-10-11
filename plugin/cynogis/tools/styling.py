"""Stylisation des couches : symbole unique, catégories, dégradés, nomenclature, étiquettes.

Chaque modification mémorise le style précédent (core/stylehistory.py) : undo_style y revient.
"""
from __future__ import annotations

import json
from typing import Any

from qgis.core import (
    Qgis,
    QgsCategorizedSymbolRenderer,
    QgsFillSymbol,
    QgsGraduatedSymbolRenderer,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsRendererCategory,
    QgsRendererRange,
    QgsSingleSymbolRenderer,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtXml import QDomDocument

from ..core import landscape as nomenclature
from ..core import palettes as palette_store
from ..core import style as specs
from ..core.classify import METHODS, compute_breaks, range_labels
from ..core.colors import parse_color
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.naming import clean_name, unique_path
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.stats import to_float
from ..core.stylehistory import HISTORY
from .common import (
    feature_request,
    geometry_kind,
    get_layer,
    get_vector_layer,
    prepare_expression,
    refresh_layer,
    require_field,
    to_json_value,
)
from .outputs import output_dir

MAX_CATEGORIES = 60
MAX_VALUES = 100_000
GROUP_COLORS = {"1": "#d7191c", "2": "#ffd92f", "3": "#1a9641", "4": "#35978f", "5": "#2166ac"}
# QGIS >= 3.26 / 4.x : Qgis.LabelPlacement ; avant : QgsPalLayerSettings.Placement
_PLACEMENT = getattr(Qgis, "LabelPlacement", None) or QgsPalLayerSettings.Placement
PLACEMENTS = {"centre": _PLACEMENT.OverPoint, "autour_du_point": _PLACEMENT.AroundPoint,
              "le_long_de_la_ligne": _PLACEMENT.Line, "horizontal": _PLACEMENT.Horizontal,
              "libre": _PLACEMENT.Free}

LAYER_ID = Param("string", "Couche vecteur (layer_id).")
PALETTE = Param("string", "Palette nommée (voir list_style_options).", required=False)
COLORS = Param("array", 'Couleurs imposées, ex. ["#1a9641", "vert_fonce", "rgb(215,25,28)"].',
               required=False, items="string")
REVERSE = Param("boolean", "Inverser l'ordre des couleurs.", required=False, default=False)
STROKE_COLOR = Param("string", "Couleur de contour commune.", required=False)
STROKE_WIDTH = Param("number", "Épaisseur de contour (mm).", required=False, minimum=0,
                     maximum=20)
OPACITY = Param("number", "Opacité de 0 (transparent) à 1 (opaque).", required=False, default=1,
                minimum=0, maximum=1)


# --- Helpers ------------------------------------------------------------------------------
def _qcolor(value: Any) -> QColor:
    return QColor(*parse_color(value))


def _kind(layer: QgsVectorLayer) -> str:
    kind = geometry_kind(layer)
    if kind not in specs.GEOMETRY_KINDS:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'a pas de géométrie "
                        "stylisable.")
    return kind


def _validated(spec: dict, kind: str) -> dict:
    try:
        return specs.validate_symbol(spec, kind)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc


def _symbol(validated: dict):
    builder = {"polygon": QgsFillSymbol, "line": QgsLineSymbol,
               "point": QgsMarkerSymbol}[validated["geometry"]]
    symbol = builder.createSimple(validated["properties"])
    if symbol is None:
        raise ToolError(ErrorCode.INTERNAL_ERROR, "QGIS a refusé cette description de symbole.")
    symbol.setOpacity(validated["opacity"])
    return symbol


def _snapshot(layer, description: str) -> int:
    """Mémorise le style actuel (symbologie + étiquettes) avant de le remplacer."""
    document = QDomDocument()
    layer.exportNamedStyle(document)
    return HISTORY.push(layer.id(), layer.name(), document.toString(), description)


def _refresh(layer) -> None:
    refresh_layer(layer)
    try:
        from qgis.utils import iface
        if iface is not None:
            iface.layerTreeView().refreshLayerSymbology(layer.id())
    except Exception:  # hors interface graphique
        pass


def _apply(layer: QgsVectorLayer, renderer, description: str) -> dict:
    steps = _snapshot(layer, description)
    layer.setRenderer(renderer)
    _refresh(layer)
    return {"layer": layer.name(), "undo_steps": steps}


def _sort_key(value: Any) -> tuple:
    """Nombres dans l'ordre numérique, puis textes ; NULL en dernier."""
    number = to_float(value)
    if value is None:
        return (2, 0.0, "")
    return (0, number, "") if number is not None else (1, 0.0, str(value))


def _distinct_values(layer: QgsVectorLayer, field: str) -> dict[str, Any]:
    """{clé texte: valeur brute QGIS} des valeurs distinctes, dans l'ordre de lecture.

    La valeur brute est transmise au moteur de rendu : QGIS compare les catégories sur
    sa propre conversion en texte (12.0 → « 12 »), pas sur la nôtre.
    """
    distinct: dict[str, Any] = {}
    request = feature_request(layer, None, [field], False)
    for index, feature in enumerate(layer.getFeatures(request)):
        if index >= MAX_VALUES:
            break
        value = to_json_value(feature[field])
        key = "" if value is None else str(value)
        distinct.setdefault(key, None if value is None else feature[field])
    return distinct


def _numeric_values(layer: QgsVectorLayer, field: str) -> list[float]:
    values = []
    request = feature_request(layer, None, [field], False)
    for index, feature in enumerate(layer.getFeatures(request)):
        if index >= MAX_VALUES:
            break
        number = to_float(to_json_value(feature[field]))
        if number is not None:
            values.append(number)
    return values


def _categorized(layer: QgsVectorLayer, field: str, built: list[dict],
                 raw: dict[str, Any], description: str) -> dict:
    categories = [QgsRendererCategory("" if raw.get(e["value"]) is None else raw[e["value"]],
                                      _symbol(e["symbol"]), e["label"]) for e in built]
    return _apply(layer, QgsCategorizedSymbolRenderer(field, categories), description)


# --- Lecture ------------------------------------------------------------------------------
@tool(level=Level.READ, params={})
def list_style_options() -> dict:
    """Motifs de remplissage, formes de points, styles de ligne, placements d'étiquettes,
    palettes et méthodes de classification acceptés par les outils de style."""
    return {**specs.describe_options(), "palettes": palette_store.describe_palettes(),
            "classification_methods": list(METHODS),
            "note": "Couleurs : hexadécimal (#1a9641), rgb(26,150,65) ou nom (vert_fonce). "
                    "Les palettes ne sont que des suggestions."}


@tool(level=Level.READ, params={"layer_id": Param("string", "Couche (layer_id).")})
def get_layer_style(layer_id: str) -> dict:
    """Style actuel d'une couche (type de rendu, champ, catégories ou classes, couleurs,
    étiquettes). À lire avant de proposer une modification ou pour vérifier un résultat."""
    layer = get_layer(layer_id)
    renderer = layer.renderer() if hasattr(layer, "renderer") else None
    if not isinstance(layer, QgsVectorLayer):
        return {"layer": layer.name(), "type": "raster",
                "renderer": renderer.type() if renderer else None,
                "opacity": renderer.opacity() if renderer else None}
    info: dict[str, Any] = {"layer": layer.name(), "geometry": geometry_kind(layer),
                            "renderer": renderer.type() if renderer else None,
                            "opacity": layer.opacity(), "labels_enabled": layer.labelsEnabled(),
                            "undo_steps": HISTORY.depth(layer.id())}
    if isinstance(renderer, QgsCategorizedSymbolRenderer):
        info["field"] = renderer.classAttribute()
        info["categories"] = [{"value": to_json_value(c.value()), "label": c.label(),
                               "color": c.symbol().color().name() if c.symbol() else None}
                              for c in renderer.categories()[:MAX_CATEGORIES]]
    elif isinstance(renderer, QgsGraduatedSymbolRenderer):
        info["field"] = renderer.classAttribute()
        info["ranges"] = [{"min": r.lowerValue(), "max": r.upperValue(), "label": r.label(),
                           "color": r.symbol().color().name() if r.symbol() else None}
                          for r in renderer.ranges()]
    elif isinstance(renderer, QgsSingleSymbolRenderer) and renderer.symbol():
        info["color"] = renderer.symbol().color().name()
    labeling = layer.labeling()
    if layer.labelsEnabled() and isinstance(labeling, QgsVectorLayerSimpleLabeling):
        info["label_source"] = labeling.settings().fieldName
    return info


# --- Symbologie ---------------------------------------------------------------------------
@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "fill_color": Param("string", "Couleur (remplissage des polygones et points, trait des "
                        "lignes), ex. #1a9641 ou vert_fonce.", required=False),
    "stroke_color": STROKE_COLOR,
    "stroke_width": STROKE_WIDTH,
    "pattern": Param("string", "Motif : polygones (solid, horizontal, cross, diagonal_x…) ou "
                     "style de trait des lignes (dash, dot…).", required=False),
    "shape": Param("string", "Forme des points (circle, square, triangle, star…).",
                   required=False),
    "size": Param("number", "Taille des points (mm).", required=False, minimum=0.1, maximum=50),
    "opacity": OPACITY,
})
def apply_single_style(layer_id: str, fill_color: str | None, stroke_color: str | None,
                       stroke_width: float | None, pattern: str | None, shape: str | None,
                       size: float | None, opacity: float) -> ToolResult:
    """Applique un symbole unique à toute la couche. Couleurs et motifs libres, vérifiés avant
    d'atteindre QGIS. Le style précédent reste récupérable par undo_style."""
    layer = get_vector_layer(layer_id)
    kind = _kind(layer)
    spec = {"color": fill_color, "stroke_color": stroke_color, "stroke_width": stroke_width,
            "shape": shape, "size": size, "opacity": opacity}
    spec["stroke_style" if kind == "line" else "pattern"] = pattern
    if kind == "line" and fill_color is None:
        spec["color"] = stroke_color
    validated = _validated(spec, kind)
    result = _apply(layer, QgsSingleSymbolRenderer(_symbol(validated)), "symbole unique")
    return ToolResult({**result, "geometry": kind}, validated["warnings"])


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "field": Param("string", "Champ portant la catégorie."),
    "categories": Param("array", 'Catégories imposées : [{"value": "foret", "color": '
                        '"#1a9641", "label": "Forêt", "pattern": "solid"}]. Les autres valeurs '
                        "reçoivent les couleurs de palette/colors.", required=False,
                        items="object"),
    "palette": PALETTE,
    "colors": COLORS,
    "reverse": REVERSE,
    "stroke_color": STROKE_COLOR,
    "stroke_width": STROKE_WIDTH,
    "opacity": OPACITY,
    "sort": Param("boolean", "Trier les catégories (ordre numérique, puis alphabétique).",
                  required=False, default=True),
})
def apply_categorized_style(layer_id: str, field: str, categories: list | None,
                            palette: str | None, colors: list | None, reverse: bool,
                            stroke_color: str | None, stroke_width: float | None,
                            opacity: float, sort: bool) -> ToolResult:
    """Une couleur par valeur d'un champ (types de paysage, natures de surface, tout champ
    qualitatif). Les valeurs présentes dans la couche sont lues automatiquement."""
    layer = get_vector_layer(layer_id)
    field = require_field(layer, field)
    kind = _kind(layer)
    raw = _distinct_values(layer, field)
    if not raw:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucune entité.")
    keys = sorted(raw, key=lambda k: _sort_key(None if raw[k] is None else k)) if sort \
        else list(raw)
    warnings: list[str] = []
    if len(keys) > MAX_CATEGORIES:
        warnings.append(f"{len(keys)} valeurs distinctes : seules les {MAX_CATEGORIES} premières "
                        "sont représentées. Regroupe-les d'abord si nécessaire.")
        keys = keys[:MAX_CATEGORIES]
    base = {"stroke_color": stroke_color, "stroke_width": stroke_width, "opacity": opacity}
    try:
        built = specs.build_categories(keys, kind, categories, palette, colors, base, reverse)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    result = _categorized(layer, field, built, raw, f"catégories sur « {field} »")
    return ToolResult({**result, "field": field, "category_count": len(built),
                       "categories": [{"value": e["value"], "label": e["label"],
                                       "color": e["color"]} for e in built]}, warnings)


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "field": Param("string", "Champ numérique à représenter."),
    "method": Param("string", "Méthode des seuils.", required=False, default="quantile",
                    enum=METHODS),
    "classes": Param("integer", "Nombre de classes souhaité.", required=False, default=5,
                     minimum=2, maximum=20),
    "palette": PALETTE,
    "colors": COLORS,
    "reverse": REVERSE,
    "decimals": Param("integer", "Décimales des libellés de légende.", required=False,
                      default=2, minimum=0, maximum=6),
    "unit": Param("string", "Unité ajoutée aux libellés, ex. ha ou %.", required=False),
    "stroke_color": STROKE_COLOR,
    "stroke_width": STROKE_WIDTH,
    "opacity": OPACITY,
})
def apply_graduated_style(layer_id: str, field: str, method: str, classes: int,
                          palette: str | None, colors: list | None, reverse: bool,
                          decimals: int, unit: str | None, stroke_color: str | None,
                          stroke_width: float | None, opacity: float) -> ToolResult:
    """Classes de couleur selon un champ numérique : intervalles égaux, quantiles, seuils
    naturels (Jenks), écart-type ou bornes arrondies. Légende à la française
    (« 10,00 à 25,00 ha »)."""
    layer = get_vector_layer(layer_id)
    field = require_field(layer, field)
    kind = _kind(layer)
    try:
        classification = compute_breaks(_numeric_values(layer, field), method, classes)
        breaks, count = classification["breaks"], classification["class_count"]
        ramp = palette_store.resolve_colors(count, palette, colors, reverse)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    labels = range_labels(breaks, decimals, unit or "")
    ranges = []
    for index in range(count):
        validated = _validated({"color": ramp[index], "stroke_color": stroke_color,
                                "stroke_width": stroke_width, "opacity": opacity}, kind)
        ranges.append(QgsRendererRange(breaks[index], breaks[index + 1], _symbol(validated),
                                       labels[index]))
    result = _apply(layer, QgsGraduatedSymbolRenderer(field, ranges),
                    f"dégradé sur « {field} »")
    return ToolResult({**result, "field": field, "method": method,
                       "method_label": classification["method_label"], "class_count": count,
                       "breaks": breaks, "min": classification["min"],
                       "max": classification["max"],
                       "legend": [{"label": labels[i], "color": ramp[i]} for i in range(count)]},
                      classification["warnings"])


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "code_field": Param("string", "Champ du code de nomenclature.", required=False,
                        default="pays_code"),
    "by": Param("string", "class : une couleur par type ; group : une par grand poste.",
                required=False, default="class", enum=("class", "group")),
    "opacity": OPACITY,
    "stroke_color": Param("string", "Couleur de contour.", required=False, default="#555555"),
})
def apply_landscape_style(layer_id: str, code_field: str, by: str, opacity: float,
                          stroke_color: str) -> ToolResult:
    """Couleurs de référence de la nomenclature pour une couche produite par
    classify_landscape. Modifiables ensuite avec apply_categorized_style."""
    layer = get_vector_layer(layer_id)
    code_field = require_field(layer, code_field)
    kind = _kind(layer)
    raw = {k: v for k, v in _distinct_values(layer, code_field).items() if v is not None}
    if not raw:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"« {code_field} » est vide : la couche "
                        "a-t-elle été produite par classify_landscape ?")
    warnings: list[str] = []
    categories = []
    for code in sorted(raw):
        item = nomenclature.get_class(code)
        if item is None:
            warnings.append(f"Code hors nomenclature : {code} (gris).")
            categories.append({"value": code, "color": "#cccccc", "label": f"{code} (inconnu)"})
        elif by == "group":
            categories.append({"value": code, "color": GROUP_COLORS.get(item.group, "#cccccc"),
                               "label": nomenclature.GROUPS[item.group]})
        else:
            categories.append({"value": code, "color": item.color,
                               "label": f"{item.code} {item.label}"})
    built = specs.build_categories(
        [c["value"] for c in categories], kind, categories,
        base_symbol={"stroke_color": stroke_color, "stroke_width": 0.2, "opacity": opacity})
    result = _categorized(layer, code_field, built, raw, "nomenclature des paysages")
    return ToolResult({**result, "code_field": code_field, "mode": by,
                       "class_count": len(built),
                       "legend": [{"label": e["label"], "color": e["color"]} for e in built]},
                      warnings)


# --- Étiquettes ---------------------------------------------------------------------------
@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "field": Param("string", "Champ à afficher.", required=False),
    "expression": Param("string", "Expression à afficher, ex. \"nom\" || ' (' || "
                        "round($area/10000, 1) || ' ha)'.", required=False),
    "enabled": Param("boolean", "false : retirer les étiquettes.", required=False,
                     default=True),
    "font_size": Param("number", "Taille de police (pt).", required=False, default=9,
                       minimum=2, maximum=72),
    "color": Param("string", "Couleur du texte.", required=False, default="#000000"),
    "bold": Param("boolean", "Gras.", required=False, default=False),
    "italic": Param("boolean", "Italique.", required=False, default=False),
    "halo": Param("boolean", "Halo autour du texte (lisibilité sur aplats).", required=False,
                  default=True),
    "halo_color": Param("string", "Couleur du halo. Défaut : contraste avec le texte.",
                        required=False),
    "halo_size": Param("number", "Épaisseur du halo (mm).", required=False, default=1,
                       minimum=0, maximum=10),
    "placement": Param("string", "Position de l'étiquette.", required=False, default="libre",
                       enum=specs.LABEL_PLACEMENTS),
    "min_scale": Param("number", "Dénominateur d'échelle au-delà duquel les étiquettes "
                       "disparaissent, ex. 50000.", required=False, minimum=1),
})
def set_labels(layer_id: str, field: str | None, expression: str | None, enabled: bool,
               font_size: float, color: str, bold: bool, italic: bool, halo: bool,
               halo_color: str | None, halo_size: float, placement: str,
               min_scale: float | None) -> ToolResult:
    """Affiche (champ ou expression) ou retire les étiquettes d'une couche. Halo activé par
    défaut. Annulable par undo_style."""
    layer = get_vector_layer(layer_id)
    if not enabled:
        steps = _snapshot(layer, "suppression des étiquettes")
        layer.setLabelsEnabled(False)
        _refresh(layer)
        return ToolResult({"layer": layer.name(), "labels_enabled": False, "undo_steps": steps})
    if field:
        field = require_field(layer, field)
    if expression:
        prepare_expression(expression, layer)
    try:
        spec = specs.validate_labels({
            "field": field, "expression": expression, "font_size": font_size, "color": color,
            "bold": bold, "italic": italic, "halo": halo, "halo_color": halo_color,
            "halo_size": halo_size, "placement": placement, "min_scale": min_scale})
        text_color, buffer_color = _qcolor(spec["color"]), _qcolor(spec["halo_color"])
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc

    settings = QgsPalLayerSettings()
    settings.fieldName = expression or spec["field"]
    settings.isExpression = bool(expression)
    font = QFont(spec["font_family"])
    font.setBold(spec["bold"])
    font.setItalic(spec["italic"])
    text_format = QgsTextFormat()
    text_format.setFont(font)
    text_format.setSize(spec["font_size"])
    text_format.setColor(text_color)
    if spec["halo"]:
        buffer = QgsTextBufferSettings()
        buffer.setEnabled(True)
        buffer.setSize(spec["halo_size"])
        buffer.setColor(buffer_color)
        text_format.setBuffer(buffer)
    settings.setFormat(text_format)
    settings.placement = PLACEMENTS[spec["placement"]]
    if spec["min_scale"]:
        settings.scaleVisibility = True
        settings.minimumScale = float(spec["min_scale"])

    steps = _snapshot(layer, "étiquettes")
    layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    layer.setLabelsEnabled(True)
    _refresh(layer)
    return ToolResult({"layer": layer.name(), "labels_enabled": True,
                       "source": settings.fieldName, "font_size": spec["font_size"],
                       "halo_color": spec["halo_color"], "undo_steps": steps})


# --- Historique, fichiers -----------------------------------------------------------------
@tool(level=Level.MODIFY, params={
    "layer_id": Param("string", "Couche (layer_id). Absent : dernière couche stylisée.",
                      required=False),
    "steps": Param("integer", "Nombre de modifications à annuler.", required=False, default=1,
                   minimum=1, maximum=10),
})
def undo_style(layer_id: str | None, steps: int) -> ToolResult:
    """Revient au style précédent d'une couche (symbologie et étiquettes). Jusqu'à 10 retours
    par couche, pendant la session QGIS."""
    layer_id = layer_id or HISTORY.last_layer()
    if layer_id is None:
        return ToolResult({"restored": 0}, ["Aucun style modifié depuis le démarrage de QGIS."])
    layer = get_layer(layer_id)
    restored, description = 0, ""
    for _ in range(steps):
        snapshot = HISTORY.pop(layer.id())
        if snapshot is None:
            break
        document = QDomDocument()
        document.setContent(snapshot.xml)
        ok, message = layer.importNamedStyle(document)
        if not ok:
            raise ToolError(ErrorCode.INTERNAL_ERROR, f"Restauration impossible : {message}")
        description = snapshot.description
        restored += 1
    _refresh(layer)
    return ToolResult({"layer": layer.name(), "restored": restored, "undone": description,
                       "remaining_steps": HISTORY.depth(layer.id())},
                      [] if restored else ["Aucun style antérieur mémorisé pour cette couche."])


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche (layer_id)."),
    "output_name": Param("string", "Nom du fichier .qml (nettoyé, jamais écrasé).",
                         required=False),
})
def save_style_file(layer_id: str, output_name: str | None) -> ToolResult:
    """Enregistre le style d'une couche dans un fichier QML de mcp_outputs/, réutilisable
    dans QGIS ou à livrer avec les données."""
    layer = get_layer(layer_id)
    directory, warnings = output_dir()
    path = unique_path(directory, clean_name(output_name or f"style_{layer.name()}"), ".qml")
    message, ok = layer.saveNamedStyle(str(path))
    if not ok:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Style non enregistré : {message}")
    return ToolResult({"layer": layer.name(), "path": str(path)}, warnings, [str(path)])


@tool(level=Level.CREATE, params={
    "name": Param("string", "Nom de la palette."),
    "colors": Param("array", "Couleurs, de 2 à 30.", items="string"),
})
def save_palette(name: str, colors: list) -> ToolResult:
    """Enregistre une palette réutilisable (~/.cynogis/palettes.json), disponible pour les
    stylisations suivantes et d'une session à l'autre."""
    try:
        key = palette_store.register_palette(name, colors)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    path = palette_store.PALETTES_FILE
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(palette_store.USER_PALETTES, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    except OSError as exc:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Palette non enregistrée : {exc}") from exc
    return ToolResult({"name": key, "colors": palette_store.USER_PALETTES[key],
                       "path": str(path)}, [], [str(path)])
