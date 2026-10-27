"""Zonages réglementaires et d'inventaire de La Réunion et de Mayotte. Python pur.

Sources nationales (WFS de la Géoplateforme IGN, service geopf_wfs) : espaces protégés et
inventaires de l'INPN (couches patrinat_*), forêts publiques de l'ONF, prescriptions des PLU
du Géoportail de l'urbanisme (EBC : typepsc 01). Les noms techniques et les champs ont été
vérifiés sur le service (Parc national de La Réunion : champ zone = Cœur / Adhesion).

Certains zonages n'ont pas de flux national (ENS, SAR / SMVM, espaces de la Loi Littoral,
inventaire des zones humides de la DEAL) : ils doivent être fournis en couches locales,
sinon ils sont signalés « non vérifiés » plutôt que passés sous silence.

Chaque zonage porte une catégorie juridique et une implication *probable* pour un projet
(pré-diagnostic, regulatory_prescan) : indicatives, le texte et le service instructeur priment.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

from .referentials import referentials_directory
from .territory import NATURA2000_MESSAGE, is_natura2000_layer

BOTH = ("reunion", "mayotte")

# Catégories, de la plus contraignante à la moins contraignante.
CATEGORIES = {
    "protection_forte": "Protection forte",
    "urbanisme": "Document d'urbanisme / planification",
    "protection_contractuelle": "Protection contractuelle / gestion",
    "foncier": "Maîtrise foncière",
    "inventaire": "Inventaire patrimonial",
}
DISCLAIMER = ("Pré-diagnostic automatique : implications probables, à confirmer par la lecture "
              "des textes et l'avis des services instructeurs.")


@dataclass(frozen=True)
class Zoning:
    key: str
    label: str
    typename: str | None          # couche WFS geopf_wfs ; None = couche locale à fournir
    name_field: str | None = None
    filter: str | None = None     # expression QGIS, évaluée en local (sécurité)
    cql_filter: str | None = None # filtre ECQL envoyé au serveur (prioritaire, moins de volume)
    url_field: str | None = None
    sort_by: str | None = None    # champ unique : ordre stable entre les pages (SORTBY)
    territories: tuple[str, ...] = BOTH
    note: str = ""
    category: str = "inventaire"  # clé de CATEGORIES
    implication: str = ""         # au conditionnel, à confirmer
    service: str = "geopf_wfs"    # clé du catalogue
    near_m: int = 1000            # en deçà : "proche" ; au-delà : "dans le rayon"

    def to_dict(self) -> dict:
        return {"key": self.key, "label": self.label,
                "source": self.typename or "couche locale à fournir",
                "territories": list(self.territories), "note": self.note,
                "category": self.category}


def _inpn(key: str, label: str, typename: str, **options) -> Zoning:
    """Couche patrinat_* de l'INPN : nom dans nom_site, fiche dans url_fiche, identifiant
    unique id_mnhn (id_local ne l'est pas)."""
    return Zoning(key, label, typename, name_field="nom_site", url_field="url_fiche",
                  sort_by="id_mnhn", **options)


_ZNIEFF1 = ("Pas de portée réglementaire directe, mais présomption d'enjeu fort : inventaires "
            "de terrain et justification renforcée probablement attendus.")
_ZNIEFF2 = "Présomption d'enjeu, à prendre en compte dans l'état initial."

ZONINGS: tuple[Zoning, ...] = (
    _inpn("pn_coeur", "Cœur du Parc national", "patrinat_pn:parc_national",
          filter="\"zone\" = 'Cœur'", cql_filter="zone='Cœur'", near_m=2000,
          territories=("reunion",), category="protection_forte",
          implication="Travaux soumis à autorisation du Parc (décret n° 2007-296 du 5 mars "
                      "2007) ; refus probable pour un aménagement neuf."),
    _inpn("pn_adhesion", "Aire d'adhésion du Parc national", "patrinat_pn:parc_national",
          filter="\"zone\" = 'Adhesion'", cql_filter="zone='Adhesion'", territories=("reunion",),
          category="protection_contractuelle",
          implication="Compatibilité avec la charte à démontrer ; avis du Parc probable."),
    _inpn("rnn", "Réserve naturelle nationale", "patrinat_rnn:rnn",
          note="Réunion : Étang de Saint-Paul, Réserve marine ; Mayotte : îlot M'Bouzi, "
               "forêts de Mayotte.", category="protection_forte",
          implication="Réglementation propre à la réserve : travaux en principe interdits ou "
                      "soumis à autorisation spéciale."),
    _inpn("pnm", "Parc naturel marin", "patrinat_pnm:pnm", territories=("mayotte",),
          category="protection_contractuelle",
          implication="Avis conforme du conseil de gestion probable si effet notable sur le "
                      "milieu marin (rejets, bassin versant) ; décret n° 2010-71."),
    _inpn("apb", "Arrêté de protection de biotope (APB)", "patrinat_apb:apb",
          category="protection_forte",
          implication="Interdictions fixées par l'arrêté préfectoral, à lire au cas par cas."),
    _inpn("cdl", "Site du Conservatoire du littoral", "patrinat_cdl:conservatoire_littoral",
          category="foncier",
          implication="Foncier inaliénable : aucun aménagement sans convention avec le CdL."),
    _inpn("ramsar", "Site Ramsar (zone humide d'importance internationale)",
          "patrinat_ramsar:ramsar", category="protection_contractuelle",
          implication="Engagement international : vigilance sur les zones humides et leur "
                      "fonctionnalité."),
    _inpn("znieff1", "ZNIEFF de type I", "patrinat_znieff1:znieff1", implication=_ZNIEFF1),
    _inpn("znieff2", "ZNIEFF de type II", "patrinat_znieff2:znieff2", implication=_ZNIEFF2),
    _inpn("znieff1_mer", "ZNIEFF marine de type I", "patrinat_znieff1_mer:znieff1_mer",
          implication=_ZNIEFF1),
    _inpn("znieff2_mer", "ZNIEFF marine de type II", "patrinat_znieff2_mer:znieff2_mer",
          implication=_ZNIEFF2),
    Zoning("foret_publique", "Forêt publique (ONF)", "ONF.FORETS_PUBLIQUES:ONF_FORETS_PUBLIQUES",
           name_field="llib_frt", sort_by="iidtn_frt", note="Domaniale si cdom_frt = OUI.",
           category="foncier",
           implication="Régime forestier : accord de l'ONF probable ; distraction du régime "
                       "forestier si emprise définitive."),
    Zoning("ebc", "Espace boisé classé (PLU)", "wfs_du:prescription_surf",
           name_field="libelle", filter="\"typepsc\" = '01'", cql_filter="typepsc='01'",
           sort_by="gid", near_m=0,
           note="Géoportail de l'urbanisme : PLU publiés seulement.", category="urbanisme",
           implication="Changement d'affectation du sol interdit, défrichement impossible "
                       "sans révision du PLU."),
    Zoning("ens", "Espace naturel sensible (ENS)", None,
           note="Département : couche locale à fournir.", category="foncier",
           implication="Droit de préemption du Département ; aménagement limité à "
                       "l'ouverture au public."),
    Zoning("sar_smvm", "SAR / SMVM (espaces naturels, coupures d'urbanisation…)", None,
           note="Région / DEAL : couche locale à fournir.", category="urbanisme",
           implication="Compatibilité avec le SAR / SMVM à vérifier (espaces protégés, "
                       "coupures d'urbanisation)."),
    Zoning("loi_littoral", "Loi Littoral (espaces remarquables, bande des 50 pas…)", None,
           note="Couche locale à fournir (SAR-SMVM, DEAL).", category="urbanisme",
           implication="Espaces remarquables : seuls des aménagements légers sont admis."),
    Zoning("zones_humides", "Zones humides (inventaire)", None,
           note="Inventaire DEAL / département : couche locale à fournir ; Ramsar vérifié "
                "à part.",
           implication="Rubrique 3.3.1.0 de la loi sur l'eau probable si assèchement ou "
                       "remblai ; séquence ERC."),
)
BY_KEY = {item.key: item for item in ZONINGS}


def for_territory(territory: str | None, keys: list[str] | None = None) -> list[Zoning]:
    """Zonages à examiner : ceux demandés (keys), sinon tous ceux du territoire."""
    if keys:
        if any(is_natura2000_layer(k) for k in keys):
            raise ValueError(NATURA2000_MESSAGE)
        unknown = [k for k in keys if k not in BY_KEY]
        if unknown:
            raise ValueError(f"Zonages inconnus : {', '.join(unknown)} "
                             f"(connus : {', '.join(BY_KEY)}).")
        return [BY_KEY[k] for k in keys]
    return [z for z in ZONINGS if territory is None or territory in z.territories]


def status(intersect_m2: float, distance_m: float | None, search_m: float) -> str:
    """Statut d'une zone vis-à-vis du projet."""
    if intersect_m2 > 0:
        return "intersecte"
    if distance_m is not None and distance_m <= search_m:
        return f"à {distance_m:,.0f} m".replace(",", " ")
    return "absent"


def getfeature_url(base_url: str, typename: str, bbox_wgs84: tuple[float, float, float, float],
                   count: int, start_index: int = 0, cql_filter: str | None = None,
                   sort_by: str | None = None) -> str:
    """Requête WFS 2.0 GetFeature en GeoJSON limitée à une emprise (ouest, sud, est, nord) :
    une seule requête HTTP, bien plus rapide que l'ouverture d'une couche WFS par QGIS.
    BBOX en urn EPSG:4326 : ordre latitude, longitude ; le GeoJSON renvoyé est en
    longitude, latitude. start_index > 0 : page suivante (STARTINDEX); cql_filter : filtre
    ECQL appliqué par le serveur (GeoServer), en plus du filtre local éventuel ; sort_by :
    champ unique, sans lequel l'ordre (donc les pages) n'est pas garanti."""
    west, south, east, north = bbox_wgs84
    params = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
              "TYPENAMES": typename, "OUTPUTFORMAT": "application/json", "COUNT": str(count),
              "SRSNAME": "urn:ogc:def:crs:EPSG::4326",
              "BBOX": f"{south},{west},{north},{east},urn:ogc:def:crs:EPSG::4326"}
    if start_index > 0:
        params["STARTINDEX"] = str(start_index)
    if cql_filter:
        params["CQL_FILTER"] = cql_filter
    if sort_by:
        params["SORTBY"] = f"{sort_by} ASC"
    separator = "&" if "?" in base_url else "?"
    return base_url + separator + urlencode(params)

