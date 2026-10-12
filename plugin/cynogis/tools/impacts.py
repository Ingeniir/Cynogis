"""Quantification des impacts d'un projet sur les habitats (direct / indirect)."""
from __future__ import annotations

from typing import Any

from qgis.core import (
    Qgis,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
)

from ..core import impacts
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    add_to_memory,
    area_m2,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    iter_geometries,
    make_field,
    polygon_parts,
    require_field,
)
from .export import TABLE_FORMATS, write_table
from .outputs import save_to_project

UNMAPPED = "Non cartographié"
MIN_AREA_M2 = 1.0  # en dessous : arrondis de géométrie, ignorés


@tool(level=Level.CREATE, params={
    "footprint_layer_id": Param("string", "Emprise du projet (layer_id), polygones : "
                                "plateforme, voirie, zone de chantier…"),
    "habitats_layer_id": Param("string", "Polygones d'habitat (layer_id), en SCR projeté, "
                               "ex. sortie de habitat_typology_join ou stake_scoring."),
    "class_field": Param("string", "Champ du type d'habitat, ex. hab_lib, hab_code, "
                         "pays_code."),
    "nature_field": Param("string", "Champ de l'emprise distinguant la nature de l'impact "
                          "direct, ex. « définitive » / « temporaire ». Absent : une seule "
                          "catégorie direct.", required=False),
    "indirect_buffers_m": Param("array", "Anneaux d'impact indirect autour de l'emprise (m), "
                                "croissants, ex. [50, 200] → 0-50 m et 50-200 m. [] : pas "
                                "d'impact indirect.", required=False, items="number"),
    "stake_field": Param("string", "Champ d'enjeu des habitats (ex. enj_lib de stake_scoring) "
                         ": surfaces ventilées par habitat et enjeu.", required=False),
    "create_layer": Param("boolean", "Produire la couche des surfaces impactées.",
                          required=False, default=True),
    "export_format": Param("string", "Tableau dans mcp_outputs/, ou none.", required=False,
                           default="xlsx", enum=(*TABLE_FORMATS, "none")),
    "output_name": Param("string", "Nom des fichiers produits.", required=False),
})
def impact_quantification(footprint_layer_id: str, habitats_layer_id: str, class_field: str,
                          nature_field: str | None, indirect_buffers_m: list | None,
                          stake_field: str | None, create_layer: bool, export_format: str,
                          output_name: str | None) -> ToolResult:
    """Surfaces d'habitat détruites (impact direct : emprise croisée avec les habitats, par nature
    d'emprise) et dégradées (impact indirect : anneaux autour de l'emprise, emprise exclue),
    par type d'habitat et, avec stake_field, par enjeu. Chaque m² n'est compté qu'une fois,
    dans la catégorie la plus proche ; « Non cartographié » = emprise hors couche d'habitats.
    Tableau (surface par catégorie, part détruite de chaque habitat) et couche des
    surfaces impactées. Défaut indirect : 0-50 m."""
    habitats = get_vector_layer(habitats_layer_id)
    footprint = get_vector_layer(footprint_layer_id)
    for layer in (habitats, footprint):
        if geometry_kind(layer) != "polygon":
            raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche "
                            "de polygones.")
    crs = habitats.crs()
    if crs.isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{habitats.name()} est en degrés : "
                        "reprojette-la (reproject_layer) pour des tampons en mètres.")
    class_field = require_field(habitats, class_field)
    stake_field = require_field(habitats, stake_field) if stake_field else None
    nature_field = require_field(footprint, nature_field) if nature_field else None
    try:
        rings = impacts.ring_labels([50] if indirect_buffers_m is None
                                    else indirect_buffers_m)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    distances = [float(d) for d in (indirect_buffers_m if indirect_buffers_m is not None
                                    else [50])]

    # Impact direct : une zone par nature, sans double compte entre natures.
    by_nature: dict[str, list[QgsGeometry]] = {}
    request = feature_request(footprint, None, [nature_field] if nature_field else [])
    for feature, geometry in iter_geometries(footprint, request, crs):
        key = str(group_key(feature[nature_field])) if nature_field else ""
        by_nature.setdefault(key, []).append(geometry)
    if not by_nature:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{footprint.name()} ne contient aucun "
                        "polygone.")
    warnings: list[str] = []
    zones: list[tuple[str, QgsGeometry]] = []
    assigned: QgsGeometry | None = None
    for nature in sorted(by_nature):
        union = QgsGeometry.unaryUnion(by_nature[nature]).makeValid()
        own = union if assigned is None else union.difference(assigned)
        if assigned is not None and union.area() - own.area() > MIN_AREA_M2:
            warnings.append(f"Emprise « {nature} » en partie superposée à une autre nature : "
                            "surface commune comptée une fois (ordre alphabétique).")
        zones.append((impacts.direct_label(nature or None), own))
        assigned = own if assigned is None else QgsGeometry.unaryUnion([assigned, own])
    direct = assigned
    assert direct is not None  # au moins une nature (contrôlé plus haut)
    inner = direct
    for distance, label in zip(distances, rings, strict=True):
        outer = direct.buffer(distance, 16)
        zones.append((label, outer.difference(inner)))
        inner = outer
    categories = [label for label, _ in zones]

    da = distance_area(crs)
    engines = []
    for label, zone in zones:
        engine = QgsGeometry.createGeometryEngine(zone.constGet())
        engine.prepareGeometry()
        engines.append((label, zone, engine))
    pieces: list[tuple[str, str | None, str, float]] = []
    shapes: list[tuple[str, str, str | None, QgsGeometry, float]] = []
    totals: dict[tuple[str, str | None], float] = {}
    covered = {label: 0.0 for label in categories}
    fields = [class_field] + ([stake_field] if stake_field else [])
    for feature, geometry in iter_geometries(habitats, feature_request(habitats, None, fields)):
        habitat = str(group_key(feature[class_field]))
        stake = str(group_key(feature[stake_field])) if stake_field else None
        totals[(habitat, stake)] = totals.get((habitat, stake), 0.0) + area_m2(da, geometry)
        box = geometry.boundingBox()
        for label, zone, engine in engines:
            if not zone.boundingBox().intersects(box) or \
                    not engine.intersects(geometry.constGet()):
                continue
            piece = polygon_parts(geometry.intersection(zone))
            if piece is None:
                continue
            area = area_m2(da, piece)
            if area < MIN_AREA_M2:
                continue
            pieces.append((habitat, stake, label, area))
            shapes.append((label, habitat, stake, piece, area))
            covered[label] += area
    zone_areas = {label: area_m2(da, zone) for label, zone in zones}
    for label in categories:
        rest = zone_areas[label] - covered[label]
        if rest > MIN_AREA_M2:  # emprise ou anneau hors de la couche d'habitats
            pieces.append((UNMAPPED, None, label, rest))
    if not any(covered.values()):
        warnings.append("Aucun habitat dans l'emprise ni ses anneaux : vérifie les couches.")
    for label in categories:
        if covered[label] > zone_areas[label] * 1.001:
            warnings.append(f"{label} : habitats qui se chevauchent, surfaces comptées "
                            "plusieurs fois (check_geometries, resolve_overlaps).")

    headers, rows = impacts.build_table(pieces, totals, categories)
    if not stake_field:  # colonne Enjeu inutile
        headers = [h for i, h in enumerate(headers) if i != 1]
        rows = [[v for i, v in enumerate(r) if i != 1] for r in rows]
    base = output_name or f"impacts_{footprint.name()}"
    data: dict[str, Any] = {
        "categories": categories,
        "category_area_ha": {label: round(zone_areas[label] / 10_000, 4)
                             for label in categories},
        "headers": headers, "rows": rows,
    }
    outputs: list[str] = []
    if export_format != "none":
        path, more = write_table(base, headers, rows, export_format)
        data["table_path"] = str(path)
        outputs.append(str(path))
        warnings += more
    result = ToolResult(data, warnings, outputs)
    if create_layer and shapes:
        layer_fields = QgsFields()
        for spec in (("impact", "string", 60), ("habitat", "string", 160),
                     ("enjeu", "string", 40), ("surface_ha", "real", 0)):
            layer_fields.append(make_field(*spec))
        memory = QgsMemoryProviderUtils.createMemoryLayer("impacts", layer_fields,
                                                          Qgis.WkbType.MultiPolygon, crs)
        features = []
        for label, habitat, stake, piece, area in shapes:
            piece.convertToMultiType()
            feature = QgsFeature(layer_fields)
            feature.setGeometry(piece)
            feature.setAttributes([label, habitat, stake, round(area / 10_000, 4)])
            features.append(feature)
        notes = add_to_memory(memory, features)
        saved = save_to_project(memory, f"{base}_surfaces")
        result.data["impact_layer"] = saved.data["outputs"][0]
        result.outputs.extend(saved.outputs)
        result.warnings.extend(notes + [w for w in saved.warnings if w not in result.warnings])
    return result
