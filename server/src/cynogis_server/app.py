"""Serveur MCP générique : le catalogue des outils est fourni par le plugin QGIS."""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from pathlib import Path
from typing import Any

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from .client import BridgeError, BridgeResult, QgisBridgeClient

logger = logging.getLogger("cynogis_server")
CACHE_FILE = Path.home() / ".cynogis" / "tools_cache.json"
JOB_TIMEOUT_S = 3600.0          # au-delà, le traitement est annulé dans QGIS
POLL_FIRST_S, POLL_MAX_S = 0.2, 1.0

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
        if result.job_id:
            result = await _wait_job(result)
    except BridgeError as exc:
        details = (f"\nDétails : {json.dumps(exc.details, ensure_ascii=False)}"
                   if exc.details else "")
        raise RuntimeError(f"{exc}{details}") from exc  # → isError=true, lisible par l'IA
    payload = {"data": result.data, "warnings": result.warnings, "audit_id": result.audit_id}
    return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=1))]


def _progress_token() -> str | int | None:
    try:
        meta = server.request_context.meta
    except LookupError:  # hors requête MCP (tests)
        return None
    return meta.progressToken if meta is not None else None


async def _wait_job(result: BridgeResult) -> BridgeResult:
    """Traitement long : QGIS a répondu tout de suite avec un job_id (son interface reste
    libre) ; c'est ici qu'on attend, en interrogeant get_job_status. L'avancement part en
    notifications de progression MCP si le client en demande. Annulation MCP ou délai
    dépassé : le traitement est annulé dans QGIS."""
    job_id, token = result.job_id, _progress_token()
    delay, deadline = POLL_FIRST_S, time.monotonic() + JOB_TIMEOUT_S
    try:
        while result.job_id:
            if time.monotonic() > deadline:
                raise TimeoutError
            await asyncio.sleep(delay)
            delay = min(delay * 1.5, POLL_MAX_S)
            result = await _client.call("get_job_status", {"job_id": job_id})
            if result.job_id and token is not None:
                status = result.data
                await server.request_context.session.send_progress_notification(
                    token, status["progress"], 100.0,
                    f"Étape {status['step']} : {status['algorithm']}")
    except (asyncio.CancelledError, TimeoutError) as exc:
        with anyio.CancelScope(shield=True), contextlib.suppress(BridgeError):
            await _client.call("cancel_job", {"job_id": job_id})
        if isinstance(exc, TimeoutError):
            raise BridgeError("TIMEOUT", f"Traitement non terminé après "
                              f"{JOB_TIMEOUT_S / 60:.0f} min : annulé dans QGIS.") from exc
        raise
    return result


async def run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