# --- Provenance et cache local ----------------------------------------------------------
CACHE_MAX_AGE_DAYS = 180
CACHE_SUBDIR = "zonages"
SERVICE_LABELS = {"geopf_wfs": "Géoplateforme IGN"}
PROVENANCE_KINDS = ("flux", "cache", "locale", "aucune", "erreur")
_UNUSED_KINDS = ("aucune", "erreur")


@dataclass(frozen=True)
class Provenance:
    """Origine des données examinées pour un zonage (une par source)."""
    kind: str                 # flux, cache, locale, aucune, erreur
    origin: str               # texte lisible repris dans la note
    dated: str = ""           # date ISO de la donnée ; "" si inconnue
    truncated: bool = False   # plafond d'entités atteint : donnée incomplète

    def __post_init__(self) -> None:
        if self.kind not in PROVENANCE_KINDS:
            raise ValueError(f"Provenance inconnue : {self.kind}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Provenance:
        return cls(str(data["kind"]), str(data["origin"]), str(data.get("dated") or ""),
                   bool(data.get("truncated", False)))


def service_label(service: str) -> str:
    return SERVICE_LABELS.get(service, service)


def provenance_from_data(sources: dict[str, list[dict]]) -> dict[str, list[Provenance]]:
    """Reconstruit les provenances depuis data["sources"] (JSON de regulatory_zoning_intersect)."""
    return {key: [Provenance.from_dict(p) for p in items] for key, items in sources.items()}


def age_days(dated: str, today: date) -> int | None:
    """Âge en jours d'une date ISO ; None si absente ou illisible ; jamais négatif."""
    try:
        return max(0, (today - date.fromisoformat(dated[:10])).days)
    except (TypeError, ValueError):
        return None


def freshness(p: Provenance, today: date, max_age: int = CACHE_MAX_AGE_DAYS) -> str:
    """Fraîcheur lisible d'une source pour le tableau « Sources et dates »."""
    if p.kind in _UNUSED_KINDS:
        return "—"
    age = age_days(p.dated, today)
    if age is None:
        text = "date inconnue"
    elif age == 0:
        text = "du jour"
    elif age > max_age:
        text = f"à rafraîchir ({age} j)"
    else:
        text = f"{age} j"
    return text + (" ; incomplète (plafond atteint)" if p.truncated else "")


def describe_sources(provs: list[Provenance], today: date) -> list[str]:
    """[origine, date, fraîcheur] d'un zonage, sources multiples séparées par « ; »."""
    if not provs:
        return ["non examiné", "", "—"]
    return [" ; ".join(p.origin for p in provs),
            " ; ".join(p.dated or "inconnue" for p in provs if p.kind not in _UNUSED_KINDS),
            " ; ".join(freshness(p, today) for p in provs)]


def cache_root() -> Path:
    """Dossier du cache des zonages : <référentiels>/zonages."""
    return referentials_directory() / CACHE_SUBDIR


def cache_paths(root: Path, territory: str, key: str) -> tuple[Path, Path]:
    """(GeoPackage, métadonnées JSON) du cache d'un zonage."""
    folder = root / territory
    return folder / f"{key}.gpkg", folder / f"{key}.json"


def cache_meta(item: Zoning, fetched_on: str, bbox_wgs84, crs: str, count: int,
               truncated: bool) -> dict:
    return {"key": item.key, "label": item.label, "service": item.service,
            "typename": item.typename, "filter": item.filter, "cql_filter": item.cql_filter,
            "fetched_on": fetched_on, "bbox_wgs84": [round(v, 6) for v in bbox_wgs84],
            "crs": crs, "features": count, "truncated": truncated}


def read_cache_meta(path: Path) -> dict | None:
    """Métadonnées du cache ; None si absentes, illisibles ou incomplètes."""
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (not isinstance(meta, dict) or not {"fetched_on", "bbox_wgs84", "features"} <= meta.keys()
            or len(meta["bbox_wgs84"]) != 4):
        return None
    return meta


def cache_matches(meta: dict, item: Zoning) -> bool:
    """Le cache a-t-il été produit avec la même couche et les mêmes filtres que le
    catalogue actuel ? Sinon il est périmé, quelle que soit sa date."""
    return (meta.get("typename") == item.typename and meta.get("filter") == item.filter
            and meta.get("cql_filter") == item.cql_filter)


def bbox_covers(outer, inner, tol: float = 1e-6) -> bool:
    """outer (ouest, sud, est, nord) contient-il inner ?"""
    return (outer[0] <= inner[0] + tol and outer[1] <= inner[1] + tol
            and outer[2] >= inner[2] - tol and outer[3] >= inner[3] - tol)


def should_replace_cache(old: dict | None, new_bbox) -> bool:
    """Un cache n'est remplacé que par une emprise au moins aussi grande : la copie de
    l'île entière n'est jamais écrasée par celle d'un projet."""
    return old is None or bbox_covers(new_bbox, old["bbox_wgs84"])


# --- Pré-diagnostic ---------------------------------------------------------------------
LEVELS = ("faible", "modéré", "fort", "majeur")
DETAIL_ROWS = 500  # sous core/report.py::MAX_ROWS ; au-delà, voir le tableau exporté
_STATE_ORDER = {"intersecte": 0, "proche": 1, "non vérifié": 2, "absent": 3}


def zoning_state(rows: list[list], label: str) -> str:
    """Bilan d'un zonage d'après les lignes de regulatory_zoning_intersect (colonne 0 :
    zonage, colonne 2 : statut) : intersecte, proche, absent ou non vérifié."""
    states = [str(r[2]) for r in rows if r[0] == label]
    if "intersecte" in states:
        return "intersecte"
    if any(s.startswith("à ") for s in states):
        return "proche"
    if any(s.startswith("absent") for s in states):
        return "absent"
    return "non vérifié"


def assess(items: list[Zoning], rows: list[list]) -> dict:
    """Synthèse : niveau de contrainte indicatif et bilan par zonage. Un zonage non vérifié
    ne fait pas baisser le niveau : il est listé à part."""
    states = {z.key: zoning_state(rows, z.label) for z in items}
    hit = [z for z in items if states[z.key] == "intersecte"]
    if any(z.category == "protection_forte" for z in hit):
        level = "majeur"
    elif hit:
        level = "fort"
    elif "proche" in states.values():
        level = "modéré"
    else:
        level = "faible"
    return {"level": level, "states": states,
            "strong_hits": [z.label for z in hit if z.category == "protection_forte"],
            "unchecked": [z.label for z in items if states[z.key] == "non vérifié"]}


def prescan_sections(items: list[Zoning], rows: list[list], headers: list[str],
                     summary: dict, provenance: dict[str, list[Provenance]],
                     today: date) -> list[dict]:
    """Sections de la note de pré-diagnostic (core/report.py::build_markdown)."""
    rank = {key: i for i, key in enumerate(CATEGORIES)}
    ordered = sorted(items, key=lambda z: (_STATE_ORDER[summary["states"][z.key]],
                                           rank.get(z.category, len(rank)), z.label))
    bullets = [f"Protection forte intersectée : {label}" for label in summary["strong_hits"]]
    bullets += [f"Non vérifié (aucune source) : {label}" for label in summary["unchecked"]]
    for z in items:
        for p in provenance.get(z.key, []):
            if p.kind == "cache":
                bullets.append(f"Donnée hors ligne : {z.label} ({p.origin}, "
                               f"{freshness(p, today)})")
            elif p.kind == "erreur":
                bullets.append(f"Source indisponible : {z.label} — {p.origin}")
            if p.truncated:
                bullets.append(f"Donnée possiblement incomplète : {z.label}")
    return [
        {"heading": "Niveau de contrainte indicatif",
         "text": f"**{summary['level'].capitalize()}** (échelle : {', '.join(LEVELS)}).",
         "bullets": bullets},
        {"heading": "Zonages examinés",
         "table": {"headers": ["Catégorie", "Zonage", "Bilan", "Implication probable"],
                   "rows": [[CATEGORIES.get(z.category, z.category), z.label,
                             summary["states"][z.key], z.implication or z.note]
                            for z in ordered]}},
        {"heading": "Détail par zone",
         "text": (f"{DETAIL_ROWS} premières lignes sur {len(rows)} : tableau complet dans "
                  "le fichier exporté." if len(rows) > DETAIL_ROWS else ""),
         "table": {"headers": headers, "rows": rows[:DETAIL_ROWS]}},
        {"heading": "Sources et dates",
         "text": (f"Date du pré-diagnostic : {today.isoformat()}. Couches locales : date "
                  "déclarée, sinon date de modification du fichier."),
         "table": {"headers": ["Zonage", "Origine", "Date de la donnée", "Fraîcheur"],
                   "rows": [[z.label, *describe_sources(provenance.get(z.key, []), today)]
                            for z in items]}},
        {"heading": "Avertissement", "text": DISCLAIMER},
    ]
