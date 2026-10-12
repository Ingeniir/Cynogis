"""Plans d'échantillonnage : points ou transects aléatoires, stratifiés ou systématiques."""
from __future__ import annotations

import math
import random

from qgis.core import (
    Qgis,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsPointXY,
)

from ..core import sampling
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    add_to_memory,
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    iter_geometries,
    make_field,
    require_field,
)
from .geoprocessing import OUTPUT_NAME
from .outputs import save_to_project

UNITS = ("points", "transects")
ATTEMPTS_PER_UNIT = 2000
WHOLE_AREA = "aire d'étude"


class _Sampler:
    """Tirage dans une géométrie (moteur GEOS préparé), avec distance minimale."""

    def __init__(self, rng: random.Random, min_distance: float):
        self.rng = rng
        self.min_distance = min_distance
        self.placed: list[QgsGeometry] = []

    def _far_enough(self, geometry: QgsGeometry) -> bool:
        return not self.min_distance or all(geometry.distance(other) >= self.min_distance
                                            for other in self.placed)

    def draw(self, zone: QgsGeometry, count: int, unit: str, length: float,
             orientation: float | None) -> list[tuple[QgsGeometry, float | None]]:
        engine = QgsGeometry.createGeometryEngine(zone.constGet())
        engine.prepareGeometry()
        box = zone.boundingBox()
        found: list[tuple[QgsGeometry, float | None]] = []
        for _ in range(count * ATTEMPTS_PER_UNIT):
            if len(found) == count:
                break
            x = self.rng.uniform(box.xMinimum(), box.xMaximum())
            y = self.rng.uniform(box.yMinimum(), box.yMaximum())
            angle = None
            if unit == "points":
                geometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
            else:
                angle = orientation if orientation is not None else self.rng.uniform(0, 180)
                geometry = _segment(x, y, angle, length)
            if engine.contains(geometry.constGet()) and self._far_enough(geometry):
                found.append((geometry, angle))
                self.placed.append(geometry)
        return found


def _segment(x: float, y: float, angle: float, length: float) -> QgsGeometry:
    """Segment centré en (x, y), orienté de angle degrés depuis le nord (sens horaire)."""
    dx, dy = math.sin(math.radians(angle)) * length / 2, math.cos(math.radians(angle)) * length / 2
    return QgsGeometry.fromPolylineXY([QgsPointXY(x - dx, y - dy), QgsPointXY(x + dx, y + dy)])


def _cut(line: QgsGeometry, length: float, gap: float) -> tuple[list[QgsGeometry], float]:
    """Tronçons de length mètres séparés de gap, centrés sur la ligne : la longueur trop
    courte pour un tronçon de plus est partagée entre les deux extrémités. Renvoie les
    tronçons et cette longueur écartée."""
    curve = line.constGet()
    total = curve.length()
    count = math.floor((total + gap) / (length + gap) + 1e-9)
    if count <= 0:
        return [], total
    used = count * length + (count - 1) * gap
    start = (total - used) / 2
    pieces = [QgsGeometry(curve.curveSubstring(start + i * (length + gap),
                                               start + i * (length + gap) + length))
              for i in range(count)]
    return pieces, total - used


