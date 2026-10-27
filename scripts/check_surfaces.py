"""Tests de référence des surfaces (feuille de route 1.1 à 1.6), sans QGIS lancé.

À exécuter avec le Python de QGIS (pytest n'y est pas installé) :
    "C:\\Program Files\\QGIS 4.2.1\\bin\\python-qgis.bat" scripts/check_surfaces.py

Référence planaire : surface exacte des carrés construits en coordonnées UTM.
Référence ellipsoïdale : surface planaire / k², k = facteur d'échelle UTM au centre du carré
(projection conforme : les surfaces sont multipliées par k²), au premier ordre en x².
"""
from __future__ import annotations

import math
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin"))

import numpy
from osgeo import gdal, osr
from qgis.core import (
    NULL,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)

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
from cynogis.tools.terrain import _surface_factors, surface_3d  # noqa: E402

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


DEM_NODATA = -9999.0


def synthetic_dem(directory: Path, slope_deg: float, hole: bool = False) -> QgsRasterLayer:
    """MNT synthétique EPSG:2975 : plan incliné vers l'est, pixels de 1 m, 200 sur 200 ;
    hole : bande sans donnée (zone sensible non diffusée)."""
    size, x0, y0 = 200, 338_000.0, 7_690_200.0
    z = numpy.tile((numpy.arange(size) + 0.5) * math.tan(math.radians(slope_deg)) + 100.0,
                   (size, 1))
    if hole:
        z[60:100, :] = DEM_NODATA
    path = directory / f"mnt_{slope_deg:g}_{int(hole)}.tif"
    dataset = gdal.GetDriverByName("GTiff").Create(str(path), size, size, 1, gdal.GDT_Float64)
    dataset.SetGeoTransform((x0, 1.0, 0.0, y0, 0.0, -1.0))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(2975)
    dataset.SetProjection(srs.ExportToWkt())
    dataset.GetRasterBand(1).SetNoDataValue(DEM_NODATA)
    dataset.GetRasterBand(1).WriteArray(z)
    dataset = None
    layer = QgsRasterLayer(str(path), path.stem)
    assert layer.isValid(), path
    return layer


def check_surface_3d() -> None:
    """Feuille de route 1.4 : plan à 30° (1/cos 30°), plan horizontal (1), plafond de pente,
    trou de données (couverture signalée, surface 3D non donnée), petit polygone."""
    x, y = 338_050.0, 7_690_050.0  # carré de 100 m au centre du MNT (lignes et colonnes 50-150)
    plot = QgsGeometry.fromWkt(f"POLYGON({square(x, y, 100)})")
    tiny = QgsGeometry.fromWkt(f"POLYGON({square(x - 30.2, y + 10.2, 0.4)})")  # hors du carré
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        directory = Path(tmp)
        for slope, cap, expected in ((30, 85, 1 / math.cos(math.radians(30))),
                                     (0, 85, 1.0),
                                     (88, 85, 1 / math.cos(math.radians(85)))):
            (ratio, valid, cells), (small, _, one) = \
                _surface_factors(synthetic_dem(directory, slope), [plot, tiny], cap)[0]
            assert abs(ratio / expected - 1) < 1e-9 and valid == cells == 10_000, (slope, ratio)
            assert one == 1 and abs(small / expected - 1) < 1e-9, (slope, small)
        (ratio, valid, cells), _ = _surface_factors(synthetic_dem(directory, 30, True),
                                                    [plot, tiny], 85)[0]
        assert valid / cells < 0.95 and abs(ratio * math.cos(math.radians(30)) - 1) < 1e-9

        # Outil complet : couche en sortie dans un projet temporaire
        project = QgsProject.instance()
        project.setPresetHomePath(tmp)
        polygons = QgsVectorLayer("Polygon?crs=EPSG:2975", "parcelles", "memory")
        features = []
        for geometry in (plot, QgsGeometry.fromWkt(f"POLYGON({square(x, y + 5, 30)})")):
            feature = QgsFeature(polygons.fields())
            feature.setGeometry(geometry)
            features.append(feature)
        polygons.dataProvider().addFeatures(features)
        dem = synthetic_dem(directory, 30, hole=True)
        project.addMapLayers([polygons, dem])
        result = surface_3d(polygons.id(), dem.id(), 85, 95, "test_surface_3d")
        output = project.mapLayer(result.data["outputs"][0]["layer_id"])
        rows = sorted((f["surf_proj_m2"], f["surf_3d_m2"], f["couv_mnt"])
                      for f in output.getFeatures())
        # 30 m sous le trou (lignes 115-145) : complet ; carré de 100 m : couverture < 95 %
        assert rows[0][1] is not None and abs(rows[0][1] / rows[0][0] - 1.1547) < 1e-3, rows
        assert rows[1][1] in (None, NULL) and rows[1][2] < 95, rows
        assert result.data["incomplete"] == 1 and result.data["sum_3d_m2"] is None
        assert any("moins de 95 %" in w for w in result.warnings), result.warnings
        project.removeAllMapLayers()
        project.setPresetHomePath("")
    print("✓ Surface 3D : plan 30° = 1/cos 30°, horizontal = 1, plafond 85°, trou signalé")


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
    check_surface_3d()
    check_geographic_rejected()
    APP.exitQgis()
