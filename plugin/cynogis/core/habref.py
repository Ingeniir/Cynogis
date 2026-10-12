"""Rattachement de polygones d'habitat aux typologies locales de HABREF (INPN). Python pur.

HABREF_<NN>.csv (« ; », UTF-8 avec BOM) regroupe toutes les typologies : une ligne par
habitat avec CD_HAB, CD_TYPO (typologie), LB_CODE (code dans la typologie), LB_HAB_FR,
NIVEAU, PATH_CD_HAB (/parent/…/habitat) et FG_VALIDITE (NR nom de référence, SUPPR supprimé).
Un même LB_CODE peut exister en NR et en SUPPR : le nom de référence l'emporte.

HABREF_CORRESP_HAB_<NN>.csv relie les habitats de deux typologies (CD_HAB_ENTRE →
CD_HAB_SORTIE, CD_TYPE_RELATION). Typologie CBNM → CORINE biotopes de La Réunion : seul le
niveau 4 est relié ; un habitat plus général reçoit les codes de ses sous-unités.
"""
from __future__ import annotations

import difflib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .naming import normalize

DOWNLOAD = "https://inpn.mnhn.fr/telechargement/referentiels/habitats"
HABREF_FILE = r"habref_\d+.*\.(zip|csv)"   # HABREF_70.zip, HABREF_70.csv
HABREF_MEMBER = r"habref_\d+\.csv"
CORRESP_MEMBER = r"habref_corresp_hab_\d+\.csv"
# Typologies locales de HABREF : clé → (CD_TYPO, territoire, intitulé).
TYPOLOGIES = {
    "reunion_cbnm": ("78", "reunion", "Habitats naturels et semi-naturels de La Réunion "
                     "(CBNM, 2021)"),
    "reunion_corine": ("72", "reunion", "Habitats CORINE biotopes de La Réunion (2000, "
                       "rév. 2010)"),
    "mayotte": ("88", "mayotte", "Habitats de Mayotte (Boullet, 2017)"),
    "mayotte_mer": ("94", "mayotte", "Habitats marins de Mayotte (2019)"),
}
DEFAULT_TYPOLOGY = {"reunion": "reunion_cbnm", "mayotte": "mayotte"}
# Correspondances publiées dans HABREF : typologie → typologie cible.
CORRESPONDENCES = {"reunion_cbnm": "reunion_corine"}
# Types de relation entre habitats (HABREF_TYPE_REL) ; vide = non précisée.
RELATIONS = {"": "non précisée", "1": "=", "2": "<", "3": ">", "4": "?", "5": "#", "6": "(#)",
             "24": "pas de correspondance", "50": "(=)", "51": "(<)", "52": "(>)", "53": "(#)"}
VIA_CHILDREN = "via sous-unités"
FUZZY_CUTOFF = 0.75


@dataclass(frozen=True)
class Habitat:
    cd_hab: int
    code: str
    label: str
    level: int | None
    path: tuple[int, ...]
    valid: bool

    def to_dict(self) -> dict:
        return {"cd_hab": self.cd_hab, "code": self.code, "label": self.label,
                "level": self.level, "valid": self.valid}


def load_typology(rows: Iterable[list[str]], cd_typo: str) -> list[Habitat]:
    """Habitats d'une typologie (lignes de HABREF_<NN>.csv, en-tête compris)."""
    rows = iter(rows)
    header = [name.lstrip("﻿").strip().upper() for name in next(rows)]
    wanted = ("CD_HAB", "CD_TYPO", "LB_CODE", "LB_HAB_FR", "NIVEAU", "PATH_CD_HAB",
              "FG_VALIDITE")
    missing = [name for name in wanted if name not in header]
    if missing:
        raise ValueError(f"Colonnes absentes de HABREF : {', '.join(missing)}.")
    col = {name: header.index(name) for name in wanted}
    habitats = []
    for row in rows:
        if len(row) <= max(col.values()) or row[col["CD_TYPO"]] != cd_typo:
            continue
        level = row[col["NIVEAU"]]
        habitats.append(Habitat(
            int(row[col["CD_HAB"]]), row[col["LB_CODE"]].strip(), row[col["LB_HAB_FR"]].strip(),
            int(level) if level.isdigit() else None,
            tuple(int(p) for p in row[col["PATH_CD_HAB"]].split("/") if p.isdigit()),
            row[col["FG_VALIDITE"]] != "SUPPR"))
    return habitats


