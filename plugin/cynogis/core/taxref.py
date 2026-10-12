"""Rattachement des noms de taxons à TAXREF et aux statuts de la BDC Statuts (INPN). Python pur.

Fichiers officiels de l'INPN, lus tels que téléchargés (zip ou extraits) :
- TAXREFv<NN>.txt (tabulation) : CD_NOM, CD_REF, LB_NOM, NOM_COMPLET, NOM_VALIDE, NOM_VERN,
  statut biogéographique par territoire (colonnes REU, MAY…) ;
- bdc_statuts_<NN>.csv (virgule) : un statut par ligne (CD_REF, CD_TYPE_STATUT, CODE_STATUT,
  CD_ISO3166_2…).

Dans la BDC, les statuts propres à un territoire portent son code ISO (FR-RE, FR-YT) : arrêtés
de protection (PD), liste rouge UICN du territoire (LRN), lutte contre les espèces (REGLLUTTE),
ZNIEFF (ZDET). Les statuts nationaux (PN) et la liste rouge mondiale (LRM) n'ont pas de code
ISO : une protection nationale peut ne viser que la métropole, elle est donc « à vérifier ».
"""
from __future__ import annotations

import io
import re
import zipfile
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from .naming import normalize

TERRITORIES = {"reunion": ("REU", "FR-RE"), "mayotte": ("MAY", "FR-YT")}
DOWNLOAD = "https://inpn.mnhn.fr/telechargement/referentielEspece/referentielTaxo"
# Statuts biogéographiques TAXREF (statuts_note.csv) : code → (libellé, origine).
BIOGEO = {
    "P": ("Présent (indigène ou indéterminé)", "indigène"),
    "E": ("Endémique", "endémique"),
    "S": ("Subendémique", "endémique"),
    "C": ("Cryptogène", "cryptogène"),
    "I": ("Introduit", "exotique"),
    "J": ("Introduit envahissant", "exotique envahissant"),
    "M": ("Introduit non établi", "exotique"),
    "B": ("Occasionnel", "occasionnel"),
    "D": ("Douteux", "douteux"),
    "G": ("ADNe uniquement", "douteux"),
    "Q": ("Mentionné par erreur", "absent"),
    "A": ("Absent", "absent"),
    "W": ("Disparu", "disparu"),
    "X": ("Éteint", "disparu"),
    "Z": ("Endémique éteint", "disparu"),
    "Y": ("Introduit éteint", "disparu"),
}
TERRITORY_PROTECTION = ("PD", "PR", "POM")


def name_key(text: str) -> str:
    """Forme comparable d'un nom (« Phelsuma  INEXPECTATA » → « phelsuma inexpectata »)."""
    return normalize(re.sub(r"<[^>]+>", "", str(text)))


@dataclass
class Taxon:
    cd_nom: int
    cd_ref: int
    nom_valide: str
    nom_vern: str
    match: str            # scientifique, vernaculaire, cd_nom
    statut_bio: str | None = None


@dataclass
class Statuses:
    lr_terr: str | None = None
    lr_mond: str | None = None
    prot_terr: set[str] = field(default_factory=set)
    prot_nat: set[str] = field(default_factory=set)
    lutte: bool = False
    znieff: bool = False


@contextmanager
def open_table(path: str | Path, pattern: str) -> Generator[io.TextIOBase]:
    """Fichier texte, ou membre d'une archive zip dont le nom correspond à pattern (regex)."""
    path = Path(path)
    if path.suffix.lower() != ".zip":
        with open(path, encoding="utf-8-sig", newline="") as handle:
            yield handle
        return
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if re.fullmatch(pattern, Path(n).name, re.I)]
        if not members:
            raise ValueError(f"{path.name} ne contient pas de fichier {pattern}.")
        with archive.open(members[0]) as raw:
            yield io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")


def _columns(header: list[str], wanted: Iterable[str], source: str) -> dict[str, int]:
    index = {name.strip().upper(): i for i, name in enumerate(header)}
    missing = [name for name in wanted if name not in index]
    if missing:
        raise ValueError(f"Colonnes absentes de {source} : {', '.join(missing)}.")
    return {name: index[name] for name in wanted}


