"""Serveur MCP générique : le catalogue des outils est fourni par le plugin QGIS."""
from __future__ import annotations

import asyncio
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
# Délai maximal d'attente avant demande d'annulation.
# L'arrêt effectif est observé séparément, sans être garanti par ce délai.
JOB_TIMEOUT_S = 3600.0
POLL_FIRST_S, POLL_MAX_S = 0.2, 1.0

CANCEL_GRACE_S = 5.0
CANCEL_POLL_S = 0.2

INSTRUCTIONS = """Tu pilotes QGIS pour un bureau d'études travaillant à La Réunion
(SCR de référence EPSG:2975, RGR92 / UTM 40S) et à Mayotte (EPSG:4471, RGM04 / UTM 38S).
Commence toujours par get_project_info puis list_layers. Désigne les couches par leur layer_id.
Lis les 'warnings' de chaque réponse et tiens-en compte (SCR, encodage…).
Natura 2000 ne s'applique pas dans les départements d'outre-mer : ne le propose jamais.
Le niveau de chaque outil est indiqué dans sa description : les modifications de données
sont validées par un humain dans QGIS ; en cas de refus, ne réessaie pas sans lui demander."""

server = Server("cynogis", instructions=INSTRUCTIONS)
_client = QgisBridgeClient()
# Catalogue de la session QGIS en cours, clé = (port, jeton) de connection.json : un
# redémarrage du pont (QGIS relancé, plugin rechargé) change le jeton et force la relecture.
_specs_cache: tuple[tuple[Any, Any], list[dict[str, Any]]] | None = None


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
    global _specs_cache
    try:
        conn = _client._read_connection()
        key = (conn.get("port"), conn.get("token"))
    except BridgeError:
        key = None
    if key is not None and _specs_cache is not None and _specs_cache[0] == key:
        return _specs_cache[1]
    try:
        result = await _client.call("list_tools")
    except BridgeError as exc:
        logger.warning("QGIS indisponible (%s) : catalogue en cache utilisé", exc)
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
    specs = result.data["tools"]
    if key is not None:
        _specs_cache = key, specs
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
    return [types.TextContent(type="text", text=json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")))]


def _progress_token() -> str | int | None:
    try:
        meta = server.request_context.meta
    except LookupError:  # hors requête MCP (tests)
        return None
    return meta.progressToken if meta is not None else None

async def _cancel_and_observe(job_id: str) -> dict[str, Any]:
    """Demande l'annulation et observe sa fin pendant un délai borné.

    Ne force jamais l'arrêt du worker QGIS.
    Une absence de confirmation ne signifie pas que le job est arrêté.
    Les détails d'une réponse d'erreur sont conservés, notamment les
    chemins de sorties retenues après une annulation tardive.
    """
    observation: dict[str, Any] = {
        "job_id": job_id,
        "request_acknowledged": False,
        "stop_confirmed": False,
        "outcome": "unconfirmed",
    }

    stage = "cancel_job"

    with anyio.move_on_after(CANCEL_GRACE_S, shield=True) as scope:
        try:
            acknowledgement = await _client.call(
                "cancel_job",
                {"job_id": job_id},
            )

            observation["request_acknowledged"] = True
            observation["last_status"] = acknowledgement.data

            stage = "get_job_status"

            while True:
                result = await _client.call(
                    "get_job_status",
                    {"job_id": job_id},
                )

                if result.job_id is None:
                    observation["stop_confirmed"] = True
                    observation["outcome"] = "completed"
                    observation["terminal_result"] = result.data
                    observation["terminal_warnings"] = result.warnings
                    observation["audit_id"] = result.audit_id
                    return observation

                observation["last_status"] = result.data
                await asyncio.sleep(CANCEL_POLL_S)
        except BridgeError as exc:
            observation["error"] = {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "stage": stage,
            }

            if stage == "get_job_status" and exc.code == "CANCELLED":
                observation["stop_confirmed"] = True
                observation["outcome"] = "cancelled"
            else:
                observation["outcome"] = "observation_error"

            return observation

    if scope.cancel_called:
        observation["outcome"] = "grace_expired"

    return observation


async def _wait_job(result: BridgeResult) -> BridgeResult:
    """Attend le résultat d'un job et transmet sa progression au client MCP.

    En cas d'annulation de l'appel ou de dépassement du délai, demande
    l'annulation dans QGIS puis observe sa fin pendant un délai borné.

    L'expiration de ce second délai ne force pas l'arrêt du traitement :
    le job peut rester actif et conserver son verrou dans QGIS.
    """

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
        try:
            observation = await _cancel_and_observe(job_id)
        except asyncio.CancelledError:
            logger.warning(
                "Observation de l'annulation interrompue pour le job %s ; "
                "arrêt non confirmé.",
                job_id,
            )
            raise
        if isinstance(exc, TimeoutError):
            outcome = observation["outcome"]

            if outcome == "cancelled":
                message = "Annulation confirmée par QGIS."
            elif outcome == "completed":
                message = (
                    "Le traitement s'est terminé pendant la demande "
                    "d'annulation ; consulter les détails."
                )
            elif outcome == "observation_error":
                message = (
                    "Une erreur a été reçue pendant la demande ou le suivi "
                    "d'annulation. L'état terminal du job n'a pas pu être "
                    "confirmé par cette observation ; consulter les détails."
                )
            else:
                message = (
                    "Arrêt non confirmé. Le traitement peut encore être "
                    "actif dans QGIS et conserver le verrou."
                )

            raise BridgeError(
                "TIMEOUT",
                f"Le délai de {JOB_TIMEOUT_S / 60:.0f} min a été dépassé. "
                f"{message}",
                {"cancellation": observation},
            ) from exc

        logger.warning(
            "Annulation de l'appel MCP pour le job %s : %s",
            job_id,
            json.dumps(observation, ensure_ascii=False, default=str),
        )
        raise
    return result


async def run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