def _index(habitats: Iterable[Habitat], key) -> dict[str, Habitat]:
    """Clé → habitat ; le nom de référence l'emporte sur un code supprimé."""
    index: dict[str, Habitat] = {}
    for item in habitats:
        found = index.get(key(item))
        if found is None or (item.valid and not found.valid):
            index[key(item)] = item
    return index


def match_habitats(values: Iterable[str], habitats: list[Habitat],
                   mapping: Mapping[str, str] | None = None
                   ) -> tuple[dict[str, tuple[Habitat, str]], dict[str, list[dict]]]:
    """Rattache chaque valeur (code ou libellé) à un habitat de la typologie.

    Ordre : mapping (valeur → code), code exact, libellé exact (sans casse ni accents).
    Renvoie {valeur: (habitat, mode)} et, pour les autres, {valeur: suggestions} par
    ressemblance du libellé (à faire valider, jamais appliquées)."""
    by_code = _index(habitats, lambda h: normalize(h.code))
    by_label = _index(habitats, lambda h: normalize(h.label))
    labels = list(by_label)
    mapping = {str(k): str(v) for k, v in (mapping or {}).items()}
    matched: dict[str, tuple[Habitat, str]] = {}
    unmatched: dict[str, list[dict]] = {}
    for value in values:
        text = str(value)
        key = normalize(text)
        if text in mapping:
            target = by_code.get(normalize(mapping[text]))
            if target is None:
                raise ValueError(f"mapping : code {mapping[text]!r} absent de la typologie.")
            matched[text] = (target, "mapping")
        elif key in by_code:
            matched[text] = (by_code[key], "code")
        elif key in by_label:
            matched[text] = (by_label[key], "libellé")
        else:
            close = difflib.get_close_matches(key, labels, n=3, cutoff=FUZZY_CUTOFF)
            unmatched[text] = [by_label[c].to_dict() for c in close]
    return matched, unmatched


def load_correspondences(rows: Iterable[list[str]], cd_typo_in: str,
                         cd_typo_out: str) -> dict[int, list[tuple[int, str]]]:
    """CD_HAB d'entrée → [(CD_HAB de sortie, relation)] (lignes de HABREF_CORRESP_HAB)."""
    rows = iter(rows)
    header = [name.lstrip("\ufeff").strip().upper() for name in next(rows)]
    wanted = ("CD_HAB_ENTRE", "CD_HAB_SORTIE", "CD_TYPE_RELATION", "VALIDITE",
              "CD_TYPO_ENTRE", "CD_TYPO_SORTIE")
    missing = [name for name in wanted if name not in header]
    if missing:
        raise ValueError(f"Colonnes absentes des correspondances HABREF : {', '.join(missing)}.")
    col = {name: header.index(name) for name in wanted}
    links: dict[int, list[tuple[int, str]]] = {}
    for row in rows:
        if (len(row) <= max(col.values()) or row[col["CD_TYPO_ENTRE"]] != cd_typo_in
                or row[col["CD_TYPO_SORTIE"]] != cd_typo_out
                or row[col["VALIDITE"]].lower() == "false"):
            continue
        relation = RELATIONS.get(row[col["CD_TYPE_RELATION"]], row[col["CD_TYPE_RELATION"]])
        links.setdefault(int(row[col["CD_HAB_ENTRE"]]), []).append(
            (int(row[col["CD_HAB_SORTIE"]]), relation))
    return links


def correspond(habitat: Habitat, links: Mapping[int, list[tuple[int, str]]],
               habitats: Iterable[Habitat]) -> tuple[list[int], str | None]:
    """Habitats cibles d'un habitat et relation ; à défaut de lien direct, ceux de ses
    sous-unités (relation VIA_CHILDREN, à préciser sur le terrain)."""
    if habitat.cd_hab in links:
        targets = list(dict.fromkeys(t for t, _ in links[habitat.cd_hab]))
        relations = sorted({r for _, r in links[habitat.cd_hab]})
        return targets, ", ".join(relations)
    targets = list(dict.fromkeys(t for h in habitats
                                 if habitat.cd_hab in h.path[:-1] and h.cd_hab in links
                                 for t, _ in links[h.cd_hab]))
    return (targets, VIA_CHILDREN) if targets else ([], None)
