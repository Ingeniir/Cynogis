"""Référentiels d'occupation du sol (OCS GE de l'IGN, cartes du CIRAD) : découpage sur une
zone d'étude et traduction dans la nomenclature des paysages Cynogis."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsProject,
    QgsSpatialIndex,
    QgsVectorLayer,
)

from ..core import landscape as nomenclature
from ..core import referentials as refs
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.metrics import M2_PER_HA
from ..core.registry import Level, tool
from ..core.schema import Param
from .common import (
    area_m2,
    distance_area,
    feature_request,
    geometry_kind,
    get_vector_layer,
    iter_geometries,
    make_field,
    require_field,
    select_ids,
    to_json_value,
)
from .geoprocessing import OUTPUT_NAME
from .landscape import _territory
from .outputs import run_in_memory, save_to_project

OUTPUT_FIELDS = (("pays_code", "string", 10), ("pays_lib", "string", 80),
                 ("pays_grp", "string", 40), ("pays_surf", "real", 0))
Piece = tuple[QgsGeometry, dict, str]  # géométrie, résultat de map_feature, code source lisible


def _open(source: refs.Source) -> QgsVectorLayer:
    """Couche du référentiel (non ajoutée au projet)."""
    path = refs.find_source_file(source)
    if path is None:
        raise ToolError(ErrorCode.FILE_NOT_FOUND,
                        f"Référentiel {source.key} absent : enregistre-le sous "
                        f"{source.key}.gpkg (ou .shp) dans {refs.referentials_directory()}. "
                        f"Téléchargement : {source.url}")
    layer = None
    if source.layer_name and path.suffix.lower() == ".gpkg":
        layer = QgsVectorLayer(f"{path}|layername={source.layer_name}", source.key, "ogr")
    if layer is None or not layer.isValid():  # GeoPackage à une seule couche, Shapefile
        layer = QgsVectorLayer(str(path), source.key, "ogr")
    if not layer.isValid():
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{path} illisible par QGIS.")
    return layer


def _polygonal(geometry: QgsGeometry) -> QgsGeometry | None:
    """Parties surfaciques seules : un voisin qui touche la zone d'étude donne une ligne, que
    convertToType changerait en polygone d'aire nulle."""
    parts = [part for part in geometry.asGeometryCollection()
             if part.type() == Qgis.GeometryType.Polygon and not part.isEmpty()]
    return QgsGeometry.collectGeometry(parts) if parts else None


def _clipped(source: refs.Source, aoi: QgsGeometry,
             crs: QgsCoordinateReferenceSystem) -> list[Piece]:
    """Entités du référentiel découpées par la zone d'étude (SCR crs) et traduites."""
    layer = _open(source)
    fields = [require_field(layer, name) for name in source.code_fields]
    rect = aoi.boundingBox()
    if layer.crs() != crs:
        rect = QgsCoordinateTransform(crs, layer.crs(),
                                      QgsProject.instance()).transformBoundingBox(rect)
    request = feature_request(layer, None, fields)
    request.setFilterRect(rect)  # indispensable : un référentiel départemental est énorme
    engine = QgsGeometry.createGeometryEngine(aoi.constGet())
    engine.prepareGeometry()
    pieces: list[Piece] = []
    for feature, geometry in iter_geometries(layer, request, crs):
        if not engine.intersects(geometry.constGet()):
            continue
        piece = _polygonal(geometry if engine.contains(geometry.constGet())
                           else geometry.intersection(aoi))
        if piece is None:
            continue
        values = {name: to_json_value(feature[field])
                  for name, field in zip(source.code_fields, fields, strict=True)}
        label = " / ".join(str(v) for v in values.values() if v is not None) or "(vide)"
        pieces.append((piece, refs.map_feature(source, values), label))
    return pieces