def match_taxa(rows: Iterable[list[str]], names: Iterable[str],
               territory: str) -> tuple[dict[str, Taxon], dict[str, list[str]]]:
    """Rattache chaque nom (scientifique avec ou sans auteur, vernaculaire, ou CD_NOM) à
    TAXREF. Renvoie {nom: Taxon} et {nom: noms valides candidats} pour les noms ambigus.
    En cas d'homonymie, le taxon présent sur le territoire puis le nom valide l'emportent."""
    rows = iter(rows)
    terr_column = TERRITORIES[territory][0]
    col = _columns(next(rows), ("CD_NOM", "CD_REF", "LB_NOM", "NOM_COMPLET", "NOM_VALIDE",
                                "NOM_VERN", terr_column), "TAXREF")
    keys: dict[str, list[str]] = {}
    for name in names:
        text = str(name).strip()
        key = f"#{text}" if text.isdigit() else name_key(text)
        if key:
            keys.setdefault(key, []).append(name)
    candidates: dict[str, dict[int, tuple[int, str, str, str]]] = {}
    status: dict[int, str] = {}
    for row in rows:
        if len(row) <= max(col.values()):
            continue
        cd_nom, cd_ref = int(row[col["CD_NOM"]]), int(row[col["CD_REF"]])
        if cd_nom == cd_ref and row[col[terr_column]]:
            status[cd_ref] = row[col[terr_column]]
        hits: dict[str, str] = {}  # clé → type de correspondance, le plus sûr d'abord
        vernacular = row[col["NOM_VERN"]].split(",")
        for key, kind in ((f"#{cd_nom}", "cd_nom"),
                          (name_key(row[col["LB_NOM"]]), "scientifique"),
                          (name_key(row[col["NOM_COMPLET"]]), "scientifique"),
                          *((name_key(v), "vernaculaire") for v in vernacular)):
            hits.setdefault(key, kind)
        for key, kind in hits.items():
            if key in keys:
                found = candidates.setdefault(key, {})
                if cd_ref not in found or cd_nom == cd_ref:
                    found[cd_ref] = (cd_nom, row[col["NOM_VALIDE"]], row[col["NOM_VERN"]], kind)

    taxa: dict[str, Taxon] = {}
    ambiguous: dict[str, list[str]] = {}
    for key, found in candidates.items():
        present = {r: v for r, v in found.items()
                   if BIOGEO.get(status.get(r, "A"), ("", "absent"))[1] != "absent"}
        pool = present or found
        exact = {r: v for r, v in pool.items() if v[3] != "vernaculaire"} or pool
        if len(exact) > 1:
            for name in keys[key]:
                ambiguous[name] = sorted(v[1] for v in exact.values())
            continue
        cd_ref, (cd_nom, valide, vern, kind) = next(iter(exact.items()))
        for name in keys[key]:
            taxa[name] = Taxon(cd_nom, cd_ref, valide, vern, kind, status.get(cd_ref))
    return taxa, ambiguous


def read_statuses(rows: Iterable[list[str]], refs: set[int],
                  territory: str) -> dict[int, Statuses]:
    """Statuts utiles par CD_REF : ceux du territoire et les statuts nationaux / mondiaux."""
    rows = iter(rows)
    iso = TERRITORIES[territory][1]
    col = _columns(next(rows), ("CD_REF", "CD_TYPE_STATUT", "CODE_STATUT", "CD_ISO3166_2",
                                "FULL_CITATION"), "la BDC Statuts")
    found: dict[int, Statuses] = {}
    for row in rows:
        if len(row) <= max(col.values()) or not row[col["CD_REF"]].isdigit():
            continue
        cd_ref = int(row[col["CD_REF"]])
        if cd_ref not in refs:
            continue
        kind, code = row[col["CD_TYPE_STATUT"]], row[col["CODE_STATUT"]]
        local = row[col["CD_ISO3166_2"]] == iso
        citation = re.sub(r"<[^>]+>", "", row[col["FULL_CITATION"]]).strip()[:200]
        item = found.setdefault(cd_ref, Statuses())
        if local and kind == "LRN":
            item.lr_terr = code
        elif kind == "LRM":
            item.lr_mond = code
        elif local and kind in TERRITORY_PROTECTION:
            item.prot_terr.add(citation)
        elif kind == "PN" and not row[col["CD_ISO3166_2"]]:
            item.prot_nat.add(citation)
        elif local and kind == "REGLLUTTE":
            item.lutte = True
        elif local and kind == "ZDET":
            item.znieff = True
    return found


TAXREF_FILE = r"taxref_?v\d+.*\.(zip|txt)"   # TAXREF_v18_2025.zip, TAXREFv18.txt
BDC_FILE = r"bdc[-_]statuts[-_]v?\d+.*\.(zip|csv)"  # BDC-STATUTS-v18.zip, bdc_statuts_18.csv


def find_file(directory: Path, pattern: str) -> Path | None:
    """Fichier du dossier dont le nom correspond à pattern ; le plus récent (nom le plus
    grand) s'il y en a plusieurs."""
    if not directory.is_dir():
        return None
    found = sorted(p for p in directory.iterdir() if re.fullmatch(pattern, p.name, re.I))
    return found[-1] if found else None
