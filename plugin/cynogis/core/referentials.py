"""Référentiels d'occupation du sol et passage vers la nomenclature des paysages.

Sources : OCS GE de l'IGN (couverture CODE_CS et usage CODE_US) et cartes d'occupation du sol
du CIRAD (code de niveau 3, table propre à chaque territoire). Chaque valeur
est rattachée à un code fermé de core/landscape.py, jamais inventé. Python pur.

Lecture des règles OCS GE : une règle s'applique si son code de couverture est un préfixe du
code de l'entité (CS2.1.1 couvre CS2.1.1.1) et son usage aussi (None = tout usage). La règle la
plus précise sur l'usage l'emporte, puis la plus précise sur la couverture. Une règle avec une
note signale une correspondance à faire vérifier par un humain (l'OCS GE ne distingue pas, par
exemple, la canne d'une prairie : la carte du CIRAD le fait).
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .landscape import BY_CODE, classes_for, suggest_mapping
from .naming import normalize
from .stats import to_float

TERRITORIES = {"REU": "reunion", "MYT": "mayotte"}
# Fichiers des référentiels : <dossier>/<clé>.<extension>, ex. ocsge_974_2022.gpkg
DEFAULT_DIRECTORY = Path.home() / ".cynogis" / "referentials"
EXTENSIONS = (".gpkg", ".shp", ".geojson")
DOWNLOAD = {"ocsge": "https://geoservices.ign.fr/ocsge",
            "cirad": "https://geode.cirad.fr/geoserver/ows (WFS)"}
AGRICULTURAL_GROUP = "2"  # grand poste remplacé par une source prioritaire (overlay)


@dataclass(frozen=True)
class Source:
    key: str
    territory: str          # REU ou MYT
    kind: str               # ocsge ou cirad
    year: int
    code_fields: tuple[str, ...]
    layer_name: str | None = None   # couche à lire dans un GeoPackage multi-couches
    file_stems: tuple[str, ...] = ()  # noms de fichier d'origine acceptés en plus de la clé
    codes: Mapping[int, tuple[str | None, str]] | None = None  # code → (nomenclature, note)

    @property
    def landscape_territory(self) -> str:
        return TERRITORIES[self.territory]

    @property
    def url(self) -> str:
        return DOWNLOAD[self.kind]


# Cartes d'occupation du sol de La Réunion du CIRAD (2020, 2022, 2024 : même nomenclature,
# 29 classes de niveau 3). Correspondance par code et non par libellé (libellés du fichier
# parfois abîmés, ex. « Panneau photovolta?que »). Valeur : (code de nomenclature, note à
# vérifier ou "").
CIRAD_974_CODES: dict[int, tuple[str | None, str]] = {
    1: ("2.1.1", ""),                    # Canne à sucre
    3: ("2.3.1", ""),                    # Prairies pâturées
    4: ("2.3.1", ""),                    # Prairies fauchées
    5: ("2.1.2", ""),                    # Autres cultures maraîchères
    7: ("2.1.2", ""),                    # Ananas (maraîchage pour le CIRAD)
    8: ("2.1.2", "Culture sur treille (pitaya, passion, vigne) : verger (2.2.1) possible."),
    9: ("2.1.2", ""),                    # Culture sous serre ou sous ombrage
    10: ("2.2.1", ""),                   # Verger d'agrumes
    11: ("2.2.1", ""),                   # Verger de letchis et longanis
    12: ("2.2.1", ""),                   # Verger de manguiers
    13: ("2.2.1", ""),                   # Plantation de cocotiers
    14: ("2.2.1", ""),                   # Plantation de bananiers
    15: ("3.1.1", "Inclut tamarinaies (3.1.3) et fourrés de montagne (3.2.2)."),
    16: ("3.1.6", ""),                   # Autre végétation arborée
    17: ("3.1.5", ""),                   # Plantation forestière
    18: ("3.2.2", ""),                   # Végétation altimontaine (brande, avoune)
    19: ("3.2.2", "Lande de rempart : végétation arbustive (3.2.3) possible."),
    20: ("3.2.1", ""),                   # Savane herbacée de basse altitude
    21: ("3.2.3", ""),                   # Végétation arbustive
    22: ("3.2.4", ""),                   # Massif de vigne marronne (espèce envahissante)
    23: ("3.3.2", ""),                   # Végétation naturelle sur coulée de lave
    24: ("3.3.1", ""),                   # Rochers et sols peu végétalisés
    25: (None, "Ombre due au relief : occupation inconnue (compléter avec l'OCS GE)."),
    26: ("4.1.1", ""),                   # Marais
    27: ("5.1.2", "Surface en eau : peut inclure la mer côtière (5.2.2) ou des ravines "
                  "(5.1.1)."),
    28: ("1.1.1", "Tissu dense ou habitat diffus (1.1.2) selon la densité du quartier."),
    29: ("1.2.1", "Centrale photovoltaïque rattachée aux zones d'activité."),
    30: ("1.2.2", ""),                   # Route et parking
    200: ("3.2.3", "Friche agricole."),
}

# Carte d'occupation du sol de Mayotte 2023 du CIRAD (couche TETIS:mayotte_2023_final_map),
# champ Code3 (33 classes de niveau 3).
CIRAD_976_2023_CODES: dict[int, tuple[str | None, str]] = {
    1: ("4.2.2", "Zone intertidale ou tanne : sol nu (3.3.4) possible pour les tannes."),
    2: ("4.2.1", ""),                    # Mangroves externes
    3: ("4.2.1", ""),                    # Mangroves centrales et internes
    4: ("4.2.1", "Forêt d'arrière-mangrove : forêt naturelle (3.1.4) possible."),
    5: ("3.3.5", ""),                    # Plages
    6: ("5.1.2", "Eaux : lagon (5.2.1) si le champ Lagon vaut 1, ravine (5.1.1) possible."),
    7: ("3.3.1", "Falaises, rochers et sols nus non agricoles : sol nu (3.3.4) possible."),
    8: ("3.2.3", "Fourrés, broussailles et zones herbacées : savane (3.2.1) possible."),
    9: ("3.1.4", ""),                    # Forêts sèches
    10: ("3.1.4", ""),                   # Forêts mésophiles
    11: ("3.1.4", ""),                   # Forêts humides de moyenne altitude
    12: ("3.1.4", ""),                   # Forêts et végétation submontagnarde
    13: ("3.1.4", "Ripisylve ou forêt marécageuse : zone humide (4.1.1) possible."),
    14: ("3.1.4", "Forêt enlianée effondrée : espèces envahissantes (3.2.4) possible."),
    15: ("2.3.1", ""),                   # Pâturages
    16: ("2.1.3", ""),                   # Manioc dominant
    17: ("2.1.3", ""),                   # Ananas dominant
    18: ("2.1.3", ""),                   # Songe dominant
    19: ("2.1.3", "Cultures mélangées ou maraîchères : maraîchage (2.1.2) possible."),
    20: ("2.1.3", ""),                   # Bananeraies
    21: ("2.2.3", ""),                   # Ylang-ylang
    22: ("2.1.3", "Agroforêt (jardin mahorais) : cocoteraie = plantation pérenne (2.2.3)."),
    23: ("3.1.5", "Plantation d'Acacia mangium : espèce envahissante (3.2.4) possible."),
    24: ("3.1.5", ""),                   # Autres plantations forestières
    25: ("3.2.4", "Bambouseraie : forêt naturelle (3.1.4) possible."),
    26: ("3.3.3", ""),                   # Padzas nus
    27: ("3.3.3", "Padza végétalisé : végétation arbustive (3.2.3) ou savane (3.2.1) possible."),
    28: ("1.1.1", "Bâti et chantiers : habitat diffus (1.1.2) selon la densité."),
    29: ("1.2.1", "Centrale photovoltaïque rattachée aux zones d'activité."),
    30: ("2.1.2", ""),                   # Serres
    31: ("1.4.1", ""),                   # Végétation urbaine
    32: ("1.3.1", ""),                   # Carrières et décharges
    33: ("1.2.2", ""),                   # Routes et parkings
}

SOURCES = (
    Source("ocsge_974_2022", "REU", "ocsge", 2022, ("CODE_CS", "CODE_US"), "OCCUPATION_SOL"),
    Source("ocsge_974_2017", "REU", "ocsge", 2017, ("CODE_CS", "CODE_US"), "OCCUPATION_SOL"),
    Source("ocsge_976_2023", "MYT", "ocsge", 2023, ("CODE_CS", "CODE_US"), "OCCUPATION_SOL"),
    Source("ocsge_976_2020", "MYT", "ocsge", 2020, ("CODE_CS", "CODE_US"), "OCCUPATION_SOL"),
    # 2024 : couche AIDA:os2024_reunion du WFS du CIRAD, sans fiche de catalogue publiée.
    Source("cirad_974_2024", "REU", "cirad", 2024, ("niveau3",), codes=CIRAD_974_CODES),
    Source("cirad_974_2022", "REU", "cirad", 2022, ("code3",),
           file_stems=("OS_2022_Run_32740",), codes=CIRAD_974_CODES),
    Source("cirad_974_2020", "REU", "cirad", 2020, ("niveau3",),
           file_stems=("OS_SPOT_2020_32740",), codes=CIRAD_974_CODES),
    Source("cirad_976_2023", "MYT", "cirad", 2023, ("Code3",), codes=CIRAD_976_2023_CODES),
)
BY_KEY = {source.key: source for source in SOURCES}


def referentials_directory() -> Path:
    """Dossier des référentiels : CYNOGIS_REFERENTIALS_DIR, sinon ~/.cynogis/referentials."""
    return Path(os.environ.get("CYNOGIS_REFERENTIALS_DIR") or DEFAULT_DIRECTORY)


def find_source_file(source: Source, directory: Path | None = None) -> Path | None:
    """Premier fichier <clé>.gpkg / .shp / .geojson présent (casse ignorée), sinon None."""
    folder = directory or referentials_directory()
    if not folder.is_dir():
        return None
    by_name = {entry.name.lower(): entry for entry in folder.iterdir() if entry.is_file()}
    for stem in (source.key, *source.file_stems):
        for extension in EXTENSIONS:
            found = by_name.get(f"{stem}{extension}".lower())
            if found is not None:
                return found
    return None


def sources_for(territory: str | None) -> list[Source]:
    """Sources d'un territoire (reunion / mayotte), les plus récentes d'abord."""
    selected = [s for s in SOURCES if territory is None or s.landscape_territory == territory]
    return sorted(selected, key=lambda s: (s.kind, -s.year))


def is_agricultural(code: str | None) -> bool:
    """Vrai pour les classes du grand poste agricole, que la source prioritaire remplace."""
    item = BY_CODE.get(code or "")
    return item is not None and item.group == AGRICULTURAL_GROUP


@dataclass(frozen=True)
class Rule:
    """Correspondance OCS GE → code de nomenclature, par territoire."""

    cs: str                 # préfixe de couverture, ex. CS2.1.1
    us: str | None          # préfixe d'usage, ex. US1.1 ; None = tout usage
    reunion: str | None
    mayotte: str | None
    note: str = ""          # non vide = à vérifier par un humain

    def code_for(self, territory: str) -> str | None:
        return self.reunion if territory == "reunion" else self.mayotte


# Nomenclature OCS GE (IGN) — couverture :
#   CS1.1.1.1 bâti · CS1.1.1.2 imperméable non bâti · CS1.1.2.1 perméable minéral ·
#   CS1.1.2.2 perméable composite · CS1.2.1 sols nus · CS1.2.2 eau · CS1.2.3 névés ·
#   CS2.1.1.1 feuillus · CS2.1.1.2 conifères · CS2.1.1.3 mixte · CS2.1.2 arbustif ·
#   CS2.1.3 autres ligneux (vergers, vignes) · CS2.2.1 herbacé · CS2.2.2 autres non ligneux
# — usage :
#   US1.1 agriculture · US1.2 sylviculture · US1.3 extraction · US1.4 pêche, aquaculture ·
#   US1.5 autre primaire · US2 secondaire · US3 tertiaire · US235 mixte (2, 3 et 5) ·
#   US4.1.1 routier · US4.1.2 ferré · US4.1.3 aérien · US4.1.4 fluvial et maritime ·
#   US4.1.5 autres transports · US4.2 logistique · US4.3 réseaux d'utilité publique ·
#   US5 résidentiel · US6.1 en transition · US6.2 abandonné · US6.3 sans usage ·
#   US6.6 usage inconnu
OCSGE_RULES: tuple[Rule, ...] = (
    # --- Surfaces anthropisées -----------------------------------------------------------
    Rule("CS1.1.1.1", None, "1.1.1", "1.1.1",
         "Tissu dense ou habitat diffus (1.1.2) : la densité ne se lit pas sur une seule zone "
         "bâtie."),
    Rule("CS1.1", "US5", "1.1.1", "1.1.1",
         "Tissu dense ou habitat diffus (1.1.2) selon la densité du quartier."),
    Rule("CS1.1", "US235", "1.1.1", "1.1.1"),
    Rule("CS1.1", "US2", "1.2.1", "1.2.1"),
    Rule("CS1.1", "US3", "1.2.1", "1.2.1",
         "Équipement sportif ou de loisirs (1.4.2) possible."),
    Rule("CS1.1", "US4.2", "1.2.1", "1.2.1"),
    Rule("CS1.1", "US4.3", "1.2.1", "1.2.1"),
    Rule("CS1.1.1.2", None, "1.2.2", "1.2.2",
         "Places et parkings rattachés au réseau routier."),
    Rule("CS1.1", "US4.1.1", "1.2.2", "1.2.2"),
    Rule("CS1.1", "US4.1.2", "1.2.2", "1.2.2"),
    Rule("CS1.1", "US4.1.5", "1.2.2", "1.2.2"),
    Rule("CS1.1", "US4.1.3", "1.2.4", "1.2.4"),
    Rule("CS1.1", "US4.1.4", "1.2.4", "1.2.4"),
    Rule("CS1", "US1.3", "1.3.1", "1.3.1"),
    Rule("CS1.1.2", None, "3.3.4", "3.3.4",
         "Surface perméable artificialisée (stabilisé, chemin de terre, chantier)."),
    Rule("CS1.1", "US6.1", "3.3.4", "3.3.4", "Chantier ou zone en transition."),
    # --- Surfaces naturelles sans végétation ---------------------------------------------
    Rule("CS1.2.1", None, "3.3.4", "3.3.4",
         "Préciser : roche (3.3.1), coulée de lave (3.3.2, Réunion), padza (3.3.3, Mayotte) "
         "ou plage (3.3.5)."),
    Rule("CS1.2.2", None, "5.1.2", "5.1.2",
         "Préciser : ravine en eau (5.1.1), lagon (5.2.1, Mayotte) ou mer (5.2.2)."),
    Rule("CS1.2.2", "US1.4", "5.1.2", "5.1.2"),
    Rule("CS1.2.3", None, None, None, "Névés et glaciers : absents des deux îles."),
    # --- Végétation ligneuse -------------------------------------------------------------
    Rule("CS2.1.1", None, "3.1.6", "3.1.4",
         "Réunion : forêt de montagne (3.1.1), semi-sèche (3.1.2) ou tamarinaie (3.1.3) selon "
         "l'étage. Mayotte : mangrove (4.2.1) en bord de lagon."),
    Rule("CS2.1.1.2", None, "3.1.5", "3.1.5"),   # pas de conifère indigène : plantation
    Rule("CS2.1.1", "US1.2", "3.1.5", "3.1.5"),
    Rule("CS2.1.1", "US1.1", "2.2.1", "2.1.3",
         "Mayotte : jardin mahorais sous couvert arboré ; plantation (2.2.3) possible."),
    Rule("CS2.1.2", None, "3.2.3", "3.2.3",
         "Fourré et brande des hauts (3.2.2, Réunion) ou espèces envahissantes (3.2.4) "
         "possibles."),
    Rule("CS2.1.3", None, "2.2.1", "2.2.3",
         "Mayotte : verger (2.2.1) possible."),
    # --- Végétation non ligneuse ---------------------------------------------------------
    Rule("CS2.2.1", None, "3.2.1", "3.2.1", "Savane ou friche herbacée."),
    Rule("CS2.2.1", "US1.1", "2.4.1", "2.4.1",
         "Canne (2.1.1), prairie (2.3.1) ou maraîchage (2.1.2) : la carte du CIRAD tranche."),
    Rule("CS2.2.2", None, "4.1.1", "4.1.1", "Roselière ou zone humide à vérifier."),
    Rule("CS2.2.2", "US1.1", "2.4.1", "2.1.3",
         "Cultures non herbacées : la carte du CIRAD tranche (canne, maraîchage…)."),
    # --- Végétation selon l'usage --------------------------------------------------------
    Rule("CS2", "US5", "1.4.1", "1.4.1", "Jardins et espaces verts résidentiels."),
    Rule("CS2", "US3", "1.4.1", "1.4.1", "Équipement sportif (1.4.2) possible."),
    Rule("CS2", "US2", "1.4.1", "1.4.1"),
    Rule("CS2", "US4.1", "1.2.2", "1.2.2", "Accotements et dépendances vertes des routes."),
    Rule("CS2", "US6.2", "3.2.3", "3.2.3", "Friche."),
)

# Libellés usuels des cartes du CIRAD (normalisés : minuscules, sans accent).
# À vérifier sur le fichier livré ; les libellés absents passent par la recherche par
# mots-clés de la nomenclature, toujours marquée à vérifier.
CIRAD_LABELS: dict[str, tuple[str | None, str | None]] = {
    "canne a sucre": ("2.1.1", None),
    "canne": ("2.1.1", None),
    "paturage": ("2.3.1", "2.3.1"),
    "paturage et fourrage": ("2.3.1", "2.3.1"),
    "prairie": ("2.3.1", "2.3.1"),
    "culture maraichere": ("2.1.2", "2.1.2"),
    "maraichage": ("2.1.2", "2.1.2"),
    "culture sous serre": ("2.1.2", "2.1.2"),
    "serre": ("2.1.2", "2.1.2"),
    "verger": ("2.2.1", "2.2.1"),
    "culture vivriere": (None, "2.1.3"),
    "jardin mahorais": (None, "2.1.3"),
    "ylang": (None, "2.2.3"),
    "foret": ("3.1.6", "3.1.4"),
    "plantation forestiere": ("3.1.5", "3.1.5"),
    "savane": ("3.2.1", "3.2.1"),
    "vegetation herbacee": ("3.2.1", "3.2.1"),
    "vegetation arbustive": ("3.2.3", "3.2.3"),
    "fourre": ("3.2.3", "3.2.3"),
    "roche": ("3.3.1", "3.3.1"),
    "roche nue": ("3.3.1", "3.3.1"),
    "sol nu": ("3.3.4", "3.3.4"),
    "padza": (None, "3.3.3"),
    "mangrove": (None, "4.2.1"),
    "eau": ("5.1.2", "5.1.2"),
    "plan d eau": ("5.1.2", "5.1.2"),
    "bati": ("1.1.1", "1.1.1"),
    "zone urbaine": ("1.1.1", "1.1.1"),
    "route": ("1.2.2", "1.2.2"),
}
CIRAD_REVIEW = {"foret": "Forêt de montagne (3.1.1), semi-sèche (3.1.2) ou tamarinaie (3.1.3) "
                         "selon l'étage."}


def _segments(code: Any, prefix: str) -> list[str]:
    """« cs2.1.1 » ou « 2.1.1 » → ['CS2', '1', '1'] : comparaison par segments, pas par
    caractères (CS1.1 ne doit pas couvrir CS1.11)."""
    text = str(code).strip().upper().replace(" ", "")
    if text and text[0].isdigit():
        text = prefix + text
    return text.split(".")


def _covers(rule_code: str, code: Any, prefix: str) -> bool:
    expected = _segments(rule_code, prefix)
    return _segments(code, prefix)[:len(expected)] == expected


def map_ocsge(cs: Any, us: Any, territory: str) -> dict:
    """Code de nomenclature d'une entité OCS GE : {"code", "review", "note", "rule"}."""
    if not cs:
        return {"code": None, "review": True, "note": "Code de couverture absent.", "rule": None}
    candidates = [rule for rule in OCSGE_RULES if _covers(rule.cs, cs, "CS")
                  and (rule.us is None or (us and _covers(rule.us, us, "US")))]
    if not candidates:
        return {"code": None, "review": True,
                "note": f"Aucune règle pour {cs} / {us}.", "rule": None}
    rule = max(candidates, key=lambda r: (len(_segments(r.us, "US")) if r.us else 0,
                                          len(_segments(r.cs, "CS"))))
    code = rule.code_for(territory)
    return {"code": code, "review": bool(rule.note) or code is None, "note": rule.note,
            "rule": f"{rule.cs} / {rule.us or '*'}"}


