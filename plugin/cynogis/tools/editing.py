"""Édition vectorielle encadrée par le tampon d'édition de QGIS.

Toute modification reste en mémoire jusqu'à request_commit : l'opérateur voit les changements
à l'écran et peut les annuler d'un seul appel (rollback_edits).
"""
from __future__ import annotations

from typing import Any

from qgis.analysis import QgsGeometrySnapper  # bibliothèque d'analyse, pas qgis.core
from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeature,
    QgsFeatureRequest,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsPointXY,
    QgsProject,
    QgsRectangle,
    QgsVectorDataProvider,
    QgsVectorLayer,
    QgsWkbTypes,
)

from ..core.dispatcher import ToolResult
from ..core.edits import JOURNAL, MAX_FEATURES_PER_CALL, check_batch_size, describe_summary
from ..core.errors import ErrorCode, ToolError
from ..core.fields import FIELD_TYPES, coerce_record, coerce_value, resolve_type, unique_field_name
from ..core.registry import Level, tool
from ..core.schema import Param
from ..ui.confirm import register_detail_provider
from .common import (
    add_to_memory,
    area_m2,
    begin_edit,
    distance_area,
    feature_request,
    field_type_name,
    geometry_from_wkt,
    geometry_kind,
    get_vector_layer,
    is_shapefile,
    layer_field_types,
    length_m,
    make_field,
    prepare_expression,
    refresh_layer,
    require_field,
    select_ids,
    source_path,
    to_json_value,
    wkt_to_layer_crs,
)

LAYER_ID = Param("string", "Couche vecteur (layer_id).")
OPTIONAL_LAYER_ID = Param("string", "Couche vecteur (layer_id). Absent : toutes les couches en "
                          "cours d'édition.", required=False)
FIELD_TYPE_NAMES = tuple(FIELD_TYPES)
GEOMETRY_CRS = Param("string", "SCR des géométries fournies, ex. EPSG:4326. Défaut : celui de "
                     "la couche.", required=False)
NEXT_STEP = "request_commit pour enregistrer, rollback_edits pour annuler."
# QGIS >= 3.40 / 4.x : Qgis.VectorProviderCapability ; avant : QgsVectorDataProvider.Capability
Caps = getattr(Qgis, "VectorProviderCapability", None) or QgsVectorDataProvider.Capability


def _record(layer: QgsVectorLayer, operation: str, count: int, detail: str = "") -> int:
    """Trace l'opération dans le journal et renvoie le total en attente pour la couche."""
    JOURNAL.record(layer.id(), layer.name(), operation, count, detail)
    return JOURNAL.count_for(layer.id())


def _field_limit(layer: QgsVectorLayer) -> int:
    return 10 if is_shapefile(layer) else 63


def _editing_layers() -> list[QgsVectorLayer]:
    return [lyr for lyr in QgsProject.instance().mapLayers().values()
            if isinstance(lyr, QgsVectorLayer) and lyr.isEditable()]


def _targets(layer_id: str | None) -> list[QgsVectorLayer]:
    return [get_vector_layer(layer_id)] if layer_id else _editing_layers()


def _check_count(ids: list[int], max_features: int) -> None:
    if len(ids) > max_features:
        raise ToolError(ErrorCode.TOO_MANY_FEATURES,
                        f"Plus de {max_features} entités visées. Affine le filtre ou augmente "
                        "max_features en connaissance de cause.")


# --- État ---------------------------------------------------------------------------------
@tool(level=Level.READ, params={"layer_id": OPTIONAL_LAYER_ID})
def get_pending_edits(layer_id: str | None) -> ToolResult:
    """Modifications faites par l'IA et en attente de sauvegarde, par couche. À appeler avant
    request_commit pour vérifier ce qui sera écrit, et après une erreur pour faire le point."""
    project = QgsProject.instance()
    for known in JOURNAL.layer_ids():  # tampon fermé dans QGIS (annulé ou enregistré à la main)
        lyr = project.mapLayer(known)
        if lyr is None or not lyr.isEditable():
            JOURNAL.clear(known)
    lid = get_vector_layer(layer_id).id() if layer_id else None
    summary = JOURNAL.summary(lid)
    summary["human_readable"] = describe_summary(summary)
    journaled = set(JOURNAL.layer_ids())
    manual = [lyr.name() for lyr in _editing_layers()
              if lyr.isModified() and lyr.id() not in journaled and lid in (None, lyr.id())]
    warnings = [f"Modifications faites hors Cynogis (à la main) dans : {', '.join(manual)}. "
                "request_commit les enregistrera aussi."] if manual else []
    return ToolResult(summary, warnings)


