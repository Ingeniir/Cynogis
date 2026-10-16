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
from ..core.jobs import Pacer, Steps
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


def _zones(by_nature: dict[str, list[QgsGeometry]], distances: list[float], rings: list[str],
           warnings: list[str]) -> tuple[list[tuple[str, QgsGeometry]], QgsGeometry]:
    """Zones d'impact : une zone directe par nature (sans double compte, ordre alphabétique)
    puis les anneaux indirects ; renvoie aussi l'emprise directe totale."""
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
    assert direct is not None  # au moins une nature (contrôlé par l'appelant)
    inner = direct
    for distance, label in zip(distances, rings, strict=True):
        outer = direct.buffer(distance, 16)
        zones.append((label, outer.difference(inner)))
        inner = outer
    return zones, direct


def _intersect(zones: list[tuple[str, QgsGeometry]], habitats, class_field: str,
               stake_field: str | None, warnings: list[str]) -> Steps:
    """Morceaux d'habitat de chaque zone : (pieces pour le tableau, shapes pour la couche,
    surfaces totales des habitats, surfaces des zones). Zone hors couche : UNMAPPED."""
    da = distance_area(habitats.crs())
    categories = [label for label, _ in zones]
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
    pace = Pacer("croisement avec les habitats", habitats.featureCount())
    for done, (feature, geometry) in enumerate(
            iter_geometries(habitats, feature_request(habitats, None, fields))):
        yield from pace(done)
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
    return pieces, shapes, totals, zone_areas


def _check_layers(habitats, footprints) -> None:
    for layer in (habitats, *footprints):
        if geometry_kind(layer) != "polygon":
            raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche "
                            "de polygones.")
    if habitats.crs().isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{habitats.name()} est en degrés : "
                        "reprojette-la (reproject_layer) pour des tampons en mètres.")


def _distances(indirect_buffers_m: list | None) -> tuple[list[float], list[str]]:
    values = [50.0] if indirect_buffers_m is None else [float(d) for d in indirect_buffers_m]
    try:
        return values, impacts.ring_labels(values)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc


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
                          output_name: str | None) -> Steps:
    """Surfaces d'habitat détruites (impact direct : emprise croisée avec les habitats, par nature
    d'emprise) et dégradées (impact indirect : anneaux autour de l'emprise, emprise exclue),
    par type d'habitat et, avec stake_field, par enjeu. Chaque m² n'est compté qu'une fois,
    dans la catégorie la plus proche ; « Non cartographié » = emprise hors couche d'habitats.
    Tableau (surface par catégorie, part détruite de chaque habitat) et couche des
    surfaces impactées. Défaut indirect : 0-50 m."""
    habitats = get_vector_layer(habitats_layer_id)
    footprint = get_vector_layer(footprint_layer_id)
    _check_layers(habitats, [footprint])
    crs = habitats.crs()
    class_field = require_field(habitats, class_field)
    stake_field = require_field(habitats, stake_field) if stake_field else None
    nature_field = require_field(footprint, nature_field) if nature_field else None
    distances, rings = _distances(indirect_buffers_m)

    by_nature: dict[str, list[QgsGeometry]] = {}
    request = feature_request(footprint, None, [nature_field] if nature_field else [])
    for feature, geometry in iter_geometries(footprint, request, crs):
        key = str(group_key(feature[nature_field])) if nature_field else ""
        by_nature.setdefault(key, []).append(geometry)
    if not by_nature:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{footprint.name()} ne contient aucun "
                        "polygone.")
    warnings: list[str] = []
    zones, _ = _zones(by_nature, distances, rings, warnings)
    categories = [label for label, _ in zones]
    pieces, shapes, totals, zone_areas = yield from _intersect(
        zones, habitats, class_field, stake_field, warnings)

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


