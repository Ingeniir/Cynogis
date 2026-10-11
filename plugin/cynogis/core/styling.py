"""Stylisation des couches : symboles, catégories, dégradés et étiquettes."""

from __future__ import annotations

import json
import os

from qgis.core import (
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
from ..core.errors import ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.stats import to_float
from ..core.stylehistory import HISTORY
from .common import (
    feature_request,
    outputs_root,
    refresh_layer,
    require_field,
    resolve_layer,
    to_json_value,
)

MAX_CATEGORIES = 60
MAX_VALUES = 100_000

_LAYER = Param(type="string", description="Nom ou identifiant de la couche.", required=True)
_PALETTE = Param(
    type="string",
    description="Palette de couleurs à utiliser (voir list_style_options).",
    required=False,
)
_COLORS = Param(
    type="array",
    description="Couleurs imposées, par exemple [\"#1a9641\", \"#d7191c\"].",
    required=False,
    items="string",
)


def _qcolor(value) -> QColor:
    red, green, blue, alpha = parse_color(value)
    return QColor(red, green, blue, alpha)


def _build_symbol(validated: dict):
    """Construit un symbole QGIS à partir de propriétés validées."""
    builders = {
        "polygon": QgsFillSymbol,
        "line": QgsLineSymbol,
        "point": QgsMarkerSymbol,
    }
    symbol = builders[validated["geometry"]].createSimple(validated["properties"])
    if symbol is None:
        raise ToolError("STYLE_FAILED", "QGIS n'a pas accepté cette description de symbole.")
    symbol.setOpacity(validated["opacity"])
    return symbol


def _geometry_kind(layer) -> str:
    if not isinstance(layer, QgsVectorLayer):
        raise ToolError("BAD_LAYER", "Seules les couches vecteur sont stylisables ici.")
    return specs.normalize_geometry(int(layer.geometryType()))


def _snapshot(layer, description: str) -> int:
    """Mémorise le style actuel avant de le remplacer."""
    document = QDomDocument()
    layer.exportNamedStyle(document)
    return HISTORY.push(layer.id(), layer.name(), document.toString(), description)


def _apply(layer, renderer, description: str) -> dict:
    depth = _snapshot(layer, description)
    layer.setRenderer(renderer)
    refresh_layer(layer)
    _refresh_legend(layer)
    return {"layer": layer.name(), "undo_steps": depth}


def _refresh_legend(layer) -> None:
    """Met à jour la légende du panneau des couches."""
    try:
        from qgis.utils import iface

        if iface is not None:
            iface.layerTreeView().refreshLayerSymbology(layer.id())
    except Exception:  # pragma: no cover - hors interface graphique
        pass


def _collect_values(layer, field: str, numeric: bool = False) -> list:
    """Lit les valeurs d'un champ, sans charger les géométries."""
    values = []
    request = feature_request(layer, fields=[field], geometry=False)
    for index, feature in enumerate(layer.getFeatures(request)):
        if index >= MAX_VALUES:
            break
        raw = to_json_value(feature[field])
        if numeric:
            number = to_float(raw)
            if number is not None:
                values.append(number)
        else:
            values.append(raw)
    return values


@tool(level=Level.READ, params={})
def list_style_options() -> dict:
    """Liste les motifs, formes, palettes et méthodes de classification.

    À consulter avant de styliser : donne les valeurs exactes acceptées par
    apply_single_style, apply_categorized_style et apply_graduated_style.
    """
    return {
        **specs.describe_options(),
        "palettes": palette_store.describe_palettes(),
        "classification_methods": list(METHODS),
        "note": (
            "Les couleurs s'écrivent en hexadécimal (#1a9641), en rgb(26,150,65) "
            "ou par leur nom (vert_fonce). Les palettes ne sont que des "
            "suggestions : vous pouvez fournir vos propres couleurs."
        ),
    }


@tool(level=Level.READ, params={"layer": _LAYER})
def get_layer_style(layer: str) -> dict:
    """Décrit le style actuellement appliqué à une couche.

    Utile pour savoir ce qui existe déjà avant de proposer une modification,
    et pour vérifier le résultat d'une stylisation.
    """
    target = resolve_layer(layer)
    if not isinstance(target, QgsVectorLayer):
        return {
            "layer": target.name(),
            "type": "raster",
            "opacity": target.renderer().opacity() if target.renderer() else None,
        }
    renderer = target.renderer()
    info: dict = {
        "layer": target.name(),
        "geometry": _geometry_kind(target),
        "renderer": renderer.type() if renderer else None,
        "opacity": target.opacity(),
        "labels_enabled": target.labelsEnabled(),
        "undo_steps": HISTORY.depth(target.id()),
    }
    if isinstance(renderer, QgsCategorizedSymbolRenderer):
        info["field"] = renderer.classAttribute()
        info["categories"] = [
            {
                "value": to_json_value(category.value()),
                "label": category.label(),
                "color": category.symbol().color().name() if category.symbol() else None,
            }
            for category in renderer.categories()[:MAX_CATEGORIES]
        ]
    elif isinstance(renderer, QgsGraduatedSymbolRenderer):
        info["field"] = renderer.classAttribute()
        info["ranges"] = [
            {
                "min": item.lowerValue(),
                "max": item.upperValue(),
                "label": item.label(),
                "color": item.symbol().color().name() if item.symbol() else None,
            }
            for item in renderer.ranges()
        ]
    elif isinstance(renderer, QgsSingleSymbolRenderer) and renderer.symbol():
        info["color"] = renderer.symbol().color().name()
    if target.labelsEnabled() and target.labeling():
        settings = target.labeling().settings()
        info["label_field"] = settings.fieldName
    return info


@tool(
    level=Level.MODIFY,
    params={
        "layer": _LAYER,
        "fill_color": Param(
            type="string",
            description="Couleur de remplissage, par exemple #1a9641 ou vert_fonce.",
            required=False,
        ),
        "stroke_color": Param(type="string", description="Couleur du contour.", required=False),
        "stroke_width": Param(
            type="number",
            description="Épaisseur du contour en millimètres.",
            required=False,
            minimum=0,
            maximum=20,
        ),
        "pattern": Param(
            type="string",
            description="Motif de remplissage pour les polygones (solid, horizontal, "
                        "cross, diagonal_x, dense3...).",
            required=False,
        ),
        "shape": Param(
            type="string",
            description="Forme des points (circle, square, triangle, star...).",
            required=False,
        ),
        "size": Param(
            type="number",
            description="Taille des points en millimètres.",
            required=False,
            minimum=0.1,
            maximum=50,
        ),
        "opacity": Param(
            type="number",
            description="Opacité de 0 (transparent) à 1 (opaque).",
            required=False,
            default=1,
            minimum=0,
            maximum=1,
        ),
    },
)
def apply_single_style(
    layer: str,
    fill_color: str | None = None,
    stroke_color: str | None = None,
    stroke_width: float | None = None,
    pattern: str | None = None,
    shape: str | None = None,
    size: float | None = None,
    opacity: float = 1,
) -> dict:
    """Applique un symbole unique à toute une couche.

    Choisissez librement les couleurs et les motifs : ils sont vérifiés avant
    d'être transmis à QGIS. Le style précédent reste récupérable par undo_style.
    """
    target = resolve_layer(layer)
    kind = _geometry_kind(target)
    try:
        validated = specs.validate_symbol(
            {
                "fill_color": fill_color,
                "stroke_color": stroke_color,
                "stroke_width": stroke_width,
                "pattern": pattern,
                "shape": shape,
                "size": size,
                "opacity": opacity,
            },
            kind,
        )
    except ValueError as exc:
        raise ToolError("BAD_STYLE", str(exc)) from exc
    renderer = QgsSingleSymbolRenderer(_build_symbol(validated))
    result = _apply(target, renderer, "symbole unique")
    return {**result, "geometry": kind, "warnings": validated["warnings"]}


@tool(
    level=Level.MODIFY,
    params={
        "layer": _LAYER,
        "field": Param(
            type="string",
            description="Champ portant la catégorie à représenter.",
            required=True,
        ),
        "categories": Param(
            type="array",
            description='Catégories imposées : [{"value": "foret", "color": "#1a9641", '
                        '"label": "Forêt", "pattern": "solid"}]. Vide : couleurs automatiques.',
            required=False,
            items="object",
        ),
        "palette": _PALETTE,
        "colors": _COLORS,
        "reverse": Param(
            type="boolean",
            description="Inverser l'ordre des couleurs.",
            required=False,
            default=False,
        ),
        "stroke_color": Param(
            type="string", description="Couleur de contour commune.", required=False
        ),
        "stroke_width": Param(
            type="number",
            description="Épaisseur de contour commune en millimètres.",
            required=False,
            minimum=0,
            maximum=20,
        ),
        "opacity": Param(
            type="number",
            description="Opacité de 0 à 1.",
            required=False,
            default=1,
            minimum=0,
            maximum=1,
        ),
        "sort": Param(
            type="boolean",
            description="Trier les catégories par ordre alphabétique.",
            required=False,
            default=True,
        ),
    },
)
def apply_categorized_style(
    layer: str,
    field: str,
    categories: list | None = None,
    palette: str | None = None,
    colors: list | None = None,
    reverse: bool = False,
    stroke_color: str | None = None,
    stroke_width: float | None = None,
    opacity: float = 1,
    sort: bool = True,
) -> dict:
    """Colore une couche selon les valeurs d'un champ, une couleur par valeur.

    Convient aux types de paysage, aux natures de surface ou à tout champ
    qualitatif. Les valeurs présentes dans la couche sont lues automatiquement.
    """
    target = resolve_layer(layer)
    require_field(target, field)
    kind = _geometry_kind(target)

    values = _collect_values(target, field)
    distinct = []
    seen = set()
    for value in values:
        key = "" if value is None else str(value)
        if key not in seen:
            seen.add(key)
            distinct.append(key)
    if not distinct:
        raise ToolError("EMPTY_LAYER", f"Le champ « {field} » ne contient aucune valeur.")
    warnings: list[str] = []
    if len(distinct) > MAX_CATEGORIES:
        warnings.append(
            f"{len(distinct)} valeurs distinctes : seules les {MAX_CATEGORIES} "
            "premières sont représentées. Regroupez-les d'abord si nécessaire."
        )
        distinct = distinct[:MAX_CATEGORIES]
    if sort:
        distinct.sort()

    base = {"stroke_color": stroke_color, "stroke_width": stroke_width, "opacity": opacity}
    base = {key: value for key, value in base.items() if value is not None}
    try:
        built = specs.build_categories(
            distinct, kind, categories, palette, colors, base, reverse
        )
    except ValueError as exc:
        raise ToolError("BAD_STYLE", str(exc)) from exc

    renderer_categories = [
        QgsRendererCategory(entry["value"], _build_symbol(entry["symbol"]), entry["label"])
        for entry in built
    ]
    renderer = QgsCategorizedSymbolRenderer(field, renderer_categories)
    result = _apply(target, renderer, f"catégories sur « {field} »")
    return {
        **result,
        "field": field,
        "category_count": len(built),
        "categories": [
            {"value": entry["value"], "label": entry["label"], "color": entry["color"]}
            for entry in built
        ],
        "warnings": warnings,
    }


@tool(
    level=Level.MODIFY,
    params={
        "layer": _LAYER,
        "field": Param(
            type="string", description="Champ numérique à représenter.", required=True
        ),
        "method": Param(
            type="string",
            description="Méthode de calcul des seuils.",
            required=False,
            default="quantile",
            enum=list(METHODS),
        ),
        "classes": Param(
            type="integer",
            description="Nombre de classes souhaité.",
            required=False,
            default=5,
            minimum=2,
            maximum=20,
        ),
        "palette": _PALETTE,
        "colors": _COLORS,
        "reverse": Param(
            type="boolean", description="Inverser le dégradé.", required=False, default=False
        ),
        "decimals": Param(
            type="integer",
            description="Décimales affichées dans la légende.",
            required=False,
            default=2,
            minimum=0,
            maximum=6,
        ),
        "unit": Param(
            type="string",
            description="Unité ajoutée aux libellés, par exemple ha ou %.",
            required=False,
        ),
        "stroke_color": Param(type="string", description="Couleur de contour.", required=False),
        "stroke_width": Param(
            type="number",
            description="Épaisseur de contour en millimètres.",
            required=False,
            minimum=0,
            maximum=20,
        ),
        "opacity": Param(
            type="number", description="Opacité de 0 à 1.", required=False,
            default=1, minimum=0, maximum=1,
        ),
    },
)
def apply_graduated_style(
    layer: str,
    field: str,
    method: str = "quantile",
    classes: int = 5,
    palette: str | None = None,
    colors: list | None = None,
    reverse: bool = False,
    decimals: int = 2,
    unit: str | None = None,
    stroke_color: str | None = None,
    stroke_width: float | None = None,
    opacity: float = 1,
) -> dict:
    """Colore une couche en classes selon un champ numérique.

    Les seuils sont calculés par intervalles égaux, quantiles, seuils naturels
    de Jenks, écart-type ou bornes arrondies. Convient aux surfaces, aux
    coefficients et aux densités.
    """
    target = resolve_layer(layer)
    require_field(target, field)
    kind = _geometry_kind(target)

    values = _collect_values(target, field, numeric=True)
    try:
        classification = compute_breaks(values, method, int(classes))
    except ValueError as exc:
        raise ToolError("BAD_PARAM", str(exc)) from exc

    breaks = classification["breaks"]
    count = classification["class_count"]
    try:
        ramp = palette_store.resolve_colors(count, palette, colors, reverse)
    except ValueError as exc:
        raise ToolError("BAD_STYLE", str(exc)) from exc
    labels = range_labels(breaks, int(decimals), unit or "")

    ranges = []
    for index in range(count):
        spec = {
            "fill_color": ramp[index],
            "stroke_color": stroke_color,
            "stroke_width": stroke_width,
            "opacity": opacity,
        }
        validated = specs.validate_symbol(
            {key: value for key, value in spec.items() if value is not None}, kind
        )
        ranges.append(
            QgsRendererRange(
                breaks[index], breaks[index + 1], _build_symbol(validated), labels[index]
            )
        )
    renderer = QgsGraduatedSymbolRenderer(field, ranges)
    result = _apply(target, renderer, f"dégradé sur « {field} »")
    return {
        **result,
        "field": field,
        "method": classification["method"],
        "method_label": classification["method_label"],
        "class_count": count,
        "breaks": breaks,
        "legend": [
            {"label": labels[index], "color": ramp[index]} for index in range(count)
        ],
        "min": classification["min"],
        "max": classification["max"],
        "warnings": classification["warnings"],
    }


@tool(
    level=Level.MODIFY,
    params={
        "layer": _LAYER,
        "code_field": Param(
            type="string",
            description="Champ portant le code de nomenclature.",
            required=False,
            default="pays_code",
        ),
        "by": Param(
            type="string",
            description="Styliser par classe détaillée ou par grand poste.",
            required=False,
            default="class",
            enum=["class", "group"],
        ),
        "opacity": Param(
            type="number", description="Opacité de 0 à 1.", required=False,
            default=1, minimum=0, maximum=1,
        ),
        "stroke_color": Param(
            type="string", description="Couleur de contour.", required=False, default="#555555"
        ),
    },
)
def apply_landscape_style(
    layer: str,
    code_field: str = "pays_code",
    by: str = "class",
    opacity: float = 1,
    stroke_color: str = "#555555",
) -> dict:
    """Applique les couleurs de la nomenclature aux paysages classés.

    À utiliser sur une couche produite par classify_landscape : chaque type de
    paysage reçoit sa couleur de référence et son libellé complet. Les couleurs
    restent modifiables ensuite avec apply_categorized_style.
    """
    target = resolve_layer(layer)
    require_field(target, code_field)
    kind = _geometry_kind(target)

    values = _collect_values(target, code_field)
    distinct = sorted({str(value) for value in values if value is not None})
    if not distinct:
        raise ToolError(
            "EMPTY_LAYER",
            f"Le champ « {code_field} » est vide : la couche a-t-elle été classée "
            "par classify_landscape ?",
        )
    warnings: list[str] = []
    categories: list[dict] = []
    for code in distinct:
        item = nomenclature.get_class(code)
        if item is None:
            warnings.append(f"Code hors nomenclature ignoré pour le style : {code}")
            categories.append({"value": code, "color": "#cccccc", "label": f"{code} (inconnu)"})
            continue
        if by == "group":
            categories.append(
                {
                    "value": code,
                    "color": _group_color(item.group),
                    "label": nomenclature.GROUPS.get(item.group, item.group),
                }
            )
        else:
            categories.append(
                {"value": code, "color": item.color, "label": f"{item.code} {item.label}"}
            )

    built = specs.build_categories(
        [entry["value"] for entry in categories],
        kind,
        categories,
        base_symbol={"stroke_color": stroke_color, "stroke_width": 0.2, "opacity": opacity},
    )
    renderer = QgsCategorizedSymbolRenderer(
        code_field,
        [
            QgsRendererCategory(entry["value"], _build_symbol(entry["symbol"]), entry["label"])
            for entry in built
        ],
    )
    result = _apply(target, renderer, "nomenclature des paysages")
    return {
        **result,
        "code_field": code_field,
        "mode": by,
        "class_count": len(built),
        "legend": [{"label": entry["label"], "color": entry["color"]} for entry in built],
        "warnings": warnings,
    }


def _group_color(group: str) -> str:
    """Couleur de référence d'un grand poste de la nomenclature."""
    return {
        "1": "#d7191c", "2": "#ffd92f", "3": "#1a9641",
        "4": "#35978f", "5": "#2166ac",
    }.get(group, "#cccccc")


@tool(
    level=Level.MODIFY,
    params={
        "layer": _LAYER,
        "field": Param(
            type="string", description="Champ à afficher en étiquette.", required=False
        ),
        "expression": Param(
            type="string",
            description="Expression QGIS à afficher, par exemple "
                        '"nom" || \' (\' || round($area/10000,1) || \' ha)\'.',
            required=False,
        ),
        "enabled": Param(
            type="boolean",
            description="Faux pour retirer les étiquettes de la couche.",
            required=False,
            default=True,
        ),
        "font_size": Param(
            type="number", description="Taille de police en points.", required=False,
            default=9, minimum=2, maximum=72,
        ),
        "color": Param(
            type="string", description="Couleur du texte.", required=False, default="#000000"
        ),
        "bold": Param(type="boolean", description="Texte en gras.", required=False, default=False),
        "italic": Param(
            type="boolean", description="Texte en italique.", required=False, default=False
        ),
        "halo": Param(
            type="boolean",
            description="Contour clair autour du texte, pour la lisibilité.",
            required=False,
            default=True,
        ),
        "halo_color": Param(
            type="string",
            description="Couleur du halo. Déduite du texte si absente.",
            required=False,
        ),
        "halo_size": Param(
            type="number", description="Épaisseur du halo en millimètres.", required=False,
            default=1, minimum=0, maximum=10,
        ),
        "placement": Param(
            type="string",
            description="Position de l'étiquette.",
            required=False,
            default="libre",
            enum=list(specs.LABEL_PLACEMENTS),
        ),
        "min_scale": Param(
            type="number",
            description="Dénominateur d'échelle au-delà duquel les étiquettes "
                        "disparaissent, par exemple 50000.",
            required=False,
        ),
    },
)
def set_labels(
    layer: str,
    field: str | None = None,
    expression: str | None = None,
    enabled: bool = True,
    font_size: float = 9,
    color: str = "#000000",
    bold: bool = False,
    italic: bool = False,
    halo: bool = True,
    halo_color: str | None = None,
    halo_size: float = 1,
    placement: str = "libre",
    min_scale: float | None = None,
) -> dict:
    """Affiche ou retire les étiquettes d'une couche.

    Indiquez un champ ou une expression. Le halo clair autour du texte est
    activé par défaut : sans lui, les étiquettes deviennent illisibles sur les
    aplats sombres.
    """
    target = resolve_layer(layer)
    if not isinstance(target, QgsVectorLayer):
        raise ToolError("BAD_LAYER", "Seules les couches vecteur peuvent être étiquetées.")
    description = "étiquettes"
    if not enabled:
        _snapshot(target, "suppression des étiquettes")
        target.setLabelsEnabled(False)
        refresh_layer(target)
        return {"layer": target.name(), "labels_enabled": False, "warnings": []}

    if field:
        require_field(target, field)
    try:
        validated = specs.validate_labels(
            {
                "field": field,
                "expression": expression,
                "font_size": font_size,
                "color": color,
                "bold": bold,
                "italic": italic,
                "halo": halo,
                "halo_color": halo_color,
                "halo_size": halo_size,
                "placement": placement,
                "min_scale": min_scale,
            }
        )
    except ValueError as exc:
        raise ToolError("BAD_STYLE", str(exc)) from exc
    if expression:
        from .common import prepare_expression

        prepare_expression(expression, target)

    settings = QgsPalLayerSettings()
    if expression:
        settings.fieldName = expression
        settings.isExpression = True
    else:
        settings.fieldName = validated["field"]
        settings.isExpression = False

    text_format = QgsTextFormat()
    font = QFont(validated["font_family"])
    font.setBold(validated["bold"])
    font.setItalic(validated["italic"])
    text_format.setFont(font)
    text_format.setSize(validated["font_size"])
    text_format.setColor(_qcolor(validated["color"]))
    if validated["halo"]:
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(validated["halo_size"])
        buffer_settings.setColor(_qcolor(validated["halo_color"]))
        text_format.setBuffer(buffer_settings)
    settings.setFormat(text_format)

    placements = {
        "centre": QgsPalLayerSettings.Placement.OverPoint,
        "autour_du_point": QgsPalLayerSettings.Placement.AroundPoint,
        "le_long_de_la_ligne": QgsPalLayerSettings.Placement.Line,
        "horizontal": QgsPalLayerSettings.Placement.Horizontal,
        "libre": QgsPalLayerSettings.Placement.Free,
    }
    try:
        settings.placement = placements[validated["placement"]]
    except AttributeError:  # pragma: no cover - API antérieure
        settings.placement = 0
    if validated["min_scale"]:
        settings.scaleVisibility = True
        settings.minimumScale = float(validated["min_scale"])

    _snapshot(target, description)
    target.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    target.setLabelsEnabled(True)
    refresh_layer(target)
    return {
        "layer": target.name(),
        "labels_enabled": True,
        "source": expression or validated["field"],
        "font_size": validated["font_size"],
        "halo_color": validated["halo_color"],
        "undo_steps": HISTORY.depth(target.id()),
        "warnings": [],
    }


@tool(
    level=Level.MODIFY,
    params={
        "layer": Param(
            type="string",
            description="Couche concernée. Vide : dernière couche stylisée.",
            required=False,
        ),
        "steps": Param(
            type="integer",
            description="Nombre de modifications à annuler.",
            required=False,
            default=1,
            minimum=1,
            maximum=10,
        ),
    },
)
def undo_style(layer: str | None = None, steps: int = 1) -> dict:
    """Revient au style précédent d'une couche.

    Chaque stylisation est mémorisée : jusqu'à dix retours en arrière sont
    possibles par couche pendant la session.
    """
    if layer:
        target = resolve_layer(layer)
    else:
        last = HISTORY.last_layer()
        if last is None:
            return {
                "restored": 0,
                "warnings": ["Aucun style n'a été modifié depuis le démarrage de QGIS."],
            }
        target = resolve_layer(last)

    restored = 0
    description = ""
    for _ in range(int(steps)):
        snapshot = HISTORY.pop(target.id())
        if snapshot is None:
            break
        document = QDomDocument()
        document.setContent(snapshot.xml)
        message, ok = target.importNamedStyle(document)
        if not ok:
            raise ToolError("STYLE_FAILED", f"Restauration impossible : {message}")
        description = snapshot.description
        restored += 1
    refresh_layer(target)
    _refresh_legend(target)
    warnings = [] if restored else ["Aucun style antérieur mémorisé pour cette couche."]
    return {
        "layer": target.name(),
        "restored": restored,
        "undone": description,
        "remaining_steps": HISTORY.depth(target.id()),
        "warnings": warnings,
    }


@tool(
    level=Level.CREATE,
    params={
        "layer": _LAYER,
        "output_name": Param(
            type="string", description="Nom du fichier de style produit.", required=False
        ),
    },
)
def save_style_file(layer: str, output_name: str | None = None) -> dict:
    """Enregistre le style d'une couche dans un fichier QML réutilisable.

    Le fichier peut être appliqué à d'autres couches depuis QGIS, ou transmis
    au client avec les données.
    """
    from ..core.naming import sanitize_name, unique_name

    target = resolve_layer(layer)
    root, warnings = outputs_root()
    stem = sanitize_name(output_name or f"{target.name()}_style", "style")
    stem = unique_name(stem, lambda name: os.path.exists(os.path.join(root, name + ".qml")))
    path = os.path.join(root, stem + ".qml")
    message, ok = target.saveNamedStyle(path)
    if not ok:
        raise ToolError("WRITE_FAILED", f"Enregistrement du style impossible : {message}")
    return {"layer": target.name(), "path": path, "warnings": warnings}


@tool(
    level=Level.CREATE,
    params={
        "name": Param(type="string", description="Nom de la palette.", required=True),
        "colors": Param(
            type="array",
            description="Couleurs de la palette, de 2 à 30.",
            required=True,
            items="string",
        ),
    },
)
def save_palette(name: str, colors: list) -> dict:
    """Enregistre une palette de couleurs réutilisable.

    La palette devient disponible pour toutes les stylisations suivantes et
    reste enregistrée d'une session à l'autre.
    """
    try:
        key = palette_store.register_palette(name, colors)
    except ValueError as exc:
        raise ToolError("BAD_STYLE", str(exc)) from exc
    folder = os.path.join(os.path.expanduser("~"), ".cynogis")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "palettes.json")
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(palette_store.USER_PALETTES, handle, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise ToolError("WRITE_FAILED", f"Palette non enregistrée : {exc}") from exc
    return {
        "name": key,
        "colors": palette_store.USER_PALETTES[key],
        "path": path,
        "warnings": [],
    }