# --- Champs -------------------------------------------------------------------------------
@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "name": Param("string", "Nom du champ (nettoyé, rendu unique ; 10 caractères max en "
                  "Shapefile)."),
    "field_type": Param("string", "Type du champ.", enum=FIELD_TYPE_NAMES),
    "length": Param("integer", "Longueur (texte, entier). 0 : défaut du type.", required=False,
                    default=0, minimum=0, maximum=255),
    "precision": Param("integer", "Décimales (réel). 0 : défaut du type.", required=False,
                       default=0, minimum=0, maximum=15),
})
def add_field(layer_id: str, name: str, field_type: str, length: int,
              precision: int) -> ToolResult:
    """Ajoute un champ à la table attributaire, dans le tampon d'édition (non enregistré)."""
    layer = get_vector_layer(layer_id)
    begin_edit(layer, Caps.AddAttributes, "l'ajout de champs")
    final = unique_field_name(name, layer.fields().names(), _field_limit(layer))
    warnings = [f"Champ nommé « {final} » au lieu de « {name} »."] if final != name else []
    spec = resolve_type(field_type)
    if is_shapefile(layer) and not spec.shapefile_ok:
        warnings.append(f"Le type {spec.label} n'existe pas en Shapefile : stockage approché.")
    if not layer.addAttribute(make_field(final, field_type, length, precision)):
        raise ToolError(ErrorCode.EDIT_FAILED, f"Ajout du champ « {final} » refusé par la couche.")
    layer.updateFields()
    pending = _record(layer, "add_field", 1, final)
    return ToolResult({"layer": layer.name(), "field": final, "type": spec.name,
                       "pending_edits": pending, "next_step": NEXT_STEP}, warnings)


@tool(level=Level.DESTROY, params={
    "layer_id": LAYER_ID,
    "name": Param("string", "Champ à supprimer."),
})
def delete_field(layer_id: str, name: str) -> ToolResult:
    """Supprime un champ et toutes ses valeurs (tampon d'édition ; définitif après
    request_commit). Confirmation humaine demandée."""
    layer = get_vector_layer(layer_id)
    field = require_field(layer, name)
    begin_edit(layer, Caps.DeleteAttributes, "la suppression de champs")
    if not layer.deleteAttribute(layer.fields().indexFromName(field)):
        raise ToolError(ErrorCode.EDIT_FAILED, f"Suppression du champ « {field} » refusée.")
    layer.updateFields()
    pending = _record(layer, "delete_field", 1, field)
    return ToolResult({"layer": layer.name(), "field": field, "pending_edits": pending,
                       "next_step": NEXT_STEP},
                      ["Le champ disparaîtra définitivement à l'enregistrement."])


