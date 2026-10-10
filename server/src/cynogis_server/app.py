from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from .client import BridgeError, QgisBridgeClient

INSTRUCTIONS = """Tu pilotes QGIS pour un bureau d'études travaillant à La Réunion
(SCR de référence EPSG:2975, RGR92 / UTM 40S) et à Mayotte (EPSG:4471, RGM04 / UTM 38S).
Commence toujours par get_project_info. Désigne les couches par leur layer_id.
Les modifications de données doivent être validées par un humain dans QGIS."""

mcp = FastMCP("cynogis", instructions=INSTRUCTIONS)
_client = QgisBridgeClient()


async def call_qgis(method: str, **params: Any) -> dict[str, Any]:
    try:
        result = await _client.call(method, params)
    except BridgeError as exc:
        raise ToolError(str(exc)) from exc  # → isError=true, message lisible par l'IA
    return {"data": result.data, "warnings": result.warnings}


@mcp.tool()
async def ping() -> dict[str, Any]:
    """Vérifie que QGIS et le plugin Cynogis répondent. Renvoie les versions QGIS/Qt/plugin."""
    return await call_qgis("ping")


@mcp.tool()
async def get_project_info() -> dict[str, Any]:
    """Infos générales du projet QGIS ouvert : titre, fichier, SCR, nombre de couches.
    À appeler en premier pour comprendre le contexte de travail."""
    return await call_qgis("get_project_info")
