"""Rattachement de polygones d'habitat aux typologies locales de HABREF (INPN). Python pur.

HABREF_<NN>.csv (« ; », UTF-8 avec BOM) regroupe toutes les typologies : une ligne par
habitat avec CD_HAB, CD_TYPO (typologie), LB_CODE (code dans la typologie), LB_HAB_FR,
NIVEAU, PATH_CD_HAB (/parent/…/habitat) et FG_VALIDITE (NR nom de référence, SUPPR supprimé).
Un même LB_CODE peut exister en NR et en SUPPR : le nom de référence l'emporte.
"""
from __future__ import annotations

import difflib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .naming import normalize

DOWNLOAD = "https://inpn.mnhn.fr/telechargement/referentiels/habitats"
HABREF_FILE = r"habref_\d+.*\.(zip|csv)"   # HABREF_70.zip, HABREF_70.csv
HABREF_MEMBER = r"habref_\d+\.csv"
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
