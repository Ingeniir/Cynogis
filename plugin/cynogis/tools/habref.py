"""Rattachement des polygones d'habitat aux typologies locales de HABREF (INPN)."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from qgis.core import QgsFeature, QgsFields, QgsMemoryProviderUtils

from ..core import habref
from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.fields import unique_field_name
from ..core.referentials import DEFAULT_DIRECTORY
from ..core.registry import Level, tool
from ..core.schema import Param
from ..core.taxref import find_file, open_table
from ..core.territory import detect_territory
from .common import (
    add_to_memory,
    extent_wgs84,
    feature_request,
    geometry_kind,
    get_vector_layer,
    make_field,
    rect_to_list,
    require_field,
    to_json_value,
)
from .geoprocessing import OUTPUT_NAME
from .outputs import save_to_project

# Champs ajoutés (10 caractères max : compatibles Shapefile).
ADDED_FIELDS = (("hab_cd", "integer"), ("hab_code", "string"), ("hab_lib", "string"),
                ("hab_niv", "integer"), ("hab_n1", "string"), ("hab_valide", "integer"),
                ("hab_match", "string"))
CORINE_FIELDS = (("cb_code", "string"), ("cb_lib", "string"), ("cb_rel", "string"))


def _sibling(source: Path, pattern: str) -> Path:
    """Archive HABREF, ou fichier extrait du même dossier correspondant à pattern."""
    if source.suffix.lower() == ".zip":
        return source
    found = find_file(source.parent, pattern)
    if found is None:
        raise ValueError(f"{pattern} introuvable à côté de {source.name}.")
    return found


@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Polygones d'habitat (layer_id)."),
    "source_field": Param("string", "Champ du code ou du libellé d'habitat saisi."),
    "typology": Param("string", "Typologie HABREF. Défaut : reunion_cbnm à La Réunion, mayotte "
                      "à Mayotte (territoire détecté depuis l'emprise).", required=False,
                      enum=tuple(habref.TYPOLOGIES)),
    "mapping": Param("object", 'Valeur saisie → code de la typologie, pour les valeurs non '
                     'reconnues, ex. {"forêt de bois de couleurs": "4.1.2"}.', required=False),
    "habref_path": Param("string", "Fichier HABREF de l'INPN (HABREF_70.zip ou HABREF_70.csv). "
                         "Défaut : le plus récent de ~/.cynogis/referentials.", required=False),
    "output_name": OUTPUT_NAME,
})
def habitat_typology_join(layer_id: str, source_field: str, typology: str | None,
                          mapping: dict | None, habref_path: str | None,
                          output_name: str | None) -> ToolResult:
    """Copie des polygones d'habitat rattachée à une typologie locale de HABREF (CBNM /
    Mascarine pour La Réunion, référentiel des habitats de Mayotte) : hab_cd (CD_HAB),
    hab_code, hab_lib, hab_niv (niveau), hab_n1 (grand type), hab_valide (0 = code supprimé
    de la typologie), hab_match (code, libellé ou mapping). Typologie CBNM : correspondance
    CORINE biotopes de La Réunion publiée dans HABREF, cb_code, cb_lib (« ; » si plusieurs),
    cb_rel (=, <, non précisée… ; « via sous-unités » : codes des sous-unités d'un habitat
    général, à préciser). Valeurs non reconnues : laissées vides, avec des suggestions par
    ressemblance du libellé (unmatched) à faire valider par l'utilisateur, puis relancer avec
    mapping."""
    layer = get_vector_layer(layer_id)
    if geometry_kind(layer) != "polygon":
        raise ToolError(ErrorCode.INVALID_PARAMS, f"{layer.name()} n'est pas une couche de "
                        "polygones.")
    source_field = require_field(layer, source_field)
    if typology is None:
        territory = detect_territory(rect_to_list(extent_wgs84(layer)))
        if territory is None:
            raise ToolError(ErrorCode.INVALID_PARAMS, "Territoire non détecté : précise "
                            f"typology ({', '.join(habref.TYPOLOGIES)}).")
        typology = habref.DEFAULT_TYPOLOGY[territory.code]
    cd_typo, _, typology_label = habref.TYPOLOGIES[typology]
    if habref_path and not Path(habref_path).is_file():
        raise ToolError(ErrorCode.FILE_NOT_FOUND, f"Fichier introuvable : {habref_path}")
    source = Path(habref_path) if habref_path else find_file(DEFAULT_DIRECTORY,
                                                             habref.HABREF_FILE)
    if source is None:
        raise ToolError(ErrorCode.FILE_NOT_FOUND, "HABREF introuvable : télécharge l'archive sur "
                        f"{habref.DOWNLOAD} et place-la dans {DEFAULT_DIRECTORY} (ou indique "
                        "habref_path).")

    features = list(layer.getFeatures(feature_request(layer)))
    values = {str(v) for f in features if (v := to_json_value(f[source_field])) not in (None, "")}
    target = habref.CORRESPONDENCES.get(typology)
    links: dict = {}
    targets: dict = {}
    try:
        with open_table(source, habref.HABREF_MEMBER) as handle:
            rows = list(csv.reader(handle, delimiter=";"))
        habitats = habref.load_typology(rows, cd_typo)
        matched, unmatched = habref.match_habitats(values, habitats, mapping)
        if target:
            cd_target = habref.TYPOLOGIES[target][0]
            targets = {h.cd_hab: h for h in habref.load_typology(rows, cd_target)}
            corresp = _sibling(source, habref.CORRESP_MEMBER)
            with open_table(corresp, habref.CORRESP_MEMBER) as handle:
                links = habref.load_correspondences(csv.reader(handle, delimiter=";"),
                                                    cd_typo, cd_target)
    except (OSError, ValueError, csv.Error) as exc:
        raise ToolError(ErrorCode.INVALID_PARAMS, str(exc)) from exc
    if not habitats:
        raise ToolError(ErrorCode.INVALID_PARAMS, f"Typologie {typology} absente de "
                        f"{source.name}.")
    by_id = {h.cd_hab: h for h in habitats}

    fields = QgsFields(layer.fields())
    added = []
    for name, type_name in ADDED_FIELDS + (CORINE_FIELDS if target else ()):
        added.append(unique_field_name(name, fields.names()))
        fields.append(make_field(added[-1], type_name))
    memory = QgsMemoryProviderUtils.createMemoryLayer("habitats", fields, layer.wkbType(),
                                                      layer.crs())
    out = []
    no_corine: set[str] = set()
    for feature in features:
        value = to_json_value(feature[source_field])
        found = matched.get(str(value)) if value not in (None, "") else None
        extra = [None] * (len(added))
        if found:
            habitat, mode = found
            top = by_id.get(habitat.path[0]) if habitat.path else None
            extra = [habitat.cd_hab, habitat.code, habitat.label, habitat.level,
                     f"{top.code} {top.label}" if top else None, int(habitat.valid), mode]
            if target:
                cds, relation = habref.correspond(habitat, links, habitats)
                found_targets = [targets[c] for c in cds if c in targets]
                extra += ["; ".join(t.code for t in found_targets) or None,
                          "; ".join(t.label for t in found_targets) or None, relation]
                if not found_targets:
                    no_corine.add(habitat.code)
        copy = QgsFeature(fields)
        copy.setGeometry(feature.geometry())
        copy.setAttributes(feature.attributes() + extra)
        out.append(copy)
    notes = add_to_memory(memory, out)

    result = save_to_project(memory, output_name or f"{layer.name()}_habref")
    result.warnings.extend(notes)
    counts = Counter(to_json_value(f[source_field]) for f in features)
    suppressed = sorted(v for v, (h, _) in matched.items() if not h.valid)
    result.data.update({
        "typology": typology, "typology_label": typology_label, "habref": source.name,
        "fields": added, "values": len(values), "matched": len(matched),
        "by_mode": dict(Counter(mode for _, mode in matched.values())),
        "unmatched": {v: {"features": counts[v], "suggestions": s}
                      for v, s in sorted(unmatched.items(), key=lambda kv: -counts[kv[0]])[:30]},
    })
    if unmatched:
        result.warnings.append(f"{len(unmatched)} valeur(s) non rattachée(s) (champs vides) : "
                               "valider les suggestions avec l'utilisateur puis relancer avec "
                               "mapping.")
    if target:
        result.data["corine"] = habref.TYPOLOGIES[target][2]
        if no_corine:
            result.warnings.append(f"Sans correspondance CORINE dans HABREF : "
                                   f"{', '.join(sorted(no_corine)[:15])}.")
    if suppressed:
        result.warnings.append(f"Codes supprimés de la typologie (hab_valide = 0) : "
                               f"{', '.join(suppressed[:10])}.")
    return result
