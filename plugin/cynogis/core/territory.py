"""Territoires de travail et détection automatique à partir d'une emprise WGS84. Python pur."""
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from .naming import normalize

NATURA2000_MESSAGE = ("Natura 2000 ne s'applique pas dans les départements d'outre-mer "
                      "(La Réunion, Mayotte) : non proposé par Cynogis.")
_NATURA2000 = re.compile(r"natura[\s_:-]*2000")
# Noms et titres de couches : aussi les désignations SIC/pSIC/ZSC/ZPS.
_NATURA2000_LAYER = re.compile(r"natura|(?<![a-z])(p?sic|zsc|zps)(?![a-z])"
                               r"|importance communautaire|protection speciale")


def mentions_natura2000(text: str) -> bool:
    """Texte citant Natura 2000 (« Natura 2000 », « natura_2000 »…)."""
    return bool(_NATURA2000.search(normalize(text)))


def is_natura2000_layer(text: str) -> bool:
    """Nom ou titre de couche d'un site Natura 2000 (« patrinat_zps:zps », « SIC »…)."""
    return bool(_NATURA2000_LAYER.search(normalize(text)))


@dataclass(frozen=True)
class Territory:
    code: str
    name: str
    epsg: str
    bbox: tuple[float, float, float, float]  # lon_min, lat_min, lon_max, lat_max

    def contains(self, lon: float, lat: float) -> bool:
        x0, y0, x1, y1 = self.bbox
        return x0 <= lon <= x1 and y0 <= lat <= y1

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "name": self.name, "reference_crs": self.epsg}


REUNION = Territory("reunion", "La Réunion", "EPSG:2975", (55.15, -21.45, 55.90, -20.80))
MAYOTTE = Territory("mayotte", "Mayotte", "EPSG:4471", (44.95, -13.05, 45.35, -12.55))
TERRITORIES = {t.code: t for t in (REUNION, MAYOTTE)}
UNKNOWN = {"code": "unknown", "name": "Inconnu", "reference_crs": None}


def detect_territory(bbox_wgs84: Sequence[float] | None) -> Territory | None:
    """Territoire contenant le centre de l'emprise, ou None."""
    if not bbox_wgs84:
        return None
    x0, y0, x1, y1 = bbox_wgs84
    lon, lat = (x0 + x1) / 2, (y0 + y1) / 2
    return next((t for t in TERRITORIES.values() if t.contains(lon, lat)), None)
