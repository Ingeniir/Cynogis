"""Édition vectorielle encadrée par le tampon d'édition de QGIS.

Toute modification reste en mémoire jusqu'à request_commit : l'opérateur voit les changements
à l'écran et peut les annuler d'un seul appel (rollback_edits).
"""
from __future__ import annotations

from typing import Any

from qgis.core import Qgis, QgsFeature, QgsProject, QgsVectorDataProvider, QgsVectorLayer

from ..core.dispatcher import ToolResult
from ..core.edits import JOURNAL, MAX_FEATURES_PER_CALL, check_batch_size, describe_summary
from ..core.errors import ErrorCode, ToolError
from ..core.fields import FIELD_TYPES, coerce_record, coerce_value, resolve_type, unique_field_name
from ..core.registry import Level, tool
from ..core.schema import Param
from ..ui.confirm import register_detail_provider
from .common import (
    begin_edit,
    feature_request,
    field_type_name,
    geometry_from_wkt,
    get_vector_layer,
    is_shapefile,
    layer_field_types,
    make_field,
    prepare_expression,
    refresh_layer,
    require_field,
    select_ids,
    source_path,
    to_json_value,
)

LAYER_ID = Param("string", "Couche vecteur (layer_id).")
OPTIONAL_LAYER_ID = Param("string", "Couche vecteur (layer_id). Absent : toutes les couches en "
                          "cours d'édition.", required=False)
FIELD_TYPE_NAMES = tuple(FIELD_TYPES)
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
    "geometry_crs": Param("string", "SCR des géométries fournies, ex. EPSG:4326. Défaut : "
                          "celui de la couche.", required=False),
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
    return describe_summary(JOURNAL.summary(lid))


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
