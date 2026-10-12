"""Enrichissement des observations par TAXREF et les statuts de la BDC Statuts (INPN)."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from qgis.core import QgsFeature, QgsFields, QgsMemoryProviderUtils

from ..core import taxref
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.fields import unique_field_name
from ..core.referentials import DEFAULT_DIRECTORY
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.territory import detect_territory
from .common import (
    add_to_memory,
    extent_wgs84,
    feature_request,
    get_vector_layer,
    make_field,
    rect_to_list,
    require_field,
    to_json_value,
)
from .geoprocessing import OUTPUT_NAME
from .outputs import save_to_project

THREATENED = ("CR", "EN", "VU")
# Champs ajoutés (10 caractères max : compatibles Shapefile).
ADDED_FIELDS = (("cd_nom", "integer"), ("cd_ref", "integer"), ("nom_valide", "string"),
                ("nom_vern", "string"), ("match_tx", "string"), ("statut_bio", "string"),
                ("origine", "string"), ("lr_terr", "string"), ("lr_mond", "string"),
                ("prot_terr", "integer"), ("prot_nat", "integer"), ("protection", "string"),
                ("eee", "integer"), ("znieff", "integer"))


def _source(path: str | None, pattern: str) -> Path | None:
    if path:
        if not Path(path).is_file():
            raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Fichier introuvable : {path}")
        return Path(path)
    return taxref.find_file(DEFAULT_DIRECTORY, pattern)


def _values(taxon: taxref.Taxon | None, statuses: taxref.Statuses | None) -> list:
    if taxon is None:
        return [None] * len(ADDED_FIELDS)
    status = statuses or taxref.Statuses()
    origin = taxref.BIOGEO.get(taxon.statut_bio or "", (None, None))[1]
    citations = sorted(status.prot_terr) + [f"(national, à vérifier) {c}"
                                            for c in sorted(status.prot_nat)]
    return [taxon.cd_nom, taxon.cd_ref, taxon.nom_valide, taxon.nom_vern or None, taxon.match,
            taxon.statut_bio, origin, status.lr_terr, status.lr_mond, int(bool(status.prot_terr)),
            int(bool(status.prot_nat)), " | ".join(citations) or None,
            int(taxon.statut_bio == "J" or status.lutte), int(status.znieff)]


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche des observations (layer_id)."),
    "taxon_field": Param("string", "Champ du taxon : nom scientifique (avec ou sans auteur), "
                         "nom vernaculaire ou CD_NOM."),
    "territory": Param("string", "Territoire des statuts. Défaut : détecté depuis l'emprise.",
                       required=False, enum=tuple(taxref.TERRITORIES)),
    "taxref_path": Param("string", "Fichier TAXREF de l'INPN (TAXREF_v18_2025.zip ou "
                         "TAXREFv18.txt). Défaut : le plus récent de ~/.cynogis/referentials.",
                         required=False),
    "bdc_path": Param("string", "Fichier BDC Statuts de l'INPN (BDC-STATUTS-v18.zip ou "
                      "bdc_statuts_18.csv). Défaut : ~/.cynogis/referentials ; absent = sans "
                      "statuts de protection ni listes rouges.", required=False),
    "output_name": OUTPUT_NAME,
})
def taxon_status_join(layer_id: str, taxon_field: str, territory: str | None,
                      taxref_path: str | None, bdc_path: str | None,
                      output_name: str | None) -> ToolResult:
    """Copie des observations enrichie par TAXREF et la BDC Statuts : cd_nom, cd_ref,
    nom_valide, nom_vern, match_tx, statut_bio (code TAXREF du territoire) et origine
    (endémique, indigène, exotique, exotique envahissant…), lr_terr (liste rouge UICN du
    territoire), lr_mond (UICN mondiale), prot_terr (arrêtés de protection du territoire),
    prot_nat (protection nationale, applicabilité à vérifier), protection (textes), eee
    (introduit envahissant ou espèce en lutte), znieff (déterminante ZNIEFF). Vérifie
    unmatched et ambiguous dans la réponse avec l'utilisateur."""
    layer = get_vector_layer(layer_id)
    taxon_field = require_field(layer, taxon_field)
    if territory is None:
        found = detect_territory(rect_to_list(extent_wgs84(layer)))
        if found is None:
            raise ToolError(ErrorCode.INVALID_PARAMS, "Territoire non détecté : précise "
                            "territory (reunion ou mayotte).")
        territory = found.code
    taxref_file = _source(taxref_path, taxref.TAXREF_FILE)
    if taxref_file is None:
        raise ToolError(ErrorCode.FILE_NOT_FOUND, "TAXREF introuvable : télécharge l'archive "
                        f"sur {taxref.DOWNLOAD} et place-la dans {DEFAULT_DIRECTORY} (ou "
                        "indique taxref_path).")
    bdc_file = _source(bdc_path, taxref.BDC_FILE)

    features = list(layer.getFeatures(feature_request(layer)))
    names = {str(v) for f in features if (v := to_json_value(f[taxon_field])) not in (None, "")}
    try:
        with taxref.open_table(taxref_file, r"TAXREFv\d+\.txt") as handle:
            taxa, ambiguous = taxref.match_taxa(csv.reader(handle, delimiter="\t"), names,
                                                territory)
        statuses: dict[int, taxref.Statuses] = {}
        if bdc_file:
            with taxref.open_table(bdc_file, r"bdc_statuts_\d+\.csv") as handle:
                statuses = taxref.read_statuses(csv.reader(handle),
                                                {t.cd_ref for t in taxa.values()}, territory)
    except (OSError, ValueError, csv.Error) as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Lecture du référentiel impossible : {exc}"
                        ) from exc

    fields = QgsFields(layer.fields())
    added = []
    for name, type_name in ADDED_FIELDS:
        added.append(unique_field_name(name, fields.names()))
        fields.append(make_field(added[-1], type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("taxons", fields, layer.wkbType(),
                                                      layer.crs())
    out = []
    for feature in features:
        value = to_json_value(feature[taxon_field])
        taxon = taxa.get(str(value)) if value not in (None, "") else None
        copy = QgsFeature(fields)
        copy.setGeometry(feature.geometry())
        copy.setAttributes(feature.attributes()
                           + _values(taxon, statuses.get(taxon.cd_ref) if taxon else None))
        out.append(copy)
    notes = add_to_memory(memory, out)

    result = save_to_project(memory, output_name or f"{layer.name()}_taxref")
    result.warnings.extend(notes)
    by_ref = {t.cd_ref: t for t in taxa.values()}

    def listed(test) -> list[str]:
        return sorted({t.nom_valide for r, t in by_ref.items()
                       if test(t, statuses.get(r, taxref.Statuses()))})

    unmatched = sorted(names - set(taxa) - set(ambiguous))
    result.data.update({
        "territory": territory, "taxref": taxref_file.name,
        "bdc_statuts": bdc_file.name if bdc_file else None, "fields": added,
        "names": len(names), "matched": len(names) - len(unmatched) - len(ambiguous),
        "taxa": len(by_ref),
        "origin": dict(Counter(taxref.BIOGEO.get(t.statut_bio or "", (None, "inconnu"))[1]
                               for t in by_ref.values())),
        "protected": listed(lambda t, s: s.prot_terr),
        "threatened": listed(lambda t, s: s.lr_terr in THREATENED),
        "invasive": listed(lambda t, s: t.statut_bio == "J" or s.lutte),
        "unmatched": unmatched[:50], "ambiguous": dict(list(ambiguous.items())[:20]),
    })
    if not bdc_file:
        result.warnings.append("BDC Statuts absente : ni protection, ni liste rouge, ni ZNIEFF. "
                               f"Télécharge-la sur {taxref.DOWNLOAD}.")
    if unmatched:
        result.warnings.append(f"{len(unmatched)} nom(s) non trouvé(s) dans TAXREF (champs "
                               "vides) : vérifier l'orthographe.")
    if ambiguous:
        result.warnings.append(f"{len(ambiguous)} nom(s) ambigu(s) (plusieurs taxons) : "
                               "préciser le nom scientifique.")
    if any(s.prot_nat for s in statuses.values()):
        result.warnings.append("Protection nationale (prot_nat) : vérifier que l'arrêté "
                               "s'applique au territoire (certains ne visent que la métropole).")
    return result
