"""Protocole JSON-lines du pont : une requête/réponse JSON par ligne (UTF-8)"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from ..core.errors import ErrorCode, ToolError

PROTOCOL_VERSION = 1
MAX_MESSAGE_BYTES = 16 * 1024 * 1024
ENCODING = "utf-8"

@dataclass(frozen=True)
class Request:
    id: str
    method: str
    params: dict[str, Any]
    token: str

@dataclass
class Response:
    id: str | None
    ok: bool
    data: Any = None
    warnings: list[str] = field(default_factory=list)
    error: dict[str, Any] | None = None
    audit_id: str | None = None
    job_id: str | None = None  # traitement en cours : suivre avec get_job_status

    @classmethod
    def failure(cls, request_id: str | None, err: ToolError) -> Response:
        return cls(id=request_id, ok=False, error=err.to_dict())

    def encode(self) -> bytes:
        payload: dict[str, Any] = {"v": PROTOCOL_VERSION, "id": self.id, "ok": self.ok,
                                   "audit_id": self.audit_id}
        if self.ok:
            payload["data"] = self.data
            payload["warnings"] = self.warnings
        else:
            payload["error"] = self.error
        if self.job_id is not None:
            payload["job_id"] = self.job_id
        return json.dumps(payload, ensure_ascii=False, default=str).encode(ENCODING) + b"\n"


def _protocol_error(message: str) -> ToolError:
    return ToolError(ErrorCode.PROTOCOL_ERROR, message)

def decode_request(line: bytes) -> Request:
    try:
        obj = json.loads(line.decode(ENCODING))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _protocol_error(f"JSON invalide : {exc}") from exc
    if not isinstance(obj, dict):
        raise _protocol_error("La requête doit être un objet JSON.")
    if obj.get("v") != PROTOCOL_VERSION:
        raise _protocol_error(
            f"Version de protocole {obj.get('v')!r} non supportée (attendu: {PROTOCOL_VERSION})."
        )
    req_id, method = obj.get("id"), obj.get("method")
    params, token = obj.get("params", {}), obj.get("token")

    if not isinstance(req_id, str) or not req_id:
        raise _protocol_error("Champ 'id' manquant ou  invalide.")
    if not isinstance(method, str) or not method:
        raise _protocol_error("Champ 'method' manquant ou invalide.")
    if not isinstance(params, dict):
        raise _protocol_error("Champ 'params' : objet JSON attendu.")
    if not isinstance(token, str):
        raise ToolError(ErrorCode.UNAUTHORIZED, "Jeton d'authentification manquant.")

    return Request(id=req_id, method=method, params=params, token=token)
