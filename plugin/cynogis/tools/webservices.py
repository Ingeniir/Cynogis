"""Services web WMS / WFS du catalogue (core/webservices.py) : découverte et ajout au projet."""
from __future__ import annotations

import json
import logging
from typing import Any

from qgis.core import (
    QgsDataSourceUri,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.jobs import Fetch
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.territory import NATURA2000_MESSAGE, is_natura2000_layer
from ..core.webservices import (
    MAX_FEATURES_LIMIT,
    SERVICES_FILE,
    WebService,
    capabilities_url,
    catalog,
    choose_crs,
    parse_capabilities,
    search_layers,
    wfs_params,
    wms_params,
)
from .common import get_layer
from .outputs import Steps, add_to_group, run_to_project

logger = logging.getLogger("cynogis.webservices")
# GetCapabilities par service (plusieurs Mo pour la Géoplateforme) : vidé au rechargement.
_CAPABILITIES: dict[str, list[dict[str, Any]]] = {}


def _catalog() -> tuple[dict[str, WebService], list[str]]:
    """Relu à chaque appel : une modification du fichier est prise en compte sans recharger."""
    data, warnings = None, []
    if SERVICES_FILE.exists():
        try:
            data = json.loads(SERVICES_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            warnings.append(f"{SERVICES_FILE} illisible ({exc}) : catalogue intégré seul.")
    services, rejected = catalog(data)
    warnings += [f"Service ignoré, {reason}" for reason in rejected]
    return services, warnings


def _service(service_id: str) -> tuple[WebService, list[str]]:
    services, warnings = _catalog()
    if service_id not in services:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Service inconnu : {service_id}.",
                        {"services": sorted(services)})
    return services[service_id], warnings


def _layers(service: WebService, refresh: bool = False) -> Steps:
    """Couches du service (list[dict]) : GetCapabilities téléchargé hors du thread principal
    (tools/tasks.py, gestionnaire réseau de QGIS), gardé en cache pour la session."""
    if refresh or service.id not in _CAPABILITIES:
        content = yield Fetch(capabilities_url(service), service.authcfg,
                              f"GetCapabilities de {service.id}")
        try:
            _CAPABILITIES[service.id] = parse_capabilities(service.kind, content)
        except ValueError as exc:
            raise ToolError(ErrorCode.NETWORK_ERROR,
                            f"GetCapabilities de {service.id} : {exc}") from exc
    return _CAPABILITIES[service.id]


def _layer(service: WebService, name: str) -> Steps:
    """Description (dict) d'une couche autorisée du service."""
    if is_natura2000_layer(name):
        raise ToolError(ErrorCode.PERMISSION_DENIED, NATURA2000_MESSAGE)
    if not service.allows(name):
        raise ToolError(ErrorCode.PERMISSION_DENIED, f"Couche {name} non autorisée pour "
                        f"{service.id}.", {"layers": list(service.layers)})
    layers = yield from _layers(service)
    layer = next((x for x in layers if x["name"] == name), None)
    if layer is None:
        close = search_layers(layers, service, name.split(":")[-1], 10)["layers"]
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Couche {name} absente de {service.id} : "
                        "cherche-la avec web_list_layers.", {"proches": [x["name"] for x in close]})
    return layer


def _crs(service: WebService, layer: dict[str, Any]) -> tuple[str | None, list[str]]:
    project_crs = QgsProject.instance().crs().authid() or None
    crs, warning = choose_crs(layer["crs"], [project_crs, service.crs])
    return crs, [warning] if warning else []


def _wfs_layer(service: WebService, name: str, title: str, max_features: int | None
               ) -> Steps:
    """(couche WFS en flux, SCR, avertissements)."""
    if service.kind != "wfs":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{service.id} est un WMS (image) : choisis un "
                        "service WFS pour des entités.")
    info = yield from _layer(service, name)
    crs, warnings = _crs(service, info)
    uri = QgsDataSourceUri()
    for key, value in wfs_params(service, name, crs, max_features or service.max_features).items():
        uri.setParam(key, value)
    layer = QgsVectorLayer(uri.uri(False), title, "WFS")
    if not layer.isValid():
        raise ToolError(ErrorCode.NETWORK_ERROR, f"QGIS ne parvient pas à ouvrir {name} : "
                        f"{layer.error().summary() or 'réponse invalide'}")
    return layer, crs, warnings


@tool(level=Level.READ)
def web_list_services() -> ToolResult:
    """Catalogue des services web WMS (images : orthophotos, cartes) et WFS (entités avec
    attributs, lisibles par l'IA) : catalogue intégré (Géoplateforme IGN) et services de
    l'utilisateur (~/.cynogis/web_services.json). Seuls ces services sont accessibles."""
    services, warnings = _catalog()
    return ToolResult({"file": str(SERVICES_FILE), "file_exists": SERVICES_FILE.exists(),
                       "services": [s.as_dict() for s in services.values()]}, warnings)


