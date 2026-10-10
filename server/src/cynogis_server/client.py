"""Client du pont QGIS. Une connexion par requête : robuste aux redémarrages de QGIS."""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = 1
MAX_MESSAGE_BYTES = 16 * 1024 * 1024
DEFAULT_CONNECTION_FILE = Path.home() / ".cynogis" / "connection.json"


class BridgeError(Exception):
    def __init__(self, code: str, message: str, details: Any = None):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass
class BridgeResult:
    data: Any
    warnings: list[str] = field(default_factory=list)
    audit_id : str | None = None


class QgisBridgeClient:
    def __init__(self, connection_file: Path | None = None,
                 connect_timeout: float = 5.0, request_timeout: float = 120.0):
        self.connection_file = connection_file or Path(
            os.environ.get("CYNOGIS_CONNECTION_FILE", DEFAULT_CONNECTION_FILE))
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout

    def _read_connection(self) -> dict[str, Any]:
        try:
            return json.loads(self.connection_file.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise BridgeError("QGIS_UNAVAILABLE",
                              "QGIS n'est pas lancé ou le serveur Cynogis n'est pas démarré "
                              "(bouton Cynogis de la barre d'outils).") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise BridgeError("QGIS_UNAVAILABLE", f"Fichier de connexion illisible : {exc}") from exc

    async def call(self, method: str, params: dict[str, Any] | None = None) -> BridgeResult:
        conn = self._read_connection()
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(conn["host"], conn["port"], limit=MAX_MESSAGE_BYTES),
                self.connect_timeout)
        except (OSError, asyncio.TimeoutError) as exc:
            raise BridgeError("QGIS_UNAVAILABLE", f"Connexion à QGIS impossible : {exc}") from exc

        request = {"v": PROTOCOL_VERSION, "id": uuid.uuid4().hex, "token": conn["token"],
                   "method": method, "params": params or {}}
        try:
            writer.write(json.dumps(request, ensure_ascii=False).encode("utf-8") + b"\n")
            await writer.drain()
            line = await asyncio.wait_for(reader.readline(), self.request_timeout)
        except asyncio.TimeoutError as exc:
            raise BridgeError("TIMEOUT",
                              f"QGIS n'a pas répondu en {self.request_timeout:.0f} s ({method}).") from exc
        except ValueError as exc:
            raise BridgeError("PROTOCOL_ERROR", "Réponse trop volumineuse.") from exc
        finally:
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()

        if not line:
            raise BridgeError("QGIS_UNAVAILABLE", "Connexion fermée par QGIS sans réponse.")
        response = json.loads(line)
        if not response.get("ok"):
            err = response.get("error") or {}
            raise BridgeError(err.get("code", "UNKNOWN"), err.get("message", "Erreur inconnue"),
                              err.get("details"))
        return BridgeResult(response.get("data"), response.get("warnings") or [], response.get("audit_id"))