def map_cirad(label: Any, territory: str,
              codes: Mapping[int, tuple[str | None, str]] | None = None) -> dict:
    """Code de nomenclature d'une classe CIRAD : table de codes de la source si elle en a
    une, sinon table de libellés, sinon mots-clés."""
    if codes is not None:
        number = to_float(label)
        if number is None or int(number) not in codes:
            return {"code": None, "review": True, "note": f"Code CIRAD inconnu : {label}.",
                    "rule": None}
        code, note = codes[int(number)]
        return {"code": code, "review": bool(note) or code is None, "note": note,
                "rule": f"code CIRAD {int(number)}"}
    text = normalize(str(label or ""))
    if text in CIRAD_LABELS:
        reunion, mayotte = CIRAD_LABELS[text]
        code = reunion if territory == "reunion" else mayotte
        note = CIRAD_REVIEW.get(text, "") if code else f"« {label} » n'existe pas à {territory}."
        return {"code": code, "review": bool(note), "note": note, "rule": "libellé CIRAD"}
    proposal = suggest_mapping([str(label or "")], territory)["mapping"].get(str(label or ""))
    if proposal is None:
        return {"code": None, "review": True, "note": f"Libellé inconnu : {label}.",
                "rule": None}
    return {"code": proposal["code"], "review": True,
            "note": f"Rattaché par mots-clés (confiance {proposal['confidence']}).",
            "rule": "mots-clés"}