@tool(level=Level.READ, params={
    "service_id": Param("string", "Identifiant du service (web_list_services)."),
    "search": Param("string", "Mots à trouver dans le nom ou le titre, ex. « bdtopo batiment », "
                    "« ortho », « parcelle ».", required=False),
    "limit": Param("integer", "Nombre max de couches renvoyées.", required=False, default=50,
                   minimum=1, maximum=500),
    "refresh": Param("boolean", "Relire le GetCapabilities au lieu du cache de session.",
                     required=False, default=False),
})
def web_list_layers(service_id: str, search: str | None, limit: int, refresh: bool) -> Steps:
    """Couches proposées par un service (GetCapabilities) : nom technique à passer aux autres
    outils, titre, résumé, SCR proposés (EPSG:2975 Réunion, EPSG:4471 Mayotte ?). Les gros
    services (Géoplateforme : des centaines de couches) se filtrent avec search."""
    service, warnings = _service(service_id)
    layers = yield from _layers(service, refresh)
    result = search_layers(layers, service, search, limit)
    if result["truncated"]:
        warnings.append(f"{result['total']} couches trouvées, {limit} affichées : affine search.")
    return ToolResult({"service": service.id, "type": service.kind, **result}, warnings)


@tool(level=Level.CREATE, params={
    "service_id": Param("string", "Identifiant du service (web_list_services)."),
    "layer_name": Param("string", "Nom technique de la couche (web_list_layers), ex. "
                        "ORTHOIMAGERY.ORTHOPHOTOS ou BDTOPO_V3:batiment."),
    "name": Param("string", "Nom dans le panneau Couches (défaut : titre de la couche).",
                  required=False),
    "max_features": Param("integer", "WFS : plafond d'entités par requête (défaut : celui du "
                          "service).", required=False, minimum=1, maximum=MAX_FEATURES_LIMIT),
})
def web_add_layer(service_id: str, layer_name: str, name: str | None,
                  max_features: int | None) -> Steps:
    """Ajoute au projet (groupe « Cynogis ») une couche d'un service du catalogue, en flux :
    rien n'est téléchargé sur disque. WMS : image de fond, illisible par l'IA. WFS : entités
    lisibles avec get_features / get_field_values, chargées seulement sur l'emprise demandée
    et plafonnées à max_features ; pour une copie stable et complète d'une zone d'étude,
    utilise plutôt web_download_features."""
    service, warnings = _service(service_id)
    info = yield from _layer(service, layer_name)
    title = name or info["title"] or layer_name
    if service.kind == "wfs":
        layer, crs, crs_warnings = yield from _wfs_layer(service, layer_name, title,
                                                         max_features)
        warnings += crs_warnings
    else:
        crs, crs_warnings = _crs(service, info)
        warnings += crs_warnings
        uri = QgsDataSourceUri()
        for key, value in wms_params(service, layer_name, crs).items():
            uri.setParam(key, value)
        layer = QgsRasterLayer(bytes(uri.encodedUri()).decode(), title, "wms")
        if not layer.isValid():
            raise ToolError(ErrorCode.NETWORK_ERROR, f"QGIS ne parvient pas à ouvrir "
                            f"{layer_name} : {layer.error().summary() or 'réponse invalide'}")
        warnings.append("Couche image : l'IA n'en lit pas le contenu. Pour des attributs, "
                        "cherche l'équivalent WFS.")
    add_to_group(layer)
    logger.info("%s : %s ajoutée (%s)", service.id, layer_name, crs)
    return ToolResult({"layer_id": layer.id(), "name": layer.name(), "type": service.kind,
                       "service": service.id, "source_layer": layer_name, "crs": crs}, warnings)


@tool(level=Level.CREATE, params={
    "service_id": Param("string", "Identifiant d'un service WFS (web_list_services)."),
    "layer_name": Param("string", "Nom technique de la couche (web_list_layers), ex. "
                        "BDTOPO_V3:batiment."),
    "extent_layer_id": Param("string", "Couche dont l'emprise délimite le téléchargement "
                             "(zone d'étude)."),
    "output_name": Param("string", "Nom de la couche produite (défaut : nom de la couche WFS). "
                         "Nettoyé, jamais écrasé.", required=False),
    "max_features": Param("integer", "Plafond d'entités téléchargées (défaut : celui du service).",
                          required=False, minimum=1, maximum=MAX_FEATURES_LIMIT),
})
def web_download_features(service_id: str, layer_name: str, extent_layer_id: str,
                          output_name: str | None, max_features: int | None) -> Steps:
    """Télécharge les entités WFS intersectant l'emprise d'une couche dans un GeoPackage de
    mcp_outputs/ (copie figée, datée par le fichier, lisible hors ligne et traçable dans
    l'audit). Entités entières, non découpées : clip ensuite avec overlay si besoin."""
    service, warnings = _service(service_id)
    limit = max_features or service.max_features
    source, _, crs_warnings = yield from _wfs_layer(service, layer_name, layer_name, limit)
    warnings += crs_warnings
    extent_layer = get_layer(extent_layer_id)
    rect = extent_layer.extent()
    extent = (f"{rect.xMinimum()},{rect.xMaximum()},{rect.yMinimum()},{rect.yMaximum()} "
              f"[{extent_layer.crs().authid()}]")
    result = (yield from run_to_project("native:extractbyextent",
                                        {"INPUT": source, "EXTENT": extent, "CLIP": False},
                                        output_name or layer_name.split(":")[-1]))
    count = result.data["outputs"][0].get("feature_count", 0)
    if count >= limit:
        result.warnings.append(f"Plafond de {limit} entités atteint : résultat tronqué. Réduis "
                               "l'emprise ou augmente max_features.")
    result.data.update(service=service.id, source_layer=layer_name)
    result.warnings[:0] = warnings
    return result

