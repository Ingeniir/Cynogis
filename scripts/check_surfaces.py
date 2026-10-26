"""Tests de référence des surfaces (feuille de route 1.1 à 1.3, 1.5, 1.6), sans QGIS lancé.

À exécuter avec le Python de QGIS (pytest n'y est pas installé) :
    "C:\\Program Files\\QGIS 4.2.1\\bin\\python-qgis.bat" scripts/check_surfaces.py

Référence planaire : surface exacte des carrés construits en coordonnées UTM.
Référence ellipsoïdale : surface planaire / k², k = facteur d'échelle UTM au centre du carré
(projection conforme : les surfaces sont multipliées par k²), au premier ordre en x².
"""
from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin"))

from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsGeometry

APP = QgsApplication([], False)
APP.initQgis()

from cynogis.core.errors import ErrorCode, ToolError  # noqa: E402
from cynogis.core.jobs import collecting  # noqa: E402
from cynogis.tools.common import (  # noqa: E402
    INVALID_AREA_NOTE,
    area_m2,
    area_method,
    dissolved_areas,
    distance_area,
    overlap_warning,
)

PLANAR_TOL_M2 = 1e-6     # tolérance absolue, surface planaire
ELLIPSOIDAL_TOL = 1e-5   # tolérance relative (0,001 %), surface ellipsoïdale

A = 6378137.0                 # GRS80 (RGR92, RGM04)
E2 = (1 / 298.257222101) * (2 - 1 / 298.257222101)
K0 = 0.9996

# (SCR, territoire, abscisse et ordonnée du coin sud-ouest, latitude approchée)
SITES = [
    ("EPSG:2975", "La Réunion (Saint-Denis)", 338_000.0, 7_690_000.0, -20.88),
    ("EPSG:4471", "Mayotte (Mamoudzou)", 524_000.0, 8_586_000.0, -12.78),
]


def utm_scale(easting: float, lat_deg: float) -> float:
    """Facteur d'échelle UTM : k0 (1 + x² / (2 rho nu k0²)), x = distance au méridien
    central, rho et nu = rayons de courbure méridien et du premier vertical."""
    s2 = math.sin(math.radians(lat_deg)) ** 2
    nu = A / math.sqrt(1 - E2 * s2)
    rho = nu * (1 - E2) / (1 - E2 * s2)
    x = easting - 500_000.0
    return K0 * (1 + x * x / (2 * rho * nu * K0 * K0))


def square(x: float, y: float, side: float) -> str:
    return f"({x} {y}, {x + side} {y}, {x + side} {y + side}, {x} {y + side}, {x} {y})"


def check_site(authid: str, label: str, x: float, y: float, lat: float) -> None:
    crs = QgsCoordinateReferenceSystem(authid)
    planar, ellipsoidal = distance_area(crs, "planar"), distance_area(crs, "ellipsoidal")
    cases = {
        "carré 100 m": (f"POLYGON({square(x, y, 100)})", 10_000.0),
        "carré 1 km": (f"POLYGON({square(x, y, 1000)})", 1_000_000.0),
        "trou 20 m": (f"POLYGON({square(x, y, 100)}, {square(x + 40, y + 40, 20)})", 9_600.0),
        "multi-polygone": (f"MULTIPOLYGON(({square(x, y, 100)}), "
                           f"({square(x + 500, y, 50)}))", 12_500.0),
        # Polygone auto-intersecté (nœud papillon) : deux triangles de 25 m², pas 0.
        "papillon": (f"POLYGON(({x} {y}, {x + 10} {y + 10}, {x + 10} {y}, "
                     f"{x} {y + 10}, {x} {y}))", 50.0),
    }
    assert area_method(planar) == f"planaire ({authid}), surface projetée 2D", \
        area_method(planar)
    assert area_method(ellipsoidal).startswith("ellipsoïdale ("), area_method(ellipsoidal)
    k = utm_scale(x + 50, lat)
    notes: Counter[str] = Counter()
    for name, (wkt, expected) in cases.items():
        geometry = QgsGeometry.fromWkt(wkt)
        with collecting(notes):
            got = area_m2(planar, geometry)
        assert abs(got - expected) < PLANAR_TOL_M2, f"{label} {name} planaire : {got}"
        with collecting(notes):
            got = area_m2(ellipsoidal, geometry)
        reference = expected / (k * k)
        assert abs(got / reference - 1) < ELLIPSOIDAL_TOL, \
            f"{label} {name} ellipsoïdal : {got} au lieu de {reference}"
    # Seul le papillon est invalide : signalé (feuille de route 1.6), une fois par méthode.
    assert notes == Counter({INVALID_AREA_NOTE: 2}), notes
    print(f"✓ {label} ({authid}) : {len(cases)} cas, écart planaire/ellipsoïdal "
          f"{100 * (1 - k * k):+.4f} %, méthode « {area_method(ellipsoidal)} »")


def check_dissolved() -> None:
    """Feuille de route 1.5 : fusion par classe avant somme (chevauchement, trou, multi)."""
    x, y = 338_000.0, 7_690_000.0
    da = distance_area(QgsCoordinateReferenceSystem("EPSG:2975"), "planar")
    items = [
        ("a", f"POLYGON({square(x, y, 100)})"),
        ("a", f"POLYGON({square(x + 50, y, 100)})"),  # recouvre le premier sur 50 m sur 100 m
        ("b", f"POLYGON({square(x + 1000, y, 100)}, {square(x + 1040, y + 40, 20)})"),
        ("b", f"MULTIPOLYGON(({square(x + 2000, y, 100)}), ({square(x + 2500, y, 50)}))"),
    ]
    areas, doubled = dissolved_areas(da, ((k, QgsGeometry.fromWkt(w)) for k, w in items))
    assert abs(areas["a"] - 15_000) < PLANAR_TOL_M2, areas
    assert abs(areas["b"] - 9_600 - 12_500) < PLANAR_TOL_M2, areas
    assert doubled.keys() == {"a"} and abs(doubled["a"] - 5_000) < PLANAR_TOL_M2, doubled
    assert "5000.00 m²" in overlap_warning(doubled)[0]
    print("✓ Fusion par classe : chevauchement compté une fois, trou et multi-polygone respectés")


def check_geographic_rejected() -> None:
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    geometry = QgsGeometry.fromWkt("POLYGON((55.4 -20.9, 55.5 -20.9, 55.5 -20.8, 55.4 -20.9))")
    da = distance_area(crs, "ellipsoidal")
    try:
        area_m2(da, geometry)
    except ToolError as exc:
        assert exc.code == ErrorCode.CRS_GEOGRAPHIC, exc.code
    else:
        raise AssertionError("Surface calculée en EPSG:4326 au lieu d'être refusée")
    print("✓ EPSG:4326 : surface refusée (CRS_GEOGRAPHIC)")


if __name__ == "__main__":
    for site in SITES:
        check_site(*site)
    check_dissolved()
    check_geographic_rejected()
    APP.exitQgis()