def map_feature(source: Source, attributes: Mapping[str, Any]) -> dict:
    """Code de nomenclature d'une entité d'une source, à partir de ses attributs."""
    territory = source.landscape_territory
    if source.kind == "ocsge":
        cs_field, us_field = source.code_fields
        return map_ocsge(attributes.get(cs_field), attributes.get(us_field), territory)
    return map_cirad(attributes.get(source.code_fields[0]), territory, source.codes)


def check_rules() -> list[str]:
    """Incohérences des tables avec la nomenclature (codes inconnus ou hors territoire)."""
    problems = []
    allowed = {territory: {item.code for item in classes_for(territory)}
               for territory in TERRITORIES.values()}
    targets = [(f"OCS GE {r.cs}/{r.us}", t, r.code_for(t)) for r in OCSGE_RULES
               for t in allowed]
    targets += [(f"CIRAD « {label} »", t, codes[i]) for label, codes in CIRAD_LABELS.items()
                for i, t in enumerate(("reunion", "mayotte"))]
    targets += [(f"{source.key} code {number}", source.landscape_territory, code)
                for source in SOURCES if source.codes
                for number, (code, _) in source.codes.items()]
    for origin, territory, code in targets:
        if code is not None and (code not in BY_CODE or code not in allowed[territory]):
            problems.append(f"{origin} → {code} invalide à {territory}")
    return problems