@tool(level=Level.CREATE, params={
    "habitats_layer_id": Param("string", "Polygones d'habitat (layer_id), en SCR projeté."),
    "class_field": Param("string", "Champ du type d'habitat."),
    "variant_layer_ids": Param("array", "Une couche d'emprise par variante (layer_id) ; le nom "
                               "de la couche nomme la variante.", required=False,
                               items="string"),
    "footprint_layer_id": Param("string", "Ou une seule couche d'emprises (layer_id) avec "
                                "variant_field.", required=False),
    "variant_field": Param("string", "Champ nommant la variante dans footprint_layer_id.",
                           required=False),
    "stake_field": Param("string", "Champ d'enjeu des habitats (ex. enj_niv ou enj_lib de "
                         "stake_scoring) : impact direct ventilé et score pondéré.",
                         required=False),
    "stake_weights": Param("object", "Poids par enjeu, ex. {\"Faible\": 1, \"Fort\": 5, "
                           "\"Majeur\": 20}. Défaut : valeur numérique de l'enjeu, ou niveau "
                           "1-5 de la grille Cynogis.", required=False),
    "indirect_buffers_m": Param("array", "Anneaux d'impact indirect (m), ex. [50, 200].",
                                required=False, items="number"),
    "points_layer_id": Param("string", "Observations sensibles (layer_id), ex. sortie de "
                             "taxon_status_join.", required=False),
    "points_filter": Param("string", "Observations retenues, ex. \"prot_terr\" = 1.",
                           required=False),
    "reference_variant": Param("string", "Variante de référence des gains d'évitement. "
                               "Défaut : la plus impactante.", required=False),
    "create_layer": Param("boolean", "Couche des surfaces impactées de toutes les variantes.",
                          required=False, default=True),
    "export_format": Param("string", "Tableaux dans mcp_outputs/ (comparatif et détail par "
                           "habitat), ou none.", required=False, default="xlsx",
                           enum=(*TABLE_FORMATS, "none")),
    "output_name": Param("string", "Nom des fichiers produits.", required=False),
})
def erc_variant_compare(habitats_layer_id: str, class_field: str,
                        variant_layer_ids: list | None, footprint_layer_id: str | None,
                        variant_field: str | None, stake_field: str | None,
                        stake_weights: dict | None, indirect_buffers_m: list | None,
                        points_layer_id: str | None, points_filter: str | None,
                        reference_variant: str | None, create_layer: bool,
                        export_format: str, output_name: str | None) -> Steps:
    """Démarche ERC, étape « éviter » : compare les variantes d'emprise sur les mêmes
    habitats et chiffre leurs impacts résiduels. Par variante : emprise, impact direct et
    indirect (ha), impact direct par enjeu, habitats touchés, observations sensibles en
    emprise et en périphérie, score pondéré (surface directe multipliée par le poids de
    l'enjeu), surface et score évités par rapport à la référence, rang (1 = moindre impact).
    Les poids relèvent de la méthode du bureau d'études : les faire valider."""
    habitats = get_vector_layer(habitats_layer_id)
    class_field = require_field(habitats, class_field)
    stake_field = require_field(habitats, stake_field) if stake_field else None
    crs = habitats.crs()
    variants: dict[str, list[QgsGeometry]] = {}
    sources = []
    if variant_layer_ids:
        for layer_id in variant_layer_ids:
            layer = get_vector_layer(layer_id)
            sources.append(layer)
            variants[layer.name()] = [g for _, g in iter_geometries(
                layer, feature_request(layer, None, []), crs)]
    elif footprint_layer_id and variant_field:
        layer = get_vector_layer(footprint_layer_id)
        sources.append(layer)
        variant_field = require_field(layer, variant_field)
        request = feature_request(layer, None, [variant_field])
        for feature, geometry in iter_geometries(layer, request, crs):
            variants.setdefault(str(group_key(feature[variant_field])), []).append(geometry)
    else:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Indique variant_layer_ids, ou "
                        "footprint_layer_id avec variant_field.")
    _check_layers(habitats, sources)
    variants = {name: geoms for name, geoms in variants.items() if geoms}
    if len(variants) < 2:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{len(variants)} variante(s) avec une "
                        "emprise : au moins 2 nécessaires.")
    distances, rings = _distances(indirect_buffers_m)
    points: list[QgsGeometry] = []
    if points_layer_id:
        layer = get_vector_layer(points_layer_id)
        if geometry_kind(layer) != "point":
            raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche "
                            "de points.")
        request = feature_request(layer, points_filter, [])
        points = [g for _, g in iter_geometries(layer, request, crs)]

    da = distance_area(crs)
    warnings: list[str] = []
    results: dict[str, dict] = {}
    detail_rows: list[list] = []
    all_shapes: list[tuple] = []
    stakes_seen: list[str] = []
    detail_headers: list[str] = []
    for name, geometries in variants.items():
        notes: list[str] = []
        zones, direct = _zones({"": geometries}, distances, rings, notes)
        categories = [label for label, _ in zones]
        pieces, shapes, totals, _ = yield from _intersect(
            zones, habitats, class_field, stake_field, notes)
        warnings += [f"{name} : {n}" for n in notes]
        mapped_direct = [p for p in pieces if p[2] == impacts.DIRECT and p[0] != UNMAPPED]
        by_stake: dict[str, float] = {}
        for _, stake, _, area in mapped_direct:
            key = str(stake) if stake_field else "-"
            by_stake[key] = by_stake.get(key, 0.0) + area
            if stake_field and key not in stakes_seen:
                stakes_seen.append(key)
        outer = direct.buffer(distances[-1], 16) if distances else direct
        results[name] = {
            "footprint": area_m2(da, direct),
            "direct": sum(p[3] for p in mapped_direct),
            "indirect": sum(p[3] for p in pieces
                            if p[2] != impacts.DIRECT and p[0] != UNMAPPED),
            "by_stake": by_stake,
            "habitats": len({p[0] for p in mapped_direct}),
            "points_direct": (sum(1 for g in points if direct.intersects(g))
                              if points_layer_id else None),
            "points_indirect": (sum(1 for g in points
                                    if outer.intersects(g) and not direct.intersects(g))
                                if points_layer_id else None),
            "weighted": sum(area * impacts.stake_weight(stake if stake_field else None,
                                                        stake_weights)
                            for _, stake, _, area in mapped_direct),
        }
        detail_headers, rows = impacts.build_table(pieces, totals, categories)
        detail_rows += [[name, *row] for row in rows]
        all_shapes += [(name, *shape) for shape in shapes]
    stakes_order = sorted(stakes_seen,
                          key=lambda s: (-impacts.stake_weight(s, stake_weights), s))
    try:
        headers, rows = impacts.compare_variants(results, reference_variant, stakes_order)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    if not points_layer_id:
        drop = {headers.index("Observations sensibles (direct)"),
                headers.index("Observations sensibles (indirect)")}
        headers = [h for i, h in enumerate(headers) if i not in drop]
        rows = [[v for i, v in enumerate(r) if i not in drop] for r in rows]
    base = output_name or "variantes_erc"
    data: dict[str, Any] = {"variants": len(variants), "headers": headers, "rows": rows,
                            "best": rows[0][0], "indirect_rings": rings,
                            "weighted_by": "enjeu" if stake_field else "surface"}
    outputs: list[str] = []
    if export_format != "none":
        path, more = write_table(base, headers, rows, export_format)
        detail, more2 = write_table(f"{base}_detail", ["Variante", *detail_headers],
                                    detail_rows, export_format)
        data.update(table_path=str(path), detail_path=str(detail))
        outputs += [str(path), str(detail)]
        warnings += more + more2
    result = ToolResult(data, warnings, outputs)
    if create_layer and all_shapes:
        layer_fields = QgsFields()
        for spec in (("variante", "string", 80), ("impact", "string", 60),
                     ("habitat", "string", 160), ("enjeu", "string", 40),
                     ("surface_ha", "real", 0)):
            layer_fields.append(make_field(*spec))
        memory = QgsMemoryProviderUtils.createMemoryLayer("variantes", layer_fields,
                                                          Qgis.WkbType.MultiPolygon, crs)
        features = []
        for name, label, habitat, stake, piece, area in all_shapes:
            piece.convertToMultiType()
            feature = QgsFeature(layer_fields)
            feature.setGeometry(piece)
            feature.setAttributes([name, label, habitat, stake, round(area / 10_000, 4)])
            features.append(feature)
        notes = add_to_memory(memory, features)
        saved = save_to_project(memory, f"{base}_surfaces")
        result.data["impact_layer"] = saved.data["outputs"][0]
        result.outputs.extend(saved.outputs)
        result.warnings.extend(notes + [w for w in saved.warnings if w not in result.warnings])
    return result