# --- Entités ------------------------------------------------------------------------------
@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "features": Param("array", 'Entités à créer : [{"geometry": "WKT", "attributes": '
                      '{"champ": valeur}}]. Attributs absents = NULL.', items="object"),
    "geometry_crs": GEOMETRY_CRS,
})
def add_features(layer_id: str, features: list, geometry_crs: str | None) -> ToolResult:
    """Ajoute des entités (géométrie WKT + attributs) dans le tampon d'édition. Les valeurs
    sont converties au type des champs ; une erreur sur une entité annule tout le lot."""
    layer = get_vector_layer(layer_id)
    if not features:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune entité fournie.")
    try:
        check_batch_size(len(features))
    except ValueError as exc:
        raise ToolError(ErrorCode.TOO_MANY_FEATURES, str(exc)) from exc
    types = layer_field_types(layer)
    has_geometry = layer.geometryType() != Qgis.GeometryType.Null
    prepared: list[QgsFeature] = []
    no_geometry = 0
    for position, item in enumerate(features):  # tout valider avant d'ouvrir le tampon
        if not isinstance(item, dict):
            raise ToolError(ErrorCode.INVALID_PARAMS, f"Entité {position} : objet attendu.")
        try:
            attributes, _ = coerce_record(item.get("attributes") or {}, types, strict=True)
        except ValueError as exc:
            raise ToolError(ErrorCode.INVALID_PARAMS, f"Entité {position} : {exc}") from exc
        feature = QgsFeature(layer.fields())
        for key, value in attributes.items():
            feature.setAttribute(key, value)
        if item.get("geometry"):
            feature.setGeometry(geometry_from_wkt(item["geometry"], layer, geometry_crs))
        elif has_geometry:
            no_geometry += 1
        prepared.append(feature)

    begin_edit(layer, Caps.AddFeatures, "l'ajout d'entités")
    if not layer.addFeatures(prepared):
        raise ToolError(ErrorCode.EDIT_FAILED, "La couche a refusé l'ajout des entités.")
    refresh_layer(layer)
    pending = _record(layer, "add_features", len(prepared))
    warnings = [f"{no_geometry} entité(s) ajoutée(s) sans géométrie."] if no_geometry else []
    return ToolResult({"layer": layer.name(), "added": len(prepared), "pending_edits": pending,
                       "next_step": NEXT_STEP}, warnings)


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "values": Param("object", 'Valeurs à écrire, ex. {"type": "foret", "surface": 1200}.'),
    "expression": Param("string", 'Entités visées par une expression QGIS, ex. "type" IS NULL.',
                        required=False),
    "feature_ids": Param("array", "Entités visées par leur fid.", required=False,
                         items="integer"),
    "max_features": Param("integer", "Refus au-delà de ce nombre d'entités.", required=False,
                          default=500, minimum=1, maximum=MAX_FEATURES_PER_CALL),
})
def update_attributes(layer_id: str, values: dict, expression: str | None,
                      feature_ids: list | None, max_features: int) -> ToolResult:
    """Écrit les mêmes valeurs d'attributs sur un ensemble d'entités (tampon d'édition).
    Cible : expression OU feature_ids ; sans filtre, toute la couche (dans la limite de
    max_features)."""
    layer = get_vector_layer(layer_id)
    if not values:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune valeur à écrire.")
    try:
        converted, _ = coerce_record(values, layer_field_types(layer), strict=True)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    ids = select_ids(layer, expression, feature_ids, limit=max_features)
    _check_count(ids, max_features)
    if not ids:
        return ToolResult({"layer": layer.name(), "updated": 0},
                          ["Aucune entité ne correspond au filtre : rien n'a été modifié."])

    begin_edit(layer, Caps.ChangeAttributeValues, "la modification d'attributs")
    indexes = {name: layer.fields().indexFromName(name) for name in converted}
    changes = {fid: {indexes[name]: value for name, value in converted.items()} for fid in ids}
    if not layer.changeAttributeValues(changes):
        raise ToolError(ErrorCode.EDIT_FAILED, "La couche a refusé la modification des attributs.")
    refresh_layer(layer)
    pending = _record(layer, "update_attributes", len(ids), ", ".join(sorted(converted)))
    return ToolResult({"layer": layer.name(), "updated": len(ids), "fields": sorted(converted),
                       "pending_edits": pending, "next_step": NEXT_STEP})


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "field": Param("string", "Champ de destination, créé s'il n'existe pas."),
    "expression": Param("string", 'Expression QGIS, ex. round($area / 10000, 2) ou "a" / "b".'),
    "field_type": Param("string", "Type du champ s'il doit être créé.", required=False,
                        default="real", enum=FIELD_TYPE_NAMES),
    "filter_expression": Param("string", "Ne calculer que pour les entités qui la vérifient.",
                               required=False),
    "max_features": Param("integer", "Refus au-delà de ce nombre d'entités.", required=False,
                          default=MAX_FEATURES_PER_CALL, minimum=1,
                          maximum=MAX_FEATURES_PER_CALL),
})
def calculate_field(layer_id: str, field: str, expression: str, field_type: str,
                    filter_expression: str | None, max_features: int) -> ToolResult:
    """Calcule un champ à partir d'une expression QGIS (tampon d'édition). Le champ est créé
    s'il n'existe pas. $area et $length sont ellipsoïdaux en m² / m si le projet a un
    ellipsoïde, sinon en unités de la couche."""
    layer = get_vector_layer(layer_id)
    prepare_expression(expression, layer)
    _check_count(select_ids(layer, filter_expression, limit=max_features), max_features)
    warnings: list[str] = []

    index = layer.fields().lookupField(field)
    if index < 0:
        begin_edit(layer, Caps.AddAttributes, "l'ajout de champs")
        field = unique_field_name(field, layer.fields().names(), _field_limit(layer))
        if not layer.addAttribute(make_field(field, field_type)):
            raise ToolError(ErrorCode.EDIT_FAILED, f"Création du champ « {field} » refusée.")
        layer.updateFields()
        index = layer.fields().indexFromName(field)
        _record(layer, "add_field", 1, field)
        warnings.append(f"Champ « {field} » créé ({field_type}).")
    field = layer.fields().at(index).name()
    target_type = field_type_name(layer.fields().at(index))

    begin_edit(layer, Caps.ChangeAttributeValues, "le calcul de champ")
    compiled, context = prepare_expression(expression, layer)
    changes: dict[int, dict[int, Any]] = {}
    errors = nulls = 0
    for feature in layer.getFeatures(feature_request(layer, filter_expression)):
        context.setFeature(feature)
        value = to_json_value(compiled.evaluate(context))
        if compiled.hasEvalError():
            errors += 1
            continue
        try:
            changes[feature.id()] = {index: coerce_value(value, target_type)}
        except ValueError:
            errors += 1
            continue
        nulls += value is None

    if changes and not layer.changeAttributeValues(changes):
        raise ToolError(ErrorCode.EDIT_FAILED, "La couche a refusé les valeurs calculées.")
    refresh_layer(layer)
    pending = _record(layer, "calculate_field", len(changes), field)
    if errors:
        warnings.append(f"{errors} entité(s) non calculée(s) : erreur d'évaluation ou valeur "
                        f"incompatible avec le type {target_type}.")
    if nulls:
        warnings.append(f"{nulls} résultat(s) NULL.")
    if ("$area" in expression or "$length" in expression) and layer.crs().isGeographic():
        warnings.append("Couche en degrés : sans ellipsoïde de projet, $area/$length ne sont "
                        "pas en mètres. Préfère reproject_layer.")
    return ToolResult({"layer": layer.name(), "field": field, "updated": len(changes),
                       "errors": errors, "pending_edits": pending, "next_step": NEXT_STEP},
                      warnings)


