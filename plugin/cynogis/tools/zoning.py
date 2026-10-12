"""Croisement d'un projet avec les zonages réglementaires et d'inventaire (Réunion, Mayotte)."""
from __future__ import annotations

from typing import Any

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextScope,
    QgsFeature,
    QgsFeatureRequest,
    QgsFields,
    QgsGeometry,
    QgsJsonUtils,
    QgsMemoryProviderUtils,
    QgsProject,
    QgsRectangle,
)

from ..core import zoning
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.territory import detect_territory
from .common import (
    add_to_memory,
    area_m2,
    distance_area,
    extent_wgs84,
    feature_request,
    geometry_kind,
    get_vector_layer,
    iter_geometries,
    make_field,
    prepare_expression,
    rect_to_list,
    require_field,
    to_json_value,
)
from .export import TABLE_FORMATS, write_table
from .outputs import save_to_project
from .webservices import _fetch, _service

SERVICE = "geopf_wfs"
WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")
HEADERS = ["Zonage", "Zone", "Statut", "Surface intersectée (ha)", "Part du projet (%)",
           "Part de la zone (%)", "Distance (m)", "Fiche"]


def _wfs_features(typename: str, expression: str | None, search: QgsRectangle, crs,
                  max_features: int) -> list[QgsFeature]:
    """Entités WFS (EPSG:4326) dans l'emprise de recherche, filtrées par l'expression."""
    service, _ = _service(SERVICE)
    box = QgsCoordinateTransform(crs, WGS84, QgsProject.instance()).transformBoundingBox(search)
    url = zoning.getfeature_url(service.url, typename, (box.xMinimum(), box.yMinimum(),
                                                        box.xMaximum(), box.yMaximum()),
                                min(max_features, service.max_features))
    text = _fetch(url, service.authcfg).decode("utf-8")
    fields = QgsJsonUtils.stringToFields(text)
    features = QgsJsonUtils.stringToFeatureList(text, fields)
    if not expression:
        return features
    compiled = QgsExpression(expression)
    context = QgsExpressionContext()
    scope = QgsExpressionContextScope()
    scope.setFields(fields)
    context.appendScope(scope)
    kept = []
    for feature in features:
        context.setFeature(feature)
        if compiled.evaluate(context):
            kept.append(feature)
    return kept


