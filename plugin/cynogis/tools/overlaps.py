from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsPointXY,
    QgsProject,
    QgsSpatialIndex,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.jobs import Pacer
from ..core.registry import Level, tool
from ..core.resolve import (
    ORDERS,
    STRATEGIES,
    half_plane_corners,
    needs_priority_field,
    rank_records,
    summarize_resolution,
)
from ..core.schema import Param
from ..core.units import AREA_UNITS, convert_area
from .common import (
    add_to_memory,
    area_m2,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    group_key,
    polygon_parts,
    require_field,
)
from .features import FILTER_HELP
from .geoprocessing import OUTPUT_NAME
from .outputs import Steps, save_to_project


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Couche de polygones à contrôler (layer_id)."),
    "other_layer_id": Param("string", "Seconde couche de polygones. Si absente : chevauchements "
                            "internes à layer_id.", required=False),
    "min_area_m2": Param("number", "Surface minimale d'un chevauchement en m² (ignore les "
                         "micro-recouvrements dus aux arrondis).", required=False, default=0.01,
                         minimum=0),
    "area_unit": Param("string", "Unité des surfaces renvoyées.", required=False, default="m2",
                       enum=tuple(AREA_UNITS)),
    "filter_expression": Param("string", "Filtre sur layer_id. " + FILTER_HELP, required=False),
    "limit": Param("integer", "Nombre max de paires renvoyées (les plus grandes d'abord).",
                   required=False, default=100, minimum=1, maximum=500),
})
def detect_overlaps(layer_id: str, other_layer_id: str | None, min_area_m2: float,
                    area_unit: str, filter_expression: str | None, limit: int) -> Steps:
    """Détecte les chevauchements entre polygones : à l'intérieur d'une couche, ou entre deux
    couches (reprojection automatique). Renvoie les paires de fid qui se chevauchent avec la
    surface commune (mesure ellipsoïdale), triées par surface décroissante, et la surface totale.
    Pour voir les entités concernées : get_features avec filter_expression='$id IN (…)'."""
    layer_a = get_vector_layer(layer_id)
    internal = other_layer_id is None or other_layer_id == layer_id
    layer_b = layer_a if internal else get_vector_layer(other_layer_id)
    for lyr in (layer_a, layer_b):
        if geometry_kind(lyr) != "polygon":
            raise ToolError(ErrorCode.INVALID_PARAMS, f"{lyr.name()} n'est pas une couche de "
                            "polygones.")
    da = distance_area(layer_a.crs(), "ellipsoidal")
    transform = None
    if not internal and layer_b.crs() != layer_a.crs():
        transform = QgsCoordinateTransform(layer_b.crs(), layer_a.crs(), QgsProject.instance())

    # 1. Index spatial de la couche B, géométries gardées en mémoire (dans le SCR de A)
    if internal:
        request_b = feature_request(layer_a, filter_expression, [], True)
    else:
        request_b = QgsFeatureRequest()
        request_b.setNoAttributes()
    index = QgsSpatialIndex()
    geoms_b: dict[int, QgsGeometry] = {}
    transform_failures = 0
    pace = Pacer("lecture des polygones")
    for feature in layer_b.getFeatures(request_b):
        yield from pace()
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            continue
        geom = QgsGeometry(geom)
        if transform is not None:
            try:
                geom.transform(transform)
            except QgsCsException:
                transform_failures += 1
                continue
        geoms_b[feature.id()] = geom
        index.addFeature(feature.id(), geom.boundingBox())

    # 2. Pour chaque polygone A : candidats via l'index, test préparé, puis intersection
    if internal:
        source = list(geoms_b.items())
    else:
        source = ((f.id(), f.geometry()) for f in
                  layer_a.getFeatures(feature_request(layer_a, filter_expression, [], True)))
    pairs: list[tuple[float, int, int]] = []
    checked = failures = 0
    pace = Pacer("recherche des chevauchements", len(geoms_b) if internal else None)
    for fid_a, geom_a in source:
        yield from pace(checked)
        if geom_a.isNull() or geom_a.isEmpty():
            continue
        checked += 1
        candidates = index.intersects(geom_a.boundingBox())
        if internal:
            candidates = [c for c in candidates if c > fid_a]  # chaque paire une seule fois
        if not candidates:
            continue
        engine = QgsGeometry.createGeometryEngine(geom_a.constGet())
        engine.prepareGeometry()
        for fid_b in candidates:
            geom_b = geoms_b[fid_b]
            if not engine.intersects(geom_b.constGet()):
                continue
            intersection = geom_a.intersection(geom_b)
            if intersection.isNull():  # échec GEOS : géométrie invalide probable
                failures += 1
                continue
            area = area_m2(da, intersection)
            if area > 0 and area >= min_area_m2:
                pairs.append((area, fid_a, fid_b))

    pairs.sort(reverse=True)
    total = sum(p[0] for p in pairs)
    data = {
        "mode": "internal" if internal else "between_layers",
        "features_checked": checked,
        "overlap_pairs": len(pairs),
        "area_unit": area_unit,
        "total_overlap_area": round(convert_area(total, area_unit), 4),
        "pairs": [{"fid_a": a, "fid_b": b, "overlap_area": round(convert_area(s, area_unit), 4)}
                  for s, a, b in pairs[:limit]],
        "truncated": len(pairs) > limit,
    }
    warnings = []
    if failures:
        warnings.append(f"{failures} intersection(s) en échec (géométries invalides probables) : "
                        "lance check_geometries.")
    if transform_failures:
        warnings.append(f"{transform_failures} entité(s) de la seconde couche non reprojetables.")
    if internal and pairs:
        warnings.append("Une zone couverte par 3 entités ou plus est comptée plusieurs fois dans "
                        "total_overlap_area.")
    return ToolResult(data, warnings)