def _systematic(zone: QgsGeometry, unit: str, spacing: float, orientation: float,
                rng: random.Random) -> list[tuple[QgsGeometry, float | None]]:
    """Grille de points ou transects parallèles espacés de spacing, départ tiré au hasard."""
    box = zone.boundingBox()
    if unit == "points":
        engine = QgsGeometry.createGeometryEngine(zone.constGet())
        engine.prepareGeometry()
        x0 = box.xMinimum() + rng.uniform(0, spacing)
        y0 = box.yMinimum() + rng.uniform(0, spacing)
        found = []
        for i in range(int((box.xMaximum() - x0) // spacing) + 1):
            for j in range(int((box.yMaximum() - y0) // spacing) + 1):
                point = QgsGeometry.fromPointXY(QgsPointXY(x0 + i * spacing, y0 + j * spacing))
                if engine.contains(point.constGet()):
                    found.append((point, None))
        return found
    center = box.center()
    half = math.hypot(box.width(), box.height()) / 2 + spacing
    theta = math.radians(orientation)
    along = (math.sin(theta), math.cos(theta))
    across = (math.cos(theta), -math.sin(theta))
    start = rng.uniform(0, spacing)
    found = []
    for k in range(-int(half // spacing) - 1, int(half // spacing) + 2):
        offset = start + k * spacing
        cx, cy = center.x() + offset * across[0], center.y() + offset * across[1]
        line = QgsGeometry.fromPolylineXY([
            QgsPointXY(cx - half * along[0], cy - half * along[1]),
            QgsPointXY(cx + half * along[0], cy + half * along[1])])
        clipped = line.intersection(zone)
        for part in clipped.asGeometryCollection() if not clipped.isEmpty() else []:
            if part.type() == Qgis.GeometryType.Line and part.length() > 0:
                found.append((part, orientation))
    return found


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Aire d'étude (layer_id), polygones en SCR projeté ; toutes "
                      "les entités sont fusionnées."),
    "design": Param("string", "random : aléatoire simple ; stratified : aléatoire stratifié "
                    "par strata_layer_id ; systematic : grille ou transects parallèles espacés "
                    "de spacing_m, départ aléatoire.", required=False, default="random",
                    enum=sampling.DESIGNS),
    "unit": Param("string", "Points ou transects.", required=False, default="points",
                  enum=UNITS),
    "count": Param("integer", "random / stratified : nombre total d'unités.", required=False,
                   default=30, minimum=1, maximum=10000),
    "spacing_m": Param("number", "systematic : espacement de la grille ou des transects (m).",
                       required=False, minimum=1),
    "transect_length_m": Param("number", "random / stratified : longueur des transects (m), "
                               "entièrement inclus dans leur strate.", required=False,
                               default=100, minimum=1),
    "segment_length_m": Param("number", "systematic transects : découpe chaque ligne en "
                              "tronçons de cette longueur (m), centrés sur la ligne ; le reste "
                              "est écarté, à parts égales aux deux extrémités.",
                              required=False, minimum=1),
    "segment_gap_m": Param("number", "systematic transects : espace entre deux tronçons "
                           "(m).", required=False, default=0, minimum=0),
    "orientation_deg": Param("number", "Orientation des transects depuis le nord (0-180°). "
                             "Défaut : aléatoire (random / stratified), 0 nord-sud "
                             "(systematic).", required=False, minimum=0, maximum=180),
    "min_distance_m": Param("number", "random / stratified : distance minimale entre unités "
                            "(m), ex. 200 m entre points d'écoute.", required=False, default=0,
                            minimum=0),
    "strata_layer_id": Param("string", "Polygones des strates (layer_id), ex. habitats : "
                             "obligatoire pour stratified ; sinon sert à étiqueter les unités.",
                             required=False),
    "strata_field": Param("string", "Champ de la strate (ex. hab_code, pays_code).",
                          required=False),
    "allocation": Param("string", "stratified : proportional (à la surface) ou equal.",
                        required=False, default="proportional", enum=sampling.ALLOCATIONS),
    "min_per_stratum": Param("integer", "stratified : unités minimales par strate.",
                             required=False, default=1, minimum=0),
    "seed": Param("integer", "Graine du tirage, pour reproduire le plan. Défaut : tirée et "
                  "renvoyée.", required=False),
    "output_name": OUTPUT_NAME,
})
def transect_sampling_plan(layer_id: str, design: str, unit: str, count: int,
                           spacing_m: float | None, transect_length_m: float,
                           segment_length_m: float | None, segment_gap_m: float,
                           orientation_deg: float | None, min_distance_m: float,
                           strata_layer_id: str | None, strata_field: str | None,
                           allocation: str, min_per_stratum: int, seed: int | None,
                           output_name: str | None) -> ToolResult:
    """Plan d'échantillonnage (nouvelle couche) : points ou transects dans l'aire d'étude,
    aléatoires, stratifiés par habitat ou systématiques. Champs : id (P001 / T001), plan,
    strate, x et y (points) ou longueur_m, angle et ligne (transects ; ligne = n° de la
    ligne systématique d'origine d'un tronçon). Renvoie la graine (seed) pour reproduire le
    plan et la répartition par strate."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    if layer.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{layer.name()} est en degrés : "
                        "reprojette-la (reproject_layer) pour des distances en mètres.")
    if design == "systematic" and not spacing_m:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Le plan systematic exige spacing_m.")
    if segment_length_m and not (design == "systematic" and unit == "transects"):
        raise ToolError(ErrorCode.INVALID_PARAMS, "segment_length_m ne s'applique qu'aux "
                        "transects systematic (les autres ont transect_length_m).")
    if design == "stratified" and not strata_layer_id:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Le plan stratified exige strata_layer_id "
                        "et strata_field.")
    if bool(strata_layer_id) != bool(strata_field):
        raise ToolError(ErrorCode.INVALID_PARAMS, "strata_layer_id et strata_field vont "
                        "ensemble.")
    parts = [g for _, g in iter_geometries(layer, feature_request(layer, None, []))]
    if not parts:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucun polygone.")
    area = QgsGeometry.unaryUnion(parts).makeValid()

    strata: dict[str, QgsGeometry] = {}
    if strata_layer_id and strata_field:
        strata_layer = get_vector_layer(strata_layer_id)
        strata_field = require_field(strata_layer, strata_field)
        pieces: dict[str, list[QgsGeometry]] = {}
        request = feature_request(strata_layer, None, [strata_field])
        for feature, geometry in iter_geometries(strata_layer, request, layer.crs()):
            piece = geometry.intersection(area)
            if not piece.isEmpty() and piece.area() > 0:
                pieces.setdefault(str(group_key(feature[strata_field])), []).append(piece)
        strata = {k: QgsGeometry.unaryUnion(v).makeValid() for k, v in pieces.items()}
        if not strata:
            raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune strate dans l'aire d'étude.")

    seed = seed if seed is not None else random.SystemRandom().randrange(1, 10**6)
    rng = random.Random(seed)
    warnings: list[str] = []
    units: list[tuple[str | None, QgsGeometry, float | None]] = []
    lines: list[int | None] = []  # n° de ligne systématique de chaque unité
    allocated: dict[str, int] = {}
    leftover = 0.0
    if design == "systematic":
        orientation = orientation_deg if orientation_deg is not None else 0.0
        for number, (geometry, angle) in enumerate(
                _systematic(area, unit, float(spacing_m), orientation, rng), start=1):
            pieces = [geometry]
            if segment_length_m:
                pieces, rest = _cut(geometry, float(segment_length_m), float(segment_gap_m))
                leftover += rest
            units += [(WHOLE_AREA, piece, angle) for piece in pieces]
            lines += [number if unit == "transects" else None] * len(pieces)
    else:
        zones = strata if design == "stratified" else {WHOLE_AREA: area}
        try:
            allocated = (sampling.allocate(count, {k: g.area() for k, g in zones.items()},
                                           allocation, min_per_stratum)
                         if design == "stratified" else {WHOLE_AREA: count})
        except ValueError as exc:
            raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
        sampler = _Sampler(rng, float(min_distance_m))
        for key, wanted in allocated.items():
            drawn = sampler.draw(zones[key], wanted, unit, float(transect_length_m),
                                 orientation_deg)
            units += [(key, g, a) for g, a in drawn]
            lines += [None] * len(drawn)
            if len(drawn) < wanted:
                warnings.append(f"Strate {key} : {len(drawn)}/{wanted} unité(s) placée(s) "
                                "(strate trop petite pour la longueur ou la distance "
                                "minimale).")
    if not units:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Aucune unité placée : réduis spacing_m, "
                        "transect_length_m ou min_distance_m.")
    if strata and design != "stratified":  # étiquette de strate pour les autres plans
        engines = {k: QgsGeometry.createGeometryEngine(g.constGet()) for k, g in strata.items()}
        for engine in engines.values():
            engine.prepareGeometry()
        units = [(next((k for k, e in engines.items()
                        if e.intersects(g.centroid().constGet())), None), g, a)
                 for _, g, a in units]

    fields = QgsFields()
    names = (("id", "string", 12), ("plan", "string", 12), ("strate", "string", 80))
    names += ((("x", "real", 0), ("y", "real", 0)) if unit == "points"
              else (("longueur_m", "real", 0), ("angle", "real", 0), ("ligne", "integer", 0)))
    for spec in names:
        fields.append(make_field(*spec))
    kind = Qgis.WkbType.Point if unit == "points" else Qgis.WkbType.LineString
    memory = QgsMemoryProviderUtils.createMemoryLayer("plan", fields, kind, layer.crs())
    prefix = "P" if unit == "points" else "T"
    features = []
    for index, (key, geometry, angle) in enumerate(units, start=1):
        feature = QgsFeature(fields)
        feature.setGeometry(geometry)
        if unit == "points":
            point = geometry.asPoint()
            extra = [round(point.x(), 2), round(point.y(), 2)]
        else:
            extra = [round(geometry.length(), 1), None if angle is None else round(angle, 1),
                     lines[index - 1]]
        feature.setAttributes([sampling.unit_id(prefix, index, len(units)), design, key,
                               *extra])
        features.append(feature)
    notes = add_to_memory(memory, features)
    result = save_to_project(memory, output_name or f"plan_{design}_{unit}")
    result.warnings.extend(notes + warnings)
    per_stratum: dict[str, int] = {}
    for key, _, _ in units:
        per_stratum[str(key)] = per_stratum.get(str(key), 0) + 1
    result.data.update({
        "design": design, "unit": unit, "seed": seed, "placed": len(units),
        "allocated": allocated or None, "per_stratum": per_stratum,
        "area_ha": round(area.area() / 10_000.0, 4),
        "spacing_m": spacing_m, "min_distance_m": min_distance_m,
        "segment_length_m": segment_length_m,
        "segment_gap_m": segment_gap_m if segment_length_m else None,
        "unused_length_m": round(leftover, 1) if segment_length_m else None,
        "total_length_m": round(sum(g.length() for _, g, _ in units), 1)
        if unit == "transects" else None,
    })
    return result
