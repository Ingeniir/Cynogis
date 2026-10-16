"""Serveur MCP générique : le catalogue des outils est fourni par le plugin QGIS."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from .client import BridgeError, QgisBridgeClient

logger = logging.getLogger("cynogis_server")
CACHE_FILE = Path.home() / ".cynogis" / "tools_cache.json"

INSTRUCTIONS = """Tu pilotes QGIS pour un bureau d'études travaillant à La Réunion
(SCR de référence EPSG:2975, RGR92 / UTM 40S) et à Mayotte (EPSG:4471, RGM04 / UTM 38S).
Commence toujours par get_project_info puis list_layers. Désigne les couches par leur layer_id.
Lis les 'warnings' de chaque réponse et tiens-en compte (SCR, encodage…).
Le niveau de chaque outil est indiqué dans sa description : les modifications de données
sont validées par un humain dans QGIS ; en cas de refus, ne réessaie pas sans lui demander."""

server = Server("cynogis", instructions=INSTRUCTIONS)
_client = QgisBridgeClient()


def _to_tool(spec: dict[str, Any]) -> types.Tool:
    level = spec["level"]
    return types.Tool(
        name=spec["name"],
        description=spec["description"],
        inputSchema=spec["input_schema"],
        annotations=types.ToolAnnotations(
            readOnlyHint=level == 0, destructiveHint=level >= 3,
            idempotentHint=level == 0, openWorldHint=False),
    )


async def _fetch_specs() -> list[dict[str, Any]]:
    try:
        result = await _client.call("list_tools")
    except BridgeError as exc:
        logger.warning("QGIS indisponible (%s) : catalogue en cache utilisé", exc)
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
    specs = result.data["tools"]
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(specs, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        logger.exception("Écriture du cache impossible")
    return specs


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [_to_tool(spec) for spec in await _fetch_specs()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    try:
        result = await _client.call(name, arguments or {})
    except BridgeError as exc:
        details = (f"\nDétails : {json.dumps(exc.details, ensure_ascii=False)}"
                   if exc.details else "")
        raise RuntimeError(f"{exc}{details}") from exc  # → isError=true, lisible par l'IA
    payload = {"data": result.data, "warnings": result.warnings, "audit_id": result.audit_id}
    return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=1))]


async def run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