@tool(level=Level.DESTROY, params={
    "layer_id": LAYER_ID,
    "expression": Param("string", "Entités à supprimer, par expression QGIS.", required=False),
    "feature_ids": Param("array", "Entités à supprimer, par fid.", required=False,
                         items="integer"),
    "max_features": Param("integer", "Refus au-delà de ce nombre d'entités.", required=False,
                          default=200, minimum=1, maximum=MAX_FEATURES_PER_CALL),
})
def delete_features(layer_id: str, expression: str | None, feature_ids: list | None,
                    max_features: int) -> ToolResult:
    """Supprime des entités (tampon d'édition, annulable par rollback_edits jusqu'à
    request_commit). Filtre obligatoire : expression ou feature_ids. Confirmation humaine."""
    layer = get_vector_layer(layer_id)
    if not expression and not feature_ids:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique expression ou feature_ids : vider "
                        "toute la couche n'est pas autorisé par cet outil.")
    ids = select_ids(layer, expression, feature_ids, limit=max_features)
    _check_count(ids, max_features)
    if not ids:
        return ToolResult({"layer": layer.name(), "deleted": 0},
                          ["Aucune entité ne correspond au filtre : rien n'a été supprimé."])
    total = layer.featureCount()
    begin_edit(layer, Caps.DeleteFeatures, "la suppression d'entités")
    if not layer.deleteFeatures(ids):
        raise ToolError(ErrorCode.EDIT_FAILED, "La couche a refusé la suppression.")
    refresh_layer(layer)
    pending = _record(layer, "delete_features", len(ids), expression or "liste de fid")
    warnings = ([f"{len(ids)} entités sur {total} supprimées : plus de la moitié de la couche."]
                if total and len(ids) >= total / 2 else [])
    return ToolResult({"layer": layer.name(), "deleted": len(ids),
                       "remaining": layer.featureCount(), "pending_edits": pending,
                       "next_step": NEXT_STEP}, warnings)


# --- Géométries ---------------------------------------------------------------------------
SNAP_MODES = {"vertices": QgsGeometrySnapper.SnapMode.PreferNodes,
              "closest": QgsGeometrySnapper.SnapMode.PreferClosest}
SNAP_LAYERS = Param("array", "Couches (layer_id) auxquelles accrocher les sommets, ex. "
                    "parcelles voisines. La couche éditée peut en faire partie : les entités "
                    "modifiées sont alors exclues de la référence. Absent : pas d'accrochage.",
                    required=False, items="string")
SNAP_TOLERANCE = Param("number", "Distance d'accrochage en mètres (couche en SCR projeté).",
                       required=False, default=0.5, minimum=0.001, maximum=50)
SNAP_MODE = Param("string", "vertices : sommets voisins d'abord (limites communes propres) ; "
                  "closest : point le plus proche, sommet ou segment.", required=False,
                  default="vertices", enum=tuple(SNAP_MODES))
STALE_FIELDS = ("Les champs de surface ou de longueur déjà calculés (ex. pays_surf) ne sont pas "
                "mis à jour : relance calculate_field si besoin.")


def _measure(layer: QgsVectorLayer, geometry: QgsGeometry) -> float | None:
    """Surface (m²) ou longueur (m) ellipsoïdale, None pour des points ou sans SCR."""
    kind = geometry_kind(layer)
    if kind not in ("polygon", "line") or not layer.crs().isValid():
        return None
    da = distance_area(layer.crs())
    return round(area_m2(da, geometry) if kind == "polygon" else length_m(da, geometry), 2)


def _conform(geometry: QgsGeometry, layer: QgsVectorLayer) -> QgsGeometry:
    """Géométrie valide, du type et de la multiplicité de la couche, sinon INVALID_GEOMETRY."""
    if not geometry.isGeosValid():
        geometry = geometry.makeValid()
    converted = geometry.convertToType(layer.geometryType(),
                                       QgsWkbTypes.isMultiType(layer.wkbType()))
    if converted is None or converted.isNull() or converted.isEmpty():
        raise ToolError(ErrorCode.INVALID_GEOMETRY,
                        f"Résultat incompatible avec « {layer.name()} » "
                        f"({QgsWkbTypes.displayString(layer.wkbType())}) : géométrie vide, "
                        "d'un autre type, ou en plusieurs parties dans une couche à parties "
                        "simples.")
    return converted


def _geometries(layer: QgsVectorLayer, ids: list[int]) -> dict[int, QgsGeometry]:
    """Copies des géométries (état du tampon d'édition compris), sans les géométries vides."""
    request = QgsFeatureRequest().setFilterFids(ids)
    request.setNoAttributes()
    return {f.id(): QgsGeometry(f.geometry()) for f in layer.getFeatures(request)
            if not f.geometry().isNull() and not f.geometry().isEmpty()}


