"""Structures de style validées.

L'IA décrit un style sous forme de données ; ce module les vérifie et les
traduit en propriétés de symbole que QGIS sait lire directement. Aucun code
n'est jamais exécuté à partir de ce que l'IA produit.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .colors import parse_color, readable_text_color, to_rgba_string
from .palettes import resolve_colors

GEOMETRY_KINDS = ("polygon", "line", "point")

# Motifs de remplissage reconnus par QGIS, avec des alias en français.
FILL_PATTERNS = {
    "solid": "solid", "solide": "solid", "plein": "solid",
    "no": "no", "aucun": "no", "vide": "no", "transparent": "no",
    "horizontal": "horizontal", "hachures_horizontales": "horizontal",
    "vertical": "vertical", "hachures_verticales": "vertical",
    "cross": "cross", "croisillons": "cross", "quadrillage": "cross",
    "b_diagonal": "b_diagonal", "diagonale_montante": "b_diagonal",
    "f_diagonal": "f_diagonal", "diagonale_descendante": "f_diagonal",
    "diagonal_x": "diagonal_x", "croisillons_diagonaux": "diagonal_x",
    "dense1": "dense1", "dense2": "dense2", "dense3": "dense3", "dense4": "dense4",
    "dense5": "dense5", "dense6": "dense6", "dense7": "dense7",
}

MARKER_SHAPES = {
    "circle": "circle", "cercle": "circle", "rond": "circle",
    "square": "square", "carre": "square",
    "diamond": "diamond", "losange": "diamond",
    "triangle": "triangle",
    "equilateral_triangle": "equilateral_triangle",
    "pentagon": "pentagon", "pentagone": "pentagon",
    "hexagon": "hexagon", "hexagone": "hexagon",
    "star": "star", "etoile": "star",
    "cross": "cross", "croix": "cross",
    "cross2": "cross2", "croix_diagonale": "cross2",
    "arrow": "arrow", "fleche": "arrow",
    "half_square": "half_square",
}

LINE_STYLES = {
    "solid": "solid", "continu": "solid", "plein": "solid",
    "no": "no", "aucun": "no",
    "dash": "dash", "tirets": "dash",
    "dot": "dot", "pointilles": "dot",
    "dash_dot": "dash dot", "tiret_point": "dash dot",
    "dash_dot_dot": "dash dot dot", "tiret_point_point": "dash dot dot",
}

LABEL_PLACEMENTS = (
    "centre", "autour_du_point", "le_long_de_la_ligne", "horizontal", "libre"
)

DEFAULTS = {
    "polygon": {"fill_color": "#a6cee3", "stroke_color": "#404040", "stroke_width": 0.26},
    "line": {"stroke_color": "#2166ac", "stroke_width": 0.46},
    "point": {"fill_color": "#e41a1c", "stroke_color": "#ffffff",
              "stroke_width": 0.2, "size": 2.6},
}


def _lookup(table: Mapping[str, str], value, default: str, label: str) -> str:
    """Résout un motif par son nom, en français ou en anglais."""
    if value is None:
        return default
    key = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if key not in table:
        choices = ", ".join(sorted(set(table.values())))
        raise ValueError(f"{label} inconnu : {value}. Valeurs possibles : {choices}.")
    return table[key]


def _number(value, default: float, minimum: float, maximum: float, label: str) -> float:
    if value is None:
        return float(default)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} : nombre attendu, reçu {value!r}.") from exc
    if not minimum <= number <= maximum:
        raise ValueError(f"{label} doit être compris entre {minimum} et {maximum}.")
    return number


def normalize_geometry(kind) -> str:
    """Ramène un type de géométrie à polygon, line ou point."""
    text = str(kind).strip().lower()
    mapping = {
        "polygon": "polygon", "polygone": "polygon", "surfacique": "polygon", "2": "polygon",
        "line": "line", "ligne": "line", "lineaire": "line", "1": "line",
        "point": "point", "ponctuel": "point", "0": "point",
    }
    if text not in mapping:
        raise ValueError(f"Type de géométrie non stylisable : {kind}")
    return mapping[text]


def validate_symbol(spec: Mapping | None, geometry: str) -> dict:
    """Valide une description de symbole et la traduit pour QGIS.

    Renvoie un dictionnaire ``{"geometry", "properties", "opacity"}`` où
    ``properties`` est directement utilisable par les constructeurs de
    symboles simples de QGIS.
    """
    kind = normalize_geometry(geometry)
    data = {key: value for key, value in (spec or {}).items() if value is not None}
    defaults = DEFAULTS[kind]
    unknown = set(data) - {
        "fill_color", "color", "stroke_color", "stroke_width", "stroke_style",
        "pattern", "shape", "size", "angle", "opacity",
    }
    warnings = [f"Propriété de style ignorée : {name}" for name in sorted(unknown)]

    fill = data.get("fill_color", data.get("color", defaults.get("fill_color")))
    stroke = data.get("stroke_color", defaults.get("stroke_color"))
    opacity = _number(data.get("opacity"), 1.0, 0.0, 1.0, "L'opacité")

    if kind == "polygon":
        properties = {
            "color": to_rgba_string(fill),
            "outline_color": to_rgba_string(stroke),
            "outline_width": str(
                _number(data.get("stroke_width"), defaults["stroke_width"], 0.0, 20.0,
                        "L'épaisseur de contour")
            ),
            "outline_style": _lookup(LINE_STYLES, data.get("stroke_style"), "solid",
                                     "Style de contour"),
            "style": _lookup(FILL_PATTERNS, data.get("pattern"), "solid",
                             "Motif de remplissage"),
        }
    elif kind == "line":
        properties = {
            # « color » d'abord : c'est la clé posée par les catégories et les dégradés.
            "color": to_rgba_string(data.get("color", data.get("stroke_color",
                                                               defaults["stroke_color"]))),
            "width": str(
                _number(data.get("stroke_width"), defaults["stroke_width"], 0.0, 20.0,
                        "L'épaisseur de ligne")
            ),
            "line_style": _lookup(LINE_STYLES, data.get("stroke_style", data.get("pattern")),
                                  "solid", "Style de ligne"),
            "capstyle": "round",
            "joinstyle": "round",
        }
    else:
        properties = {
            "name": _lookup(MARKER_SHAPES, data.get("shape"), "circle", "Forme de point"),
            "color": to_rgba_string(fill),
            "outline_color": to_rgba_string(stroke),
            "outline_width": str(
                _number(data.get("stroke_width"), defaults["stroke_width"], 0.0, 10.0,
                        "L'épaisseur de contour")
            ),
            "size": str(_number(data.get("size"), defaults["size"], 0.1, 50.0,
                                "La taille du point")),
            "angle": str(_number(data.get("angle"), 0.0, 0.0, 360.0, "L'angle")),
        }
    return {
        "geometry": kind,
        "properties": properties,
        "opacity": opacity,
        "warnings": warnings,
    }


def build_categories(
    values: Sequence,
    geometry: str,
    categories: Sequence[Mapping] | None = None,
    palette: str | None = None,
    colors: Sequence | None = None,
    base_symbol: Mapping | None = None,
    reverse: bool = False,
) -> list[dict]:
    """Construit la liste des catégories à styliser.

    Si l'IA fournit des catégories explicites, elles priment ; sinon les
    couleurs sont tirées de la palette demandée, ou générées pour rester bien
    distinctes les unes des autres.
    """
    explicit = {}
    for entry in categories or []:
        if "value" not in entry:
            raise ValueError("Chaque catégorie doit comporter une clé « value ».")
        explicit[str(entry["value"])] = entry

    ordered = [str(value) if value is not None else "" for value in values]
    assigned = resolve_colors(len(ordered), palette, colors, reverse)

    result: list[dict] = []
    for index, value in enumerate(ordered):
        entry = explicit.get(value, {})
        spec = dict(base_symbol or {})
        spec.update(
            {key: entry[key] for key in ("pattern", "shape", "size", "stroke_color",
                                         "stroke_width", "opacity") if key in entry}
        )
        spec["color"] = entry.get("color", assigned[index])  # remplissage, ou trait des lignes
        symbol = validate_symbol(spec, geometry)
        result.append(
            {
                "value": value,
                "label": str(entry.get("label", value)) or "(vide)",
                "color": entry.get("color", assigned[index]),
                "symbol": symbol,
            }
        )
    return result


def validate_labels(spec: Mapping | None) -> dict:
    """Valide un paramétrage d'étiquettes.

    La couleur du halo est déduite de celle du texte si elle n'est pas
    précisée, afin que les étiquettes restent lisibles sur tout fond.
    """
    data = dict(spec or {})
    if not data.get("field") and not data.get("expression"):
        raise ValueError("Indiquez un champ ou une expression à afficher en étiquette.")
    color = data.get("color", "#000000")
    parse_color(color)
    halo_color = data.get("halo_color") or readable_text_color(color)
    placement = str(data.get("placement") or "libre").lower()
    if placement not in LABEL_PLACEMENTS:
        raise ValueError(
            f"Placement inconnu : {placement}. Valeurs possibles : "
            f"{', '.join(LABEL_PLACEMENTS)}."
        )
    return {
        "field": data.get("field"),
        "expression": data.get("expression"),
        "font_family": str(data.get("font_family") or "Arial"),
        "font_size": _number(data.get("font_size"), 9.0, 2.0, 72.0, "La taille de police"),
        "bold": bool(data.get("bold", False)),
        "italic": bool(data.get("italic", False)),
        "color": color,
        "halo": bool(data.get("halo", True)),
        "halo_color": halo_color,
        "halo_size": _number(data.get("halo_size"), 1.0, 0.0, 10.0, "La taille du halo"),
        "placement": placement,
        "min_scale": data.get("min_scale"),
        "max_scale": data.get("max_scale"),
    }


def describe_options() -> dict:
    """Catalogue des motifs et formes acceptés, destiné à l'IA."""
    return {
        "fill_patterns": sorted(set(FILL_PATTERNS.values())),
        "marker_shapes": sorted(set(MARKER_SHAPES.values())),
        "line_styles": sorted(set(LINE_STYLES.values())),
        "label_placements": list(LABEL_PLACEMENTS),
    }
