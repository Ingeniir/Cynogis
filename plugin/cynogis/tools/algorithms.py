from __future__ import annotations

import re
from typing import Any

from qgis.core import QgsApplication, QgsProcessingAlgorithm

from ..core import algorithms as catalog
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import to_json_value
from .outputs import is_optional, run_to_project

MAX_HELP_CHARS = 1500


def _allowed(algorithm_id: str) -> QgsProcessingAlgorithm:
    alg = QgsApplication.processingRegistry().algorithmById(algorithm_id) \
        if catalog.is_allowed(algorithm_id) else None
    if alg is None:
        raise ToolError(ErrorCode.ALGORITHM_NOT_ALLOWED,
                        f"Algorithme {algorithm_id!r} non autorisé ou indisponible. "
                        "Utilise list_algorithms.")
    return alg


@tool(level=Level.READ, params={
    "query": Param("string", "Mots-clés (accents et casse ignorés), ex. tampon, jointure, mnt.",
                   required=False),
    "category": Param("string", "Filtre par catégorie.", required=False,
                      enum=catalog.CATEGORIES),
})
def list_algorithms(query: str | None, category: str | None) -> dict:
    """Algorithmes Processing autorisés pour run_algorithm (liste blanche relue par un humain) :
    identifiant, libellé, catégorie et résumé. Avant d'en lancer un, lis ses paramètres avec
    describe_algorithm."""
    registry = QgsApplication.processingRegistry()
    items = [spec.to_dict() for spec in catalog.search_algorithms(query, category)
             if registry.algorithmById(spec.algorithm_id) is not None]
    return {"count": len(items), "categories": list(catalog.CATEGORIES), "algorithms": items}


@tool(level=Level.READ, params={
    "algorithm_id": Param("string", "Identifiant, ex. native:buffer (voir list_algorithms)."),
})
def describe_algorithm(algorithm_id: str) -> dict:
    """Paramètres d'entrée d'un algorithme autorisé : nom, type, description, facultatif,
    valeur par défaut, options (type enum : passer l'indice). Les sorties sont gérées par
    Cynogis (GeoPackage dans mcp_outputs/) : ne pas les fournir à run_algorithm."""
    alg = _allowed(algorithm_id)
    params = []
    for p in alg.parameterDefinitions():
        if p.isDestination():
            continue
        item: dict[str, Any] = {"name": p.name(), "type": p.type(),
                                "description": p.description(), "optional": is_optional(p),
                                "default": to_json_value(p.defaultValue())}
        if p.type() == "enum":
            item["options"] = list(p.options())
        params.append(item)
    help_text = re.sub(r"<[^>]+>", "", alg.shortHelpString() or "").strip()
    return {"id": algorithm_id, "name": alg.displayName(), "help": help_text[:MAX_HELP_CHARS],
            "parameters": params,
            "outputs": [{"name": o.name(), "type": o.type(), "description": o.description()}
                        for o in alg.outputDefinitions()]}


@tool(level=Level.CREATE, params={
    "algorithm_id": Param("string", "Identifiant d'un algorithme autorisé (list_algorithms)."),
    "parameters": Param("object", "Paramètres d'entrée (noms de describe_algorithm). Couches : "
                        "layer_id. Enum : indice de l'option. Sans paramètre de sortie."),
    "output_name": Param("string", "Nom de la couche produite (nettoyé, jamais écrasé).",
                         required=False),
})
def run_algorithm(algorithm_id: str, parameters: dict, output_name: str | None) -> ToolResult:
    """Lance un algorithme Processing de la liste blanche. Le résultat est écrit dans un
    nouveau GeoPackage de mcp_outputs/ (jamais d'écrasement) et ajouté au projet dans le
    groupe « Cynogis ». Préfère les outils dédiés (buffer, overlay…) quand ils existent."""
    alg = _allowed(algorithm_id)
    known = {p.name(): p for p in alg.parameterDefinitions()}
    unknown = sorted(set(parameters) - set(known))
    if unknown:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Paramètres inconnus : {', '.join(unknown)}",
                        {"available": [n for n, p in known.items() if not p.isDestination()]})
    destinations = sorted(n for n in parameters if known[n].isDestination())
    if destinations:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        f"Sorties gérées par Cynogis, à retirer : {', '.join(destinations)}. "
                        "Utilise output_name pour nommer le résultat.")
    name = output_name or algorithm_id.split(":")[-1]
    return run_to_project(algorithm_id, parameters, name)
