"""Noms de fichiers de sortie : nettoyés, sans accents, jamais écrasés. Python pur."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

MAX_NAME_CHARS = 60
_WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(10)),
                     *(f"lpt{i}" for i in range(10))}


def _ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def normalize(text: str) -> str:
    """Forme comparable : sans accents, minuscules, espaces simples (« Forêt  Ö » → « foret o »)."""
    return " ".join(_ascii(text).lower().split())


def clean_name(text: str, default: str = "sortie") -> str:
    """« Zones tampon 50 m (Saint-Paul) » → « zones_tampon_50_m_saint_paul »."""
    name = re.sub(r"[^a-z0-9]+", "_", _ascii(text).lower()).strip("_")[:MAX_NAME_CHARS].rstrip("_")
    if name in _WINDOWS_RESERVED:
        name += "_"
    return name or default


def unique_path(directory: Path, name: str, suffix: str) -> Path:
    """directory/name.suffix, ou name_2, name_3… si le fichier existe déjà."""
    path = directory / f"{name}{suffix}"
    n = 2
    while path.exists():
        path = directory / f"{name}_{n}{suffix}"
        n += 1
    return path
