"""Journal d'audit : un fichier JSONL par jour + mémoire des dernières actions. Python pur."""
from __future__ import annotations

import itertools
import json
import logging
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

from .registry import Level

logger = logging.getLogger("cynogis.audit")
MAX_PARAMS_CHARS = 2000


def _truncate(params: dict[str, Any]) -> Any:
    text = json.dumps(params, ensure_ascii=False, default=str)
    return params if len(text) <= MAX_PARAMS_CHARS else {"_truncated": text[:MAX_PARAMS_CHARS]}


class AuditLog:
    def __init__(self, directory: Path | None, memory_size: int = 200) -> None:
        self.directory = directory
        self._recent: deque[dict[str, Any]] = deque(maxlen=memory_size)
        self._counter = itertools.count(1)

    def record(self, *, tool: str, level: int, params: dict[str, Any], ok: bool,
               duration_ms: float, error_code: str | None = None,
               outputs: list[str] | None = None) -> str:
        now = datetime.now().astimezone()
        audit_id = f"{now:%Y%m%dT%H%M%S}-{next(self._counter):04d}"
        entry = {
            "audit_id": audit_id,
            "ts": now.isoformat(timespec="seconds"),
            "tool": tool,
            "level": level,
            "ok": ok,
            "error_code": error_code,
            "duration_ms": round(duration_ms, 1),
            # Action irréversible (code PyQGIS…) : trace complète.
            "params": params if level >= Level.DESTROY else _truncate(params),
            "outputs": outputs or [],
        }
        self._recent.append(entry)
        if self.directory is not None:
            try:
                self.directory.mkdir(parents=True, exist_ok=True)
                path = self.directory / f"{now:%Y-%m-%d}.jsonl"
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
            except OSError:
                logger.exception("Écriture du journal d'audit impossible")
        return audit_id

    def recent(self, limit: int = 20, tool: str | None = None) -> list[dict[str, Any]]:
        entries = [e for e in self._recent if tool is None or e["tool"] == tool]
        return entries[-limit:][::-1]  # le plus récent en premier