def _reference_subset(reference: QgsVectorLayer, layer: QgsVectorLayer, area: QgsRectangle,
                      exclude: set[int]) -> QgsVectorLayer:
    """Entités de reference proches de area, dans le SCR de layer, en couche mémoire.

    QgsGeometrySnapper indexe toute sa source : un extrait local évite d'indexer une couche
    entière à chaque appel.
    """
    to_layer = None
    request_area = area
    if reference.crs() != layer.crs():
        to_layer = QgsCoordinateTransform(reference.crs(), layer.crs(), QgsProject.instance())
        request_area = to_layer.transformBoundingBox(area, Qgis.TransformDirection.Reverse)
    request = QgsFeatureRequest().setFilterRect(request_area)
    request.setNoAttributes()
    subset = QgsMemoryProviderUtils.createMemoryLayer(
        "snap_reference", QgsFields(), QgsWkbTypes.multiType(reference.wkbType()), layer.crs())
    features = []
    for feature in reference.getFeatures(request):
        geometry = QgsGeometry(feature.geometry())
        if feature.id() in exclude or geometry.isNull() or geometry.isEmpty():
            continue
        if to_layer is not None:
            try:
                geometry.transform(to_layer)
            except QgsCsException:
                continue
        geometry.convertToMultiType()
        copy = QgsFeature()
        copy.setGeometry(geometry)
        features.append(copy)
    add_to_memory(subset, features)
    return subset


def _snap(layer: QgsVectorLayer, geometries: dict[int, QgsGeometry],
          reference_ids: list | None, tolerance: float, mode: str) -> set[int]:
    """Accroche geometries (remplacées sur place) aux couches de référence ; renvoie les fid
    effectivement modifiés."""
    if not reference_ids or not geometries:
        return set()
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC,
                        f"{layer.name()} est en degrés : la tolérance d'accrochage en mètres "
                        "exige un SCR projeté (reproject_layer).")
    area = QgsRectangle()
    for geometry in geometries.values():
        area.combineExtentWith(geometry.boundingBox())
    area.grow(tolerance)
    changed: set[int] = set()
    for reference_id in dict.fromkeys(reference_ids):
        reference = get_vector_layer(reference_id)
        exclude = set(geometries) if reference.id() == layer.id() else set()
        subset = _reference_subset(reference, layer, area, exclude)
        if subset.featureCount() == 0:
            continue
        snapper = QgsGeometrySnapper(subset)
        for fid, geometry in geometries.items():
            snapped = snapper.snapGeometry(geometry, tolerance, SNAP_MODES[mode])
            if not snapped.isNull() and not snapped.equals(geometry):
                geometries[fid] = snapped
                changed.add(fid)
    return changed