STATUS_FIELDS = (("cyn_statut", QMetaType.Type.QString),
                 ("cyn_aire_av", QMetaType.Type.Double),
                 ("cyn_aire_ap", QMetaType.Type.Double))
AREA_TOLERANCE_M2 = 0.001


def _as_multipolygon(geom: QgsGeometry) -> QgsGeometry | None:
    """Ne garde que les parties surfaciques (une différence peut produire lignes ou points)."""
    poly = polygon_parts(geom)
    if poly is not None:
        poly = QgsGeometry(poly)
        poly.convertToMultiType()
    return poly


def _closer_parts(fid: int, neighbours: list[int], geoms: dict[int, QgsGeometry],
                  centres: dict[int, QgsPointXY], ranks: dict[int, int],
                  span: float) -> list[QgsGeometry]:
    """split_equally : parties des voisins plus proches de LEUR centroïde que de celui de fid.

    Un point disputé revient à l'entité qui le couvre et dont le centroïde est le plus proche
    (Voronoï restreint aux entités qui le couvrent) : partage sans trou ni recouvrement.
    """
    me = centres[fid]
    parts = []
    for other in neighbours:
        there = centres[other]
        try:
            corners = half_plane_corners(there.x(), there.y(), me.x(), me.y(), span)
        except ValueError:  # centroïdes confondus : départage par ordre de lecture
            if ranks[other] < ranks[fid]:
                parts.append(geoms[other])
            continue
        half = QgsGeometry.fromPolygonXY([[QgsPointXY(x, y) for x, y in corners]])
        parts.append(geoms[other].intersection(half))
    return parts


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche de polygones (layer_id)."),
    "strategy": Param("string", "Qui garde la zone commune : priority_field (selon un champ), "
                      "keep_largest (la plus grande entité), keep_oldest (plus petite valeur de "
                      "priority_field, ex. date ; sans champ : ordre de lecture), split_equally "
                      "(partage selon la médiatrice entre centroïdes).", required=False,
                      default="keep_largest", enum=STRATEGIES),
    "priority_field": Param("string", "Champ départageant (obligatoire pour priority_field). "
                            "Valeurs nulles = priorité la plus faible.", required=False),
    "priority_order": Param("string", "priority_field : asc = la plus petite valeur gagne, "
                            "desc = la plus grande.", required=False, default="asc", enum=ORDERS),
    "output_name": OUTPUT_NAME,
})
def resolve_overlaps(layer_id: str, strategy: str, priority_field: str | None,
                     priority_order: str, output_name: str | None) -> Steps:
    """Produit une copie de la couche SANS chevauchements : chaque zone couverte par plusieurs
    polygones est attribuée à un seul selon la stratégie ; les autres sont découpés. Attributs
    conservés + champs de contrôle cyn_statut (unchanged/clipped), cyn_aire_av et cyn_aire_ap
    (m², ellipsoïdal). Couche d'origine intacte. Les entités entièrement recouvertes disparaissent
    (fid dans removed_fids). Utilise detect_overlaps avant pour mesurer l'enjeu."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    if needs_priority_field(strategy) and not priority_field:
        raise ToolError(ErrorCode.INVALID_PARAMS,
                        "La stratégie priority_field exige le paramètre priority_field.")
    field = require_field(layer, priority_field) if priority_field else None
    da = distance_area(layer.crs(), "ellipsoidal")

    # 1. Lecture : géométries (réparées si besoin), index spatial, enregistrements de rang
    features: dict[int, QgsFeature] = {}
    geoms: dict[int, QgsGeometry] = {}
    records: list[dict[str, Any]] = []
    index = QgsSpatialIndex()
    repaired = 0
    pace = Pacer("lecture des polygones", layer.featureCount())
    for order, feature in enumerate(layer.getFeatures()):
        yield from pace(order)
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            continue
        if not geom.isGeosValid():
            geom = geom.makeValid()
            repaired += 1
        fid = feature.id()
        features[fid], geoms[fid] = feature, geom
        index.addFeature(fid, geom.boundingBox())
        records.append({"id": fid, "order": order, "area": area_m2(da, geom),
                        "value": group_key(feature[field]) if field else None})
    if not records:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucune géométrie.")
    ranks = rank_records(records, strategy, priority_order)
    area_before = {r["id"]: r["area"] for r in records}
    read_order = {r["id"]: r["order"] for r in records}

    split = strategy == "split_equally"
    if split:
        centres = {fid: g.centroid().asPoint() for fid, g in geoms.items()}
        extent = layer.extent()
        span = max(extent.width() + extent.height(), 1.0) * 4.0

    # 2. Découpe, de la plus prioritaire à la moins prioritaire
    fields = QgsFields(layer.fields())
    for name, kind in STATUS_FIELDS:
        if fields.lookupField(name) < 0:
            fields.append(QgsField(name, kind))
    extra = [None] * (fields.count() - layer.fields().count())
    result = QgsMemoryProviderUtils.createMemoryLayer(
        "resolve_overlaps", fields, QgsWkbTypes.multiType(layer.wkbType()), layer.crs())

    placed: dict[int, QgsGeometry] = {}
    out: list[tuple[int, QgsFeature]] = []
    entries: list[dict[str, Any]] = []
    removed: list[int] = []
    failed: list[int] = []
    pace = Pacer("découpe des chevauchements", len(geoms))
    for done, fid in enumerate(sorted(geoms, key=ranks.__getitem__)):
        yield from pace(done)
        geom = geoms[fid]
        neighbours = [n for n in index.intersects(geom.boundingBox())
                      if n != fid and geoms[n].intersects(geom)]
        if split:
            blockers = _closer_parts(fid, neighbours, geoms, centres, ranks, span)
        else:  # les voisins déjà placés sont, par construction, plus prioritaires
            blockers = [placed[n] for n in neighbours if n in placed]
        blockers = [b for b in blockers if not b.isNull() and not b.isEmpty()]
        if blockers:
            cut = geom.difference(QgsGeometry.unaryUnion(blockers))
            if cut.isNull():  # échec GEOS
                failed.append(fid)
                continue
            geom = cut
        poly = _as_multipolygon(geom)
        after = area_m2(da, poly) if poly is not None else 0.0
        if poly is None or after <= AREA_TOLERANCE_M2:
            status = "removed"
            removed.append(fid)
        elif area_before[fid] - after > AREA_TOLERANCE_M2:
            status = "clipped"
        else:
            status = "unchanged"
        entries.append({"id": fid, "status": status, "area_before": area_before[fid],
                        "area_after": after})
        if status == "removed":
            continue
        placed[fid] = poly
        new = QgsFeature(fields)
        new.setAttributes(features[fid].attributes() + extra)
        new.setGeometry(poly)
        new["cyn_statut"] = status
        new["cyn_aire_av"] = round(area_before[fid], 3)
        new["cyn_aire_ap"] = round(after, 3)
        out.append((read_order[fid], new))
    out.sort(key=lambda item: item[0])
    notes = add_to_memory(result, [f for _, f in out])

    tool_result = save_to_project(result, output_name or f"sans_chevauchement_{layer.name()}")
    tool_result.warnings.extend(notes)
    summary = summarize_resolution(entries)
    tool_result.data.update({
        "strategy": strategy,
        "priority": f"{field} {priority_order}" if field else None,
        "features_in": summary["features_in"],
        "features_out": summary["features_out"],
        "clipped": summary["features_clipped"],
        "removed_count": summary["features_removed"],
        "removed_fids": removed[:200],
        "overlap_area_removed_m2": round(summary["area_removed"], 2),
        "repaired_inputs": repaired,
    })
    if failed:
        tool_result.warnings.append(f"{len(failed)} entité(s) non traitées (échec GEOS), "
                                    f"absentes de la sortie : fid {failed[:50]}.")
    if repaired:
        tool_result.warnings.append(f"{repaired} géométrie(s) invalide(s) réparée(s) à la volée "
                                    "(fix_geometries pour un nettoyage durable).")
    if field is None and strategy == "keep_oldest":
        tool_result.warnings.append("keep_oldest sans priority_field : l'ordre de lecture des "
                                    "entités sert de critère d'ancienneté.")
    return tool_result
