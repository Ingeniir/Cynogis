from __future__ import annotations

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.territory import detect_territory
from .common import (
    add_to_memory,
    area_m2,
    distance_area,
    extent_wgs84,
    feature_request,
    geometry_kind,
    get_vector_layer,
    make_field,
    rect_to_list,
    require_field,
)
from .outputs import Steps, run_to_project, save_to_project

OUTPUT_NAME = Param("string", "Nom de la couche produite (défaut : opération_couche). Nettoyé, "
                    "jamais écrasé : un suffixe _2, _3… est ajouté si besoin.", required=False)
LOCATION_PREDICATES = ("intersects", "contains", "disjoint", "equals", "touches", "overlaps",
                       "within", "crosses")  # ordre = indices de native:extractbylocation
OVERLAYS = {"intersection": "native:intersection", "union": "native:union",
            "difference": "native:difference",
            "symmetric_difference": "native:symmetricaldifference", "clip": "native:clip"}
# Aires d'étude d'une étude d'impact : (code, libellé), de la plus proche à la plus large.
STUDY_AREAS = (("AEI", "Aire d'étude immédiate"), ("AER", "Aire d'étude rapprochée"),
               ("AEE", "Aire d'étude éloignée"))


def _name(output_name: str | None, operation: str, layer_name: str) -> str:
    return output_name or f"{operation}_{layer_name}"


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "output_name": OUTPUT_NAME,
})
def fix_geometries(layer_id: str, output_name: str | None) -> Steps:
    """Répare les géométries invalides (auto-intersections, anneaux mal fermés…) dans une
    nouvelle couche ; l'originale n'est pas modifiée. À lancer quand check_geometries signale
    des erreurs, avant toute superposition."""
    layer = get_vector_layer(layer_id)
    return (yield from run_to_project("native:fixgeometries", {"INPUT": layer},
                                      _name(output_name, "corrige", layer.name())))


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "target_crs": Param("string", "SCR cible, ex. EPSG:2975 (Réunion) ou EPSG:4471 (Mayotte). "
                        "Défaut : SCR de référence du territoire détecté.", required=False),
    "output_name": OUTPUT_NAME,
})
def reproject_layer(layer_id: str, target_crs: str | None, output_name: str | None) -> Steps:
    """Reprojette une couche vecteur dans un nouveau SCR (nouvelle couche)."""
    layer = get_vector_layer(layer_id)
    if target_crs is None:
        territory = detect_territory(rect_to_list(extent_wgs84(layer)))
        if territory is None:
            raise ToolError(ErrorCode.INVALID_PARAMS,
                            "Territoire non détecté : précise target_crs.")
        target_crs = territory.epsg
    crs = QgsCoordinateReferenceSystem(target_crs)
    if not crs.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS, f"SCR invalide : {target_crs}")
    name = _name(output_name, crs.authid().replace(":", "_"), layer.name())
    return (yield from run_to_project("native:reprojectlayer",
                                      {"INPUT": layer, "TARGET_CRS": crs}, name))


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur (layer_id), en SCR projeté."),
    "distance": Param("number", "Distance du tampon en mètres (négative : érosion des "
                      "polygones)."),
    "segments": Param("integer", "Segments par quart de cercle.", required=False, default=8,
                      minimum=1, maximum=100),
    "dissolve": Param("boolean", "Fusionner les tampons en une seule entité.", required=False,
                      default=False),
    "output_name": OUTPUT_NAME,
})
def buffer(layer_id: str, distance: float, segments: int, dissolve: bool,
           output_name: str | None) -> Steps:
    """Zone tampon autour des entités (nouvelle couche). Ex. : bande de 10 m autour des
    ravines. La distance est en mètres : la couche doit être dans un SCR projeté."""
    layer = get_vector_layer(layer_id)
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC,
                        f"{layer.name()} est en SCR géographique ({layer.crs().authid()}) : "
                        "reprojette-la d'abord avec reproject_layer.")
    return (yield from run_to_project("native:buffer",
                                      {"INPUT": layer, "DISTANCE": distance, "SEGMENTS": segments,
                                       "DISSOLVE": dissolve},
                                      _name(output_name, f"tampon_{distance:g}m", layer.name())))


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche du polygone projet (layer_id), en SCR projeté."),
    "immediate_m": Param("number", "Distance de l'aire d'étude immédiate autour du projet (m) ; "
                         "0 = emprise du projet.", required=False, default=100, minimum=0),
    "close_m": Param("number", "Distance de l'aire d'étude rapprochée (m).", required=False,
                     default=1000, minimum=0),
    "distant_m": Param("number", "Distance de l'aire d'étude éloignée (m).", required=False,
                       default=5000, minimum=0),
    "rings": Param("boolean", "Anneaux sans recouvrement (chaque aire exclut les plus proches), "
                   "pour mesurer des surfaces par aire. Défaut : aires imbriquées.",
                   required=False, default=False),
    "filter_expression": Param("string", "Entités formant le projet (défaut : toutes, "
                               "fusionnées).", required=False),
    "output_name": OUTPUT_NAME,
})
def create_study_area_buffers(layer_id: str, immediate_m: float, close_m: float,
                              distant_m: float, rings: bool, filter_expression: str | None,
                              output_name: str | None) -> ToolResult:
    """Aires d'étude immédiate (AEI), rapprochée (AER) et éloignée (AEE) autour d'un projet :
    une couche, une entité par aire (champs aire, libelle, distance_m, surface_ha). Les
    distances usuelles varient selon le type de projet et la thématique : les confirmer avec
    l'utilisateur."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC,
                        f"{layer.name()} est en SCR géographique ({layer.crs().authid()}) : "
                        "reprojette-la d'abord avec reproject_layer.")
    distances = (float(immediate_m), float(close_m), float(distant_m))
    if not distances[0] < distances[1] < distances[2]:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Distances attendues croissantes : "
                        "immédiate < rapprochée < éloignée.")
    geometries = [f.geometry() for f in layer.getFeatures(
        feature_request(layer, filter_expression, []))
        if not (f.geometry().isNull() or f.geometry().isEmpty())]
    if not geometries:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucun polygone projet trouvé.")
    project = QgsGeometry.unaryUnion(geometries).makeValid()

    fields = QgsFields()
    for spec in (("aire", "string", 3), ("libelle", "string", 40), ("distance_m", "real", 0),
                 ("surface_ha", "real", 0)):
        fields.append(make_field(*spec))
    memory = QgsMemoryProviderUtils.createMemoryLayer("aires", fields,
                                                      Qgis.WkbType.MultiPolygon, layer.crs())
    da = distance_area(layer.crs())
    areas = [project.buffer(d, 16) if d else project for d in distances]
    features, summary = [], []
    for index in reversed(range(len(areas))):  # la plus large d'abord : dessinée dessous
        geometry = areas[index].difference(areas[index - 1]) if rings and index else areas[index]
        geometry.convertToMultiType()
        code, label = STUDY_AREAS[index]
        hectares = round(area_m2(da, geometry) / 10_000.0, 2)
        feature = QgsFeature(fields)
        feature.setGeometry(geometry)
        feature.setAttributes([code, label, distances[index], hectares])
        features.append(feature)
        summary.append({"aire": code, "distance_m": distances[index], "surface_ha": hectares})
    notes = add_to_memory(memory, features)
    result = save_to_project(memory, _name(output_name, "aires_etude", layer.name()))
    result.warnings.extend(notes)
    result.data.update({"rings": bool(rings), "project_features": len(geometries),
                        "areas": summary[::-1]})
    return result

@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "fields": Param("array", "Champs de regroupement (défaut : tout fusionner en une entité).",
                    required=False, items="string"),
    "output_name": OUTPUT_NAME,
})
def dissolve(layer_id: str, fields: list[str] | None, output_name: str | None) -> Steps:
    """Fusionne les entités (nouvelle couche), globalement ou par valeur de champs.
    Ex. : une entité par type de paysage."""
    layer = get_vector_layer(layer_id)
    names = [require_field(layer, f) for f in fields or []]
    return (yield from run_to_project("native:dissolve", {"INPUT": layer, "FIELD": names},
                                      _name(output_name, "fusion", layer.name())))


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche dont on extrait des entités (layer_id)."),
    "expression": Param("string", "Extraction attributaire : expression QGIS, ex. "
                        "\"commune\" = 'Saint-Paul'.", required=False),
    "location_layer_id": Param("string", "Extraction spatiale : couche de comparaison.",
                               required=False),
    "predicates": Param("array", "Relations spatiales (extraction spatiale).", required=False,
                        default=["intersects"], items="string",
                        items_enum=LOCATION_PREDICATES),
    "output_name": OUTPUT_NAME,
})
def extract(layer_id: str, expression: str | None, location_layer_id: str | None,
            predicates: list[str], output_name: str | None) -> Steps:
    """Copie dans une nouvelle couche les entités qui vérifient une expression OU une relation
    spatiale avec une autre couche (un seul des deux modes)."""
    layer = get_vector_layer(layer_id)
    if (expression is None) == (location_layer_id is None):
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        "Fournis soit expression, soit location_layer_id (un seul).")
    name = _name(output_name, "extrait", layer.name())
    if expression is not None:
        return (yield from run_to_project("native:extractbyexpression",
                                          {"INPUT": layer, "EXPRESSION": expression}, name))
    if not predicates:
        raise ToolError(ErrorCode.INVALID_PARAMS, "predicates ne peut pas être vide.")
    return (yield from run_to_project(
        "native:extractbylocation",
        {"INPUT": layer, "INTERSECT": get_vector_layer(location_layer_id),
         "PREDICATE": [LOCATION_PREDICATES.index(p) for p in predicates]},
        name))


# Indices de native:joinattributesbylocation et native:joinbylocationsummary (pas de disjoint).
JOIN_PREDICATES = ("intersects", "contains", "equals", "touches", "overlaps", "within",
                   "crosses")
JOIN_METHODS = ("one_to_many", "first", "largest_overlap")
JOIN_SUMMARIES = ("count", "unique", "min", "max", "range", "sum", "mean", "median", "stddev",
                  "minority", "majority", "q1", "q3", "iqr", "empty", "filled")


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche qui reçoit les attributs (layer_id)."),
    "join_layer_id": Param("string", "Couche dont on récupère les attributs (layer_id)."),
    "predicates": Param("array", "Relations spatiales entre une entité de layer_id et une "
                        "entité de join_layer_id (within : layer_id dans join_layer_id).",
                        required=False, default=["intersects"], items="string",
                        items_enum=JOIN_PREDICATES),
    "fields": Param("array", "Champs de join_layer_id à joindre. Absent : tous.",
                    required=False, items="string"),
    "method": Param("string", "Sans summaries : one_to_many (une entité par correspondance, "
                    "entités dupliquées), first (première correspondance), largest_overlap "
                    "(correspondance de plus grand recouvrement, ex. commune majoritaire "
                    "d'une parcelle).", required=False, default="first", enum=JOIN_METHODS),
    "summaries": Param("array", "Mode résumé : statistiques des entités correspondantes par "
                       "entité (count, sum, mean, majority…), champs suffixés _count, _sum…",
                       required=False, items="string", items_enum=JOIN_SUMMARIES),
    "discard_nonmatching": Param("boolean", "Retire les entités sans correspondance.",
                                 required=False, default=False),
    "prefix": Param("string", "Préfixe des champs joints (sans summaries).", required=False),
    "output_name": OUTPUT_NAME,
})
def spatial_join(layer_id: str, join_layer_id: str, predicates: list[str],
                 fields: list[str] | None, method: str, summaries: list[str] | None,
                 discard_nonmatching: bool, prefix: str | None,
                 output_name: str | None) -> Steps:
    """Jointure spatiale (nouvelle couche) : chaque entité reçoit les attributs des entités
    d'une autre couche qui la touchent, la contiennent… (reprojection automatique). Ex. :
    commune et zonage PLU de chaque parcelle, habitat de chaque observation. Avec summaries :
    statistiques des entités correspondantes (nombre de points, somme, valeur majoritaire)."""
    layer = get_vector_layer(layer_id)
    join = get_vector_layer(join_layer_id)
    if not predicates:
        raise ToolError(ErrorCode.INVALID_PARAMS, "predicates ne peut pas être vide.")
    params = {"INPUT": layer, "JOIN": join,
              "PREDICATE": [JOIN_PREDICATES.index(p) for p in dict.fromkeys(predicates)],
              "JOIN_FIELDS": [require_field(join, f) for f in fields or []],
              "DISCARD_NONMATCHING": discard_nonmatching}
    name = _name(output_name, "jointure", layer.name())
    if summaries:
        params["SUMMARIES"] = [JOIN_SUMMARIES.index(s) for s in dict.fromkeys(summaries)]
        return (yield from run_to_project("native:joinbylocationsummary", params, name))
    params.update(METHOD=JOIN_METHODS.index(method), PREFIX=prefix or "")
    result = (yield from run_to_project("native:joinattributesbylocation", params, name))
    unjoinable = result.data["results"].get("UNJOINABLE_COUNT")
    if unjoinable:
        result.warnings.append(f"{unjoinable} entité(s) sans correspondance"
                               + (" retirée(s)." if discard_nonmatching
                                  else " : champs joints à NULL."))
    return result


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche en entrée (layer_id)."),
    "overlay_layer_id": Param("string", "Couche de superposition (layer_id)."),
    "operation": Param("string", "intersection (zones communes, attributs des deux couches), "
                       "union (tout, découpé aux limites), difference (entrée moins "
                       "superposition), symmetric_difference (zones couvertes par "
                       "une seule des deux couches), clip (entrée découpée par l'emprise de la "
                       "superposition, attributs de l'entrée seulement).",
                       enum=tuple(OVERLAYS)),
    "output_name": OUTPUT_NAME,
})
def overlay(layer_id: str, overlay_layer_id: str, operation: str,
            output_name: str | None) -> Steps:
    """Superposition de deux couches vecteur (nouvelle couche) : intersection, union,
    différence ou découpage. Lance check_geometries avant : les géométries invalides font
    échouer l'opération (fix_geometries pour les réparer)."""
    layer = get_vector_layer(layer_id)
    other = get_vector_layer(overlay_layer_id)
    return (yield from run_to_project(OVERLAYS[operation], {"INPUT": layer, "OVERLAY": other},
                                      _name(output_name, operation, layer.name())))