def _sources(item: zoning.Zoning, local: dict[str, list[dict]], search: QgsRectangle, crs,
             max_features: int):
    """[(entités, SCR, champ du nom, champ de la fiche)] à examiner pour un zonage ; les
    couches locales priment sur le flux national."""
    if item.key in local:
        result = []
        for entry in local[item.key]:
            layer = get_vector_layer(str(entry["layer_id"]))
            name_field = entry.get("name_field")
            if name_field:
                name_field = require_field(layer, name_field)
            request = QgsFeatureRequest().setFilterRect(QgsCoordinateTransform(
                crs, layer.crs(), QgsProject.instance()).transformBoundingBox(search))
            if entry.get("filter"):
                prepare_expression(entry["filter"], layer, "filter")
                request.setFilterExpression(entry["filter"])
            result.append((list(layer.getFeatures(request)), layer.crs(), name_field, None))
        return result
    if item.typename is None:
        return []
    return [(_wfs_features(item.typename, item.filter, search, crs, max_features), WGS84,
             item.name_field, item.url_field)]


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Polygone(s) du projet (layer_id), en SCR projeté ; toutes les "
                      "entités sont fusionnées."),
    "zonings": Param("array", "Zonages à examiner (clés) : pn_coeur, pn_adhesion, rnn, pnm, "
                     "apb, cdl, ramsar, znieff1, znieff2, znieff1_mer, znieff2_mer, "
                     "foret_publique, ebc, ens, sar_smvm, loi_littoral, zones_humides. "
                     "Défaut : tous ceux du territoire.", required=False, items="string"),
    "local_layers": Param("array", 'Couches locales, prioritaires sur le flux national : '
                          '[{"zoning": "ens", "layer_id": "...", "name_field": "nom", '
                          '"filter": "\\"type\\" = \'ENS\'"}]. Seule source pour ens, '
                          "sar_smvm, loi_littoral et zones_humides.", required=False,
                          items="object"),
    "search_distance_m": Param("number", "Zones non intersectées listées si elles sont à "
                               "moins de cette distance (m).", required=False, default=1000,
                               minimum=0, maximum=50000),
    "create_layer": Param("boolean", "Produire la couche des intersections (zonage, zone, "
                          "surface).", required=False, default=True),
    "export_format": Param("string", "Tableau dans mcp_outputs/, ou none.", required=False,
                           default="xlsx", enum=(*TABLE_FORMATS, "none")),
    "max_features": Param("integer", "Plafond d'entités téléchargées par zonage.",
                          required=False, default=2000, minimum=1, maximum=50000),
    "output_name": Param("string", "Nom des fichiers produits.", required=False),
})
def regulatory_zoning_intersect(layer_id: str, zonings: list | None,
                                local_layers: list | None, search_distance_m: float,
                                create_layer: bool, export_format: str, max_features: int,
                                output_name: str | None) -> ToolResult:
    """Croise le projet avec les zonages réglementaires et d'inventaire (Parc national cœur
    et aire d'adhésion, réserves naturelles dont Étang de Saint-Paul et Réserve marine, Parc
    naturel marin de Mayotte, APB, Conservatoire du littoral, Ramsar, ZNIEFF I / II
    terrestres et marines, forêts publiques ONF, EBC des PLU) via le WFS de la Géoplateforme,
    et avec les couches locales fournies (ENS, SAR / SMVM, Loi Littoral, zones humides).
    Renvoie par zone : statut (intersecte, à N m, absent), surface intersectée, part du
    projet et de la zone ; checklist par zonage, « non vérifié » si aucune source."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    crs = layer.crs()
    if crs.isGeographic():
        raise ToolError(ErrorCode.CRS_GEOGRAPHIC, f"{layer.name()} est en degrés : "
                        "reprojette-la (reproject_layer) pour des surfaces et distances.")
    parts = [g for _, g in iter_geometries(layer, feature_request(layer, None, []))]
    if not parts:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} ne contient aucun polygone.")
    project = QgsGeometry.unaryUnion(parts).makeValid()
    da = distance_area(crs)
    project_m2 = area_m2(da, project)
    territory = detect_territory(rect_to_list(extent_wgs84(layer)))
    local: dict[str, list[dict]] = {}
    for entry in local_layers or []:
        if "zoning" not in entry or "layer_id" not in entry:
            raise ToolError(ErrorCode.INVALID_PARAMS, "local_layers : zoning et layer_id "
                            "requis pour chaque couche.")
        local.setdefault(str(entry["zoning"]), []).append(entry)
    keys = list(zonings or [])
    try:
        items = zoning.for_territory(territory.code if territory else None, keys or None)
    except ValueError as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    # Couches locales d'un zonage hors catalogue : examinées sous leur propre nom.
    items += [zoning.Zoning(k, k, None) for k in local if k not in zoning.BY_KEY]

    search = QgsRectangle(project.boundingBox())
    search.grow(float(search_distance_m))
    rows: list[list[Any]] = []
    checklist: dict[str, str] = {}
    pieces: list[tuple[str, str, QgsGeometry, float]] = []
    warnings: list[str] = []
    for item in items:
        try:
            sources = _sources(item, local, search, crs, max_features)
        except (ToolError, ValueError) as exc:
            checklist[item.label] = f"erreur : {exc}"
            rows.append([item.label, None, f"erreur : {exc}", None, None, None, None, None])
            continue
        if not sources:
            checklist[item.label] = "non vérifié : couche locale à fournir"
            rows.append([item.label, None, checklist[item.label], None, None, None, None,
                         None])
            continue
        found = []
        for source_features, source_crs, name_field, url_field in sources:
            to_project = QgsCoordinateTransform(source_crs, crs, QgsProject.instance())
            count = len(source_features)
            for feature in source_features:
                geometry = QgsGeometry(feature.geometry())
                if geometry.isEmpty():
                    continue
                geometry.transform(to_project)
                if not geometry.isGeosValid():
                    geometry = geometry.makeValid()
                piece = geometry.intersection(project)
                inter_m2 = area_m2(da, piece) if not piece.isEmpty() else 0.0
                distance = 0.0 if inter_m2 > 0 else geometry.distance(project)
                state = zoning.status(inter_m2, distance, float(search_distance_m))
                if state == "absent":
                    continue
                name = to_json_value(feature.attribute(name_field)) if name_field else None
                zone_m2 = area_m2(da, geometry)
                found.append([item.label, name, state, round(inter_m2 / 10_000, 4),
                              round(inter_m2 / project_m2 * 100, 2) if project_m2 else None,
                              round(inter_m2 / zone_m2 * 100, 2) if zone_m2 else None,
                              round(distance, 1),
                              to_json_value(feature.attribute(url_field)) if url_field
                              else None])
                if inter_m2 > 0:
                    pieces.append((item.label, str(name or ""), piece, inter_m2))
            if count >= max_features:
                warnings.append(f"{item.label} : plafond de {max_features} entités atteint, "
                                "résultat peut-être incomplet.")
        found.sort(key=lambda r: (r[2] != "intersecte", r[6], -(r[3] or 0)))
        rows += found or [[item.label, None, f"absent (rayon {search_distance_m:g} m)", None,
                           None, None, None, None]]
        hits = [r for r in found if r[2] == "intersecte"]
        if hits:
            checklist[item.label] = (f"intersecte : {sum(r[3] for r in hits):.4f} ha, "
                                     f"{sum(r[4] or 0 for r in hits):.2f} % du projet")
        elif found:
            checklist[item.label] = f"à proximité : {found[0][2]}"
        else:
            checklist[item.label] = f"absent dans un rayon de {search_distance_m:g} m"

    base = output_name or f"zonages_{layer.name()}"
    data: dict[str, Any] = {"territory": territory.code if territory else None,
                            "project_area_ha": round(project_m2 / 10_000, 4),
                            "search_distance_m": search_distance_m, "checklist": checklist,
                            "headers": HEADERS, "rows": rows}
    outputs: list[str] = []
    if export_format != "none":
        path, more = write_table(base, HEADERS, rows, export_format)
        data["table_path"] = str(path)
        outputs.append(str(path))
        warnings += more
    result = ToolResult(data, warnings, outputs)
    if create_layer and pieces:
        fields = QgsFields()
        for spec in (("zonage", "string", 80), ("zone", "string", 160),
                     ("surface_ha", "real", 0), ("part_proj", "real", 0)):
            fields.append(make_field(*spec))
        memory = QgsMemoryProviderUtils.createMemoryLayer("zonages", fields,
                                                          Qgis.WkbType.MultiPolygon, crs)
        features = []
        for label, name, piece, inter_m2 in pieces:
            polygon = piece.convertToType(Qgis.GeometryType.Polygon, True)
            if polygon is None or polygon.isEmpty():
                continue
            feature = QgsFeature(fields)
            feature.setGeometry(polygon)
            feature.setAttributes([label, name, round(inter_m2 / 10_000, 4),
                                   round(inter_m2 / project_m2 * 100, 2)])
            features.append(feature)
        notes = add_to_memory(memory, features)
        saved = save_to_project(memory, f"{base}_intersections")
        result.data["intersection_layer"] = saved.data["outputs"][0]
        result.outputs.extend(saved.outputs)
        result.warnings.extend(notes + [w for w in saved.warnings if w not in result.warnings])
    return result