def _overlay(pieces: list[Piece], priority: list[Piece]) -> tuple[list[Piece], int]:
    """Les parties agricoles de pieces sont remplacées par les classes agricoles de priority
    là où elles existent (ex. canne du CIRAD sur « culture » de l'OCS GE)."""
    agricultural = [(g, m, label) for g, m, label in priority
                    if refs.is_agricultural(m["code"])]
    index = QgsSpatialIndex()
    for position, (geometry, _, _) in enumerate(agricultural):
        index.addFeature(position, geometry.boundingBox())
    result: list[Piece] = []
    replaced = 0
    for geometry, mapped, label in pieces:
        hits = [agricultural[i] for i in index.intersects(geometry.boundingBox())
                if agricultural[i][0].intersects(geometry)] \
            if refs.is_agricultural(mapped["code"]) else []
        if not hits:
            result.append((geometry, mapped, label))
            continue
        replaced += 1
        for other, other_mapped, other_label in hits:
            part = _polygonal(geometry.intersection(other))
            if part is not None:
                result.append((part, other_mapped, other_label))
        rest = _polygonal(geometry.difference(QgsGeometry.unaryUnion([h[0] for h in hits])))
        if rest is not None:
            result.append((rest, mapped, label))
    return result, replaced


@tool(level=Level.READ, params={
    "layer_id": Param("string", "Zone d'étude (layer_id) : son territoire filtre les "
                      "sources. Absent : toutes les sources.", required=False),
})
def list_reference_sources(layer_id: str | None) -> ToolResult:
    """Référentiels d'occupation du sol connus (OCS GE IGN, cartes CIRAD) pour le territoire
    de la zone d'étude, avec leur présence sur disque. À appeler avant
    clip_reference_landcover."""
    territory = _territory(None, get_vector_layer(layer_id)) if layer_id else None
    directory = refs.referentials_directory()
    sources, missing = [], []
    for source in refs.sources_for(territory):
        path = refs.find_source_file(source, directory)
        sources.append({"key": source.key, "kind": source.kind, "year": source.year,
                        "territory": source.landscape_territory,
                        "available": path is not None, "path": str(path) if path else None,
                        "download": source.url})
        if path is None:
            missing.append(source)
    warnings = []
    if layer_id and territory is None:
        warnings.append("Territoire non détecté depuis l'emprise : toutes les sources listées.")
    if missing:
        warnings.append(f"Absents de {directory} : {', '.join(s.key for s in missing)}. "
                        "Télécharger depuis "
                        f"{', '.join(sorted({s.url for s in missing}))} puis enregistrer "
                        "sous <clé>.gpkg (ou .shp).")
    return ToolResult({"territory": territory, "directory": str(directory),
                       "sources": sources}, warnings)


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche de polygones de la zone d'étude (layer_id)."),
    "source": Param("string", "Clé du référentiel (voir list_reference_sources), ex. "
                    "ocsge_974_2022.", enum=tuple(refs.BY_KEY)),
    "feature_ids": Param("array", "Entités de la zone d'étude à utiliser. Absent : toutes.",
                         required=False, items="integer"),
    "overlay_sources": Param("array", "Sources prioritaires sur les surfaces agricoles, ex. "
                             '["cirad_974_2020"] : la canne, les prairies… du CIRAD remplacent '
                             "les cultures indifférenciées de l'OCS GE.", required=False,
                             items="string", items_enum=tuple(refs.BY_KEY)),
    "output_name": OUTPUT_NAME,
})
def clip_reference_landcover(layer_id: str, source: str, feature_ids: list | None,
                             overlay_sources: list | None, output_name: str | None) -> ToolResult:
    """Découpe un référentiel d'occupation du sol (OCS GE, CIRAD) sur la zone d'étude et le
    traduit dans la nomenclature paysagère Cynogis : couche de paysages (pays_code, pays_lib,
    pays_grp, pays_surf) dans mcp_outputs/. Rapide, sans entraînement. Ensuite :
    apply_landscape_style, landscape_metrics (class_field=pays_code), write_report."""
    area_layer = get_vector_layer(layer_id)
    if geometry_kind(area_layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{area_layer.name()} n'est pas une couche "
                        "de polygones.")
    primary = refs.BY_KEY[source]
    warnings: list[str] = []
    detected = _territory(None, area_layer)
    if detected and detected != primary.landscape_territory:
        warnings.append(f"Zone d'étude détectée à {detected}, référentiel de "
                        f"{primary.landscape_territory} : vérifie la source.")
    request = QgsFeatureRequest()
    if feature_ids:
        request.setFilterFids(select_ids(area_layer, None, feature_ids))
    request.setNoAttributes()
    parts = [geometry for _, geometry in iter_geometries(area_layer, request)]
    if not parts:
        raise ToolError(ErrorCode.INVALID_PARAMS, "Zone d'étude vide.")
    aoi = QgsGeometry.unaryUnion(parts)
    if not aoi.isGeosValid():
        aoi = aoi.makeValid()
    crs = area_layer.crs()

    pieces = _clipped(primary, aoi, crs)
    replaced = 0
    for key in dict.fromkeys(overlay_sources or []):
        overlay = refs.BY_KEY[key]
        if overlay.territory != primary.territory or key == source:
            raise ToolError(ErrorCode.INVALID_PARAMS, f"{key} ne peut pas compléter {source} "
                            "(autre territoire ou même source).")
        pieces, count = _overlay(pieces, _clipped(overlay, aoi, crs))
        replaced += count

    da = distance_area(crs)
    unmapped: dict[str, list[float]] = {}
    review: dict[str, float] = defaultdict(float)
    kept: list[QgsFeature] = []
    fields = QgsFields()
    fields.append(make_field("pays_code", "string", 10))
    for geometry, mapped, label in pieces:
        surface = area_m2(da, geometry)
        if mapped["code"] is None:
            entry = unmapped.setdefault(label, [0, 0.0])
            entry[0] += 1
            entry[1] += surface
            continue
        if mapped["review"]:
            review[mapped["note"] or "Correspondance à vérifier."] += surface
        feature = QgsFeature(fields)
        feature["pays_code"] = mapped["code"]
        feature.setGeometry(geometry)
        kept.append(feature)
    if not kept:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Aucune entité de {source} rattachée à la "
                        "nomenclature dans la zone d'étude (zone hors emprise du référentiel ?).")
    raw = QgsMemoryProviderUtils.createMemoryLayer("referentiel", fields,
                                                   Qgis.WkbType.MultiPolygon, crs)
    raw.dataProvider().addFeatures(kept)
    dissolved = run_in_memory("native:dissolve", {"INPUT": raw, "FIELD": ["pays_code"]})
    singles = run_in_memory("native:multiparttosingleparts", {"INPUT": dissolved})

    out_fields = QgsFields()
    for name, type_name, length in OUTPUT_FIELDS:
        out_fields.append(make_field(name, type_name, length))
    final = QgsMemoryProviderUtils.createMemoryLayer("paysages", out_fields,
                                                     singles.wkbType(), crs)
    summary: dict[str, dict[str, Any]] = {}
    features = []
    for feature in singles.getFeatures():
        item = nomenclature.BY_CODE[feature["pays_code"]]
        surface = area_m2(da, feature.geometry())
        new = QgsFeature(out_fields)
        new.setAttributes([item.code, item.label, nomenclature.GROUPS[item.group],
                           round(surface, 2)])
        new.setGeometry(feature.geometry())
        features.append(new)
        bucket = summary.setdefault(item.code, {"code": item.code, "label": item.label,
                                                "count": 0, "area_m2": 0.0})
        bucket["count"] += 1
        bucket["area_m2"] += surface
    final.dataProvider().addFeatures(features)

    result = save_to_project(final, output_name or f"paysages_{source}")
    total = sum(b["area_m2"] for b in summary.values())
    classes = sorted(({"code": b["code"], "label": b["label"], "count": b["count"],
                       "area_ha": round(b["area_m2"] / M2_PER_HA, 4),
                       "percent": round(b["area_m2"] / total * 100, 2) if total else None}
                      for b in summary.values()), key=lambda b: -b["area_ha"])
    result.data.update({
        "source": source, "overlay_sources": list(dict.fromkeys(overlay_sources or [])),
        "territory": primary.landscape_territory, "classes": classes,
        "agricultural_parts_replaced": replaced,
        "to_review": [{"note": note, "area_ha": round(area / M2_PER_HA, 4)}
                      for note, area in sorted(review.items(), key=lambda kv: -kv[1])],
        "next_step": "apply_landscape_style, puis landscape_metrics (class_field=pays_code), "
                     "puis write_report.",
    })
    result.warnings[:0] = warnings
    if unmapped:
        top = sorted(unmapped.items(), key=lambda kv: -kv[1][1])[:10]
        result.warnings.append(
            f"{sum(v[0] for v in unmapped.values())} entité(s) non rattachée(s) "
            f"({sum(v[1] for v in unmapped.values()) / M2_PER_HA:.2f} ha), absentes de la "
            "sortie : " + ", ".join(f"{label} ({v[0]})" for label, v in top) + ".")
    if review:
        result.warnings.append(f"Correspondances à vérifier sur "
                               f"{sum(review.values()) / M2_PER_HA:.2f} ha : voir to_review.")
    return result