def _change_geometries(layer: QgsVectorLayer, geometries: dict[int, QgsGeometry]) -> None:
    begin_edit(layer, Caps.ChangeGeometries, "la modification de géométries")
    for fid, geometry in geometries.items():
        if not layer.changeGeometry(fid, geometry):
            raise ToolError(ErrorCode.EDIT_FAILED, f"Géométrie de l'entité {fid} refusée par la "
                            "couche (rollback_edits pour annuler les modifications partielles).")
    refresh_layer(layer)


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "feature_id": Param("integer", "fid de l'entité à modifier."),
    "geometry": Param("string", "Nouvelle géométrie en WKT (même type que la couche)."),
    "geometry_crs": GEOMETRY_CRS,
    "snap_layer_ids": SNAP_LAYERS,
    "snap_tolerance_m": SNAP_TOLERANCE,
    "snap_mode": SNAP_MODE,
})
def update_geometry(layer_id: str, feature_id: int, geometry: str, geometry_crs: str | None,
                    snap_layer_ids: list | None, snap_tolerance_m: float,
                    snap_mode: str) -> ToolResult:
    """Remplace la géométrie d'une entité (tampon d'édition), attributs inchangés. Avec
    snap_layer_ids, les sommets proches des couches voisines y sont accrochés : pas de trou ni
    de chevauchement le long des limites communes."""
    layer = get_vector_layer(layer_id)
    before = _geometries(layer, select_ids(layer, None, [feature_id])).get(feature_id)
    new = {feature_id: geometry_from_wkt(geometry, layer, geometry_crs)}
    snapped = _snap(layer, new, snap_layer_ids, snap_tolerance_m, snap_mode)
    final = {feature_id: _conform(new[feature_id], layer)}
    _change_geometries(layer, final)
    pending = _record(layer, "update_geometry", 1, f"fid {feature_id}")
    return ToolResult({"layer": layer.name(), "feature_id": feature_id,
                       "snapped": bool(snapped),
                       "measure_before": _measure(layer, before) if before else None,
                       "measure_after": _measure(layer, final[feature_id]),
                       "pending_edits": pending, "next_step": NEXT_STEP}, [STALE_FIELDS])


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "dx_m": Param("number", "Décalage vers l'est en mètres (négatif : vers l'ouest)."),
    "dy_m": Param("number", "Décalage vers le nord en mètres (négatif : vers le sud)."),
    "expression": Param("string", "Entités à déplacer, par expression QGIS.", required=False),
    "feature_ids": Param("array", "Entités à déplacer, par fid.", required=False,
                         items="integer"),
    "max_features": Param("integer", "Refus au-delà de ce nombre d'entités.", required=False,
                          default=200, minimum=1, maximum=MAX_FEATURES_PER_CALL),
    "snap_layer_ids": SNAP_LAYERS,
    "snap_tolerance_m": SNAP_TOLERANCE,
    "snap_mode": SNAP_MODE,
})
def move_features(layer_id: str, dx_m: float, dy_m: float, expression: str | None,
                  feature_ids: list | None, max_features: int, snap_layer_ids: list | None,
                  snap_tolerance_m: float, snap_mode: str) -> ToolResult:
    """Déplace des entités d'un décalage en mètres (tampon d'édition), ex. recaler un levé sur
    le cadastre. Filtre obligatoire. Accrochage optionnel aux couches voisines après le
    déplacement."""
    layer = get_vector_layer(layer_id)
    if not expression and not feature_ids:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique expression ou feature_ids.")
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{layer.name()} est en degrés : un décalage "
                        "en mètres exige un SCR projeté (reproject_layer).")
    if dx_m == 0 and dy_m == 0 and not snap_layer_ids:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Décalage nul et pas d'accrochage : rien à "
                        "faire.")
    ids = select_ids(layer, expression, feature_ids, limit=max_features)
    _check_count(ids, max_features)
    geometries = _geometries(layer, ids)
    if not geometries:
        return ToolResult({"layer": layer.name(), "moved": 0},
                          ["Aucune entité (avec géométrie) ne correspond : rien n'a bougé."])
    for geometry in geometries.values():
        geometry.translate(dx_m, dy_m)
    snapped = _snap(layer, geometries, snap_layer_ids, snap_tolerance_m, snap_mode)
    _change_geometries(layer, {fid: _conform(g, layer) for fid, g in geometries.items()})
    pending = _record(layer, "move_features", len(geometries), f"dx={dx_m:g} m, dy={dy_m:g} m")
    return ToolResult({"layer": layer.name(), "moved": len(geometries), "dx_m": dx_m,
                       "dy_m": dy_m, "snapped": len(snapped), "pending_edits": pending,
                       "next_step": NEXT_STEP})


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "feature_id": Param("integer", "fid de l'entité (polygone ou ligne) à découper."),
    "split_line": Param("string", "Ligne de découpe en WKT, ex. LINESTRING(x1 y1, x2 y2) ; elle "
                        "doit traverser l'entité de part en part."),
    "geometry_crs": GEOMETRY_CRS,
})
def split_feature(layer_id: str, feature_id: int, split_line: str,
                  geometry_crs: str | None) -> ToolResult:
    """Découpe une entité par une ligne (tampon d'édition) : la première partie garde le fid,
    les autres deviennent de nouvelles entités aux mêmes attributs (identifiant de la source
    remis à NULL). Seule l'entité désignée est découpée, jamais ses voisines."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) not in ("polygon", "line"):
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} : seuls les polygones et les "
                        "lignes se découpent.")
    line = wkt_to_layer_crs(split_line, layer, geometry_crs)
    if line.type() != Qgis.GeometryType.Line or line.isMultipart():
        raise ToolError(ErrorCode.INVALID_GEOMETRY, "split_line doit être une LINESTRING simple.")
    points = [QgsPointXY(vertex.x(), vertex.y()) for vertex in line.vertices()]
    select_ids(layer, None, [feature_id])
    feature = layer.getFeature(feature_id)
    geometry = QgsGeometry(feature.geometry())
    outcome, parts, _ = geometry.splitGeometry(points, False)
    if outcome == Qgis.GeometryOperationResult.NothingHappened or not parts:
        return ToolResult({"layer": layer.name(), "feature_id": feature_id, "parts": 1},
                          ["La ligne ne traverse pas l'entité de part en part : rien n'a été "
                           "découpé."])
    if outcome != Qgis.GeometryOperationResult.Success:
        raise ToolError(ErrorCode.INVALID_GEOMETRY, f"Découpe impossible ({outcome}) : "
                        "géométrie invalide ? (fix_geometries)")
    pieces = [_conform(piece, layer) for piece in (geometry, *parts)]

    attributes = feature.attributes()
    for index in layer.dataProvider().pkAttributeIndexes():  # ex. fid d'un GeoPackage
        attributes[index] = None
    new_features = []
    for piece in pieces[1:]:
        new = QgsFeature(layer.fields())
        new.setAttributes(list(attributes))
        new.setGeometry(piece)
        new_features.append(new)
    _change_geometries(layer, {feature_id: pieces[0]})
    begin_edit(layer, Caps.AddFeatures, "l'ajout d'entités")
    if not layer.addFeatures(new_features):
        raise ToolError(ErrorCode.EDIT_FAILED, "Parties découpées refusées par la couche "
                        "(rollback_edits pour annuler).")
    refresh_layer(layer)
    pending = _record(layer, "split_feature", 1, f"fid {feature_id} → {len(pieces)} parties")
    return ToolResult({"layer": layer.name(), "feature_id": feature_id, "parts": len(pieces),
                       "measures": [_measure(layer, piece) for piece in pieces],
                       "pending_edits": pending, "next_step": NEXT_STEP}, [STALE_FIELDS])


@tool(level=Level.DESTROY, params={
    "layer_id": LAYER_ID,
    "feature_ids": Param("array", "fid des entités à fusionner (au moins 2).", items="integer"),
    "keep_attributes_from": Param("integer", "fid dont les attributs sont conservés. Défaut : "
                                  "la plus grande entité (surface ou longueur).",
                                  required=False),
})
def merge_features(layer_id: str, feature_ids: list, keep_attributes_from: int | None
                   ) -> ToolResult:
    """Fusionne des entités en une seule (tampon d'édition) : géométries unies, attributs d'une
    seule entité conservés, les autres supprimées. Confirmation humaine demandée."""
    layer = get_vector_layer(layer_id)
    ids = list(dict.fromkeys(int(fid) for fid in feature_ids or []))
    if len(ids) < 2:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique au moins deux fid distincts.")
    _check_count(ids, MAX_FEATURES_PER_CALL)
    geometries = _geometries(layer, select_ids(layer, None, ids))
    if len(geometries) < 2:
        raise ToolError(ErrorCode.INVALID_GEOMETRY, "Moins de deux entités ont une géométrie.")
    if keep_attributes_from is not None and keep_attributes_from not in ids:
        raise ToolError(ErrorCode.INVALID_PARAMS, "keep_attributes_from doit figurer dans "
                        "feature_ids.")
    keeper = keep_attributes_from if keep_attributes_from is not None else max(
        geometries, key=lambda fid: _measure(layer, geometries[fid]) or 0.0)

    merged = QgsGeometry.unaryUnion(list(geometries.values()))
    if geometry_kind(layer) == "line" and not merged.isNull():
        merged = merged.mergeLines()  # tronçons bout à bout → une seule ligne
    if merged.isNull() or merged.isEmpty():
        raise ToolError(ErrorCode.INVALID_GEOMETRY, "Union impossible : géométries invalides ? "
                        "(fix_geometries)")
    final = _conform(merged, layer)
    others = [fid for fid in ids if fid != keeper]

    _change_geometries(layer, {keeper: final})
    begin_edit(layer, Caps.DeleteFeatures, "la suppression d'entités")
    if not layer.deleteFeatures(others):
        raise ToolError(ErrorCode.EDIT_FAILED, "Suppression des entités fusionnées refusée "
                        "(rollback_edits pour annuler).")
    refresh_layer(layer)
    pending = _record(layer, "merge_features", 1, f"{len(ids)} entités → fid {keeper}")
    warnings = [STALE_FIELDS]
    if final.isMultipart() and len(final.asGeometryCollection()) > 1:
        warnings.append("Entités non contiguës : le résultat est en plusieurs parties.")
    return ToolResult({"layer": layer.name(), "kept_feature_id": keeper,
                       "deleted_feature_ids": others, "measure": _measure(layer, final),
                       "pending_edits": pending, "next_step": NEXT_STEP}, warnings)


@tool(level=Level.MODIFY, params={
    "layer_id": LAYER_ID,
    "reference_layer_ids": Param("array", "Couches voisines (layer_id) de référence. La couche "
                                 "éditée peut en faire partie : les entités visées sont alors "
                                 "accrochées aux autres entités de la couche.", items="string"),
    "tolerance_m": SNAP_TOLERANCE,
    "mode": SNAP_MODE,
    "expression": Param("string", "Entités à accrocher, par expression QGIS.", required=False),
    "feature_ids": Param("array", "Entités à accrocher, par fid.", required=False,
                         items="integer"),
    "max_features": Param("integer", "Refus au-delà de ce nombre d'entités.", required=False,
                          default=500, minimum=1, maximum=MAX_FEATURES_PER_CALL),
})
def snap_features(layer_id: str, reference_layer_ids: list, tolerance_m: float, mode: str,
                  expression: str | None, feature_ids: list | None,
                  max_features: int) -> ToolResult:
    """Accroche les sommets des entités aux couches voisines dans la tolérance (tampon
    d'édition) : supprime micro-trous et micro-chevauchements le long des limites communes
    (parcelles, limites communales). Sans filtre : toute la couche, dans max_features."""
    layer = get_vector_layer(layer_id)
    ids = select_ids(layer, expression, feature_ids, limit=max_features)
    _check_count(ids, max_features)
    geometries = _geometries(layer, ids)
    snapped = _snap(layer, geometries, reference_layer_ids, tolerance_m, mode)
    if not snapped:
        return ToolResult({"layer": layer.name(), "checked": len(geometries), "snapped": 0},
                          [f"Aucun sommet à moins de {tolerance_m:g} m des couches de "
                           "référence : rien n'a changé."])
    _change_geometries(layer, {fid: _conform(geometries[fid], layer) for fid in snapped})
    pending = _record(layer, "snap_features", len(snapped), f"tolérance {tolerance_m:g} m")
    return ToolResult({"layer": layer.name(), "checked": len(geometries),
                       "snapped": len(snapped), "snapped_ids": sorted(snapped)[:200],
                       "pending_edits": pending, "next_step": NEXT_STEP})


# --- Enregistrement et annulation ---------------------------------------------------------
@tool(level=Level.MODIFY, params={"layer_id": OPTIONAL_LAYER_ID})
def rollback_edits(layer_id: str | None) -> ToolResult:
    """Annule les modifications en attente et ferme le tampon d'édition. Les fichiers ne sont
    pas touchés : retour à l'état du dernier enregistrement."""
    rolled = []
    for layer in _targets(layer_id):
        discarded = JOURNAL.summary(layer.id())
        if layer.isEditable():
            layer.rollBack()
        JOURNAL.clear(layer.id())
        refresh_layer(layer)
        rolled.append({"layer": layer.name(), "discarded_operations": discarded["total_operations"],
                       "detail": describe_summary(discarded)})
    return ToolResult({"rolled_back": rolled, "layer_count": len(rolled)},
                      [] if rolled else ["Aucune couche n'était en cours d'édition."])


@tool(level=Level.DESTROY, params={
    "layer_id": OPTIONAL_LAYER_ID,
    "keep_editing": Param("boolean", "Rester en mode édition après l'enregistrement.",
                          required=False, default=False),
})
def request_commit(layer_id: str | None, keep_editing: bool) -> ToolResult:
    """Enregistre définitivement sur le disque les modifications en attente. Une fenêtre
    récapitule les changements et l'opérateur valide ou refuse. En cas d'échec, le tampon
    reste intact."""
    committed, failures = [], []
    for layer in _targets(layer_id):
        if not layer.isEditable():
            continue
        summary = JOURNAL.summary(layer.id())
        if layer.commitChanges(not keep_editing):
            JOURNAL.clear(layer.id())
            committed.append({"layer": layer.name(), "path": source_path(layer),
                              "operations": summary["total_operations"],
                              "detail": describe_summary(summary),
                              "feature_count": layer.featureCount()})
        else:
            failures.append({"layer": layer.name(),
                             "errors": [str(m) for m in layer.commitErrors()][:5]})
        refresh_layer(layer)
    messages = [f"{f['layer']} : {' / '.join(f['errors'])}" for f in failures]
    if failures and not committed:
        raise ToolError(ErrorCode.COMMIT_FAILED,
                        f"Enregistrement impossible. {'; '.join(messages)}. Les modifications "
                        "restent en attente : corrige puis relance, ou rollback_edits.")
    warnings = [f"Échec : {m}" for m in messages]
    if not committed and not failures:
        warnings.append("Aucune couche en cours d'édition : rien à enregistrer.")
    return ToolResult({"committed": committed, "layer_count": len(committed)}, warnings,
                      [c["path"] for c in committed if c["path"]])


# --- Détail de la fenêtre de confirmation (niveau DESTROY) --------------------------------
def _commit_details(params: dict) -> list[str]:
    lid = get_vector_layer(params["layer_id"]).id() if params.get("layer_id") else None
    summary = JOURNAL.summary(lid)
    # commitChanges enregistre tout le tampon, y compris ce que l'opérateur a saisi à la main.
    tracked = {bucket["layer_id"] for bucket in summary["layers"]}
    untracked = [f"⚠ {layer.name()} : modifications faites hors Cynogis, enregistrées aussi."
                 for layer in _targets(lid)
                 if layer.isModified() and layer.id() not in tracked]
    return [*untracked, *describe_summary(summary)]


def _delete_features_details(params: dict) -> list[str]:
    layer = get_vector_layer(params["layer_id"])
    ids = select_ids(layer, params.get("expression"), params.get("feature_ids"),
                     limit=params.get("max_features"))
    lines = [f"Couche : {layer.name()}", f"Entités visées : {len(ids)}"]
    if params.get("expression"):
        lines.append(f"Filtre : {params['expression']}")
    return lines


def _delete_field_details(params: dict) -> list[str]:
    layer = get_vector_layer(params["layer_id"])
    return [f"Couche : {layer.name()}", f"Champ supprimé : {params.get('name')}",
            f"Valeurs perdues : {layer.featureCount()}"]


register_detail_provider("request_commit", _commit_details)
register_detail_provider("delete_features", _delete_features_details)
register_detail_provider("delete_field", _delete_field_details)


def _merge_details(params: dict) -> list[str]:
    layer = get_vector_layer(params["layer_id"])
    ids = list(dict.fromkeys(params.get("feature_ids") or []))
    keeper = params.get("keep_attributes_from")
    return [f"Couche : {layer.name()}", f"{len(ids)} entités fusionnées en une : {ids[:20]}",
            f"Attributs conservés : fid {keeper}" if keeper is not None
            else "Attributs conservés : la plus grande entité",
            f"{max(len(ids) - 1, 0)} entité(s) supprimée(s)."]


register_detail_provider("merge_features", _merge_details)
