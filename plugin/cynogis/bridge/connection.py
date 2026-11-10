"""Fichier de connexion partagé avec le serveur MCP : hôte, port, jeton."""
from __future__ import annotations

import json
import os
import secrets
from pathlib import Path

CONNECTION_FILE = Path(
    os.environ.get("CYNOGIS_CONNECTION_FILE", Path.home() / ".cynogis" / "connection.json")
)

def new_token() -> str:
    return secrets.token_urlsafe(32)

def write_connection_file(host: str, port: int, token: str) -> Path:
    CONNECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONNECTION_FILE.with_suffix(".tmp")
    tmp.write_text(
        json.dumps({
            "host": host,
            "port": port,
            "token": token,
            "pid": os.getpid(),
        }),
        encoding="utf-8",
    )

    if os.name != "nt":
        os.chmod(tmp, 0o600)
    os.replace(tmp, CONNECTION_FILE)
    return CONNECTION_FILE

def remove_connection_file(token: str, *, strict: bool = False) -> None:
    """Supprime le fichier uniquement s'il appartient à cette instance.

    Un fichier absent n'est pas une erreur.
    En mode strict, les erreurs de lecture, de format ou de suppression
    remontent à l'appelant.
    """
    try:
        data = json.loads(CONNECTION_FILE.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError("Le fichier de connexion doit contenir un objet JSON.")

        if data.get("token") != token:
            return

        CONNECTION_FILE.unlink()
    except FileNotFoundError:
        return
    except (OSError, ValueError):
        if strict:
            raise
