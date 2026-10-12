"""Zonages réglementaires et d'inventaire de La Réunion et de Mayotte. Python pur.

Sources nationales (WFS de la Géoplateforme IGN, service geopf_wfs) : espaces protégés et
inventaires de l'INPN (couches patrinat_*), forêts publiques de l'ONF, prescriptions des PLU
du Géoportail de l'urbanisme (EBC : typepsc 01). Les noms techniques et les champs ont été
vérifiés sur le service (Parc national de La Réunion : champ zone = Cœur / Adhesion).

Certains zonages n'ont pas de flux national (ENS, SAR / SMVM, espaces de la Loi Littoral,
inventaire des zones humides de la DEAL) : ils doivent être fournis en couches locales,
sinon ils sont signalés « non vérifiés » plutôt que passés sous silence.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

BOTH = ("reunion", "mayotte")


@dataclass(frozen=True)
class Zoning:
    key: str
    label: str
    typename: str | None          # couche WFS geopf_wfs ; None = couche locale à fournir
    name_field: str | None = None
    filter: str | None = None     # expression QGIS sur la couche WFS
    url_field: str | None = None
    territories: tuple[str, ...] = BOTH
    note: str = ""

    def to_dict(self) -> dict:
        return {"key": self.key, "label": self.label,
                "source": self.typename or "couche locale à fournir",
                "territories": list(self.territories), "note": self.note}


def _inpn(key: str, label: str, typename: str, **options) -> Zoning:
    """Couche patrinat_* de l'INPN : nom dans nom_site, fiche dans url_fiche."""
    return Zoning(key, label, typename, name_field="nom_site", url_field="url_fiche", **options)


ZONINGS: tuple[Zoning, ...] = (
    _inpn("pn_coeur", "Cœur du Parc national", "patrinat_pn:parc_national",
           filter="\"zone\" = 'Cœur'", territories=("reunion",)),
    _inpn("pn_adhesion", "Aire d'adhésion du Parc national", "patrinat_pn:parc_national",
           filter="\"zone\" = 'Adhesion'", territories=("reunion",)),
    _inpn("rnn", "Réserve naturelle nationale", "patrinat_rnn:rnn",
           note="Réunion : Étang de Saint-Paul, Réserve marine ; Mayotte : îlot M'Bouzi, "
                "forêts de Mayotte."),
    _inpn("pnm", "Parc naturel marin", "patrinat_pnm:pnm", territories=("mayotte",)),
    _inpn("apb", "Arrêté de protection de biotope (APB)", "patrinat_apb:apb"),
    _inpn("cdl", "Site du Conservatoire du littoral", "patrinat_cdl:conservatoire_littoral"),
    _inpn("ramsar", "Site Ramsar (zone humide d'importance internationale)",
           "patrinat_ramsar:ramsar"),
    _inpn("znieff1", "ZNIEFF de type I", "patrinat_znieff1:znieff1"),
    _inpn("znieff2", "ZNIEFF de type II", "patrinat_znieff2:znieff2"),
    _inpn("znieff1_mer", "ZNIEFF marine de type I", "patrinat_znieff1_mer:znieff1_mer"),
    _inpn("znieff2_mer", "ZNIEFF marine de type II", "patrinat_znieff2_mer:znieff2_mer"),
    Zoning("foret_publique", "Forêt publique (ONF)", "ONF.FORETS_PUBLIQUES:ONF_FORETS_PUBLIQUES",
           name_field="llib_frt", note="Domaniale si cdom_frt = OUI."),
    Zoning("ebc", "Espace boisé classé (PLU)", "wfs_du:prescription_surf",
           name_field="libelle", filter="\"typepsc\" = '01'",
           note="Géoportail de l'urbanisme : PLU publiés seulement."),
    Zoning("ens", "Espace naturel sensible (ENS)", None,
           note="Département : couche locale à fournir."),
    Zoning("sar_smvm", "SAR / SMVM (espaces naturels, coupures d'urbanisation…)", None,
           note="Région / DEAL : couche locale à fournir."),
    Zoning("loi_littoral", "Loi Littoral (espaces remarquables, bande des 50 pas…)", None,
           note="Couche locale à fournir (SAR-SMVM, DEAL)."),
    Zoning("zones_humides", "Zones humides (inventaire)", None,
           note="Inventaire DEAL / département : couche locale à fournir ; Ramsar vérifié "
                "à part."),
)
BY_KEY = {item.key: item for item in ZONINGS}


def for_territory(territory: str | None, keys: list[str] | None = None) -> list[Zoning]:
    """Zonages à examiner : ceux demandés (keys), sinon tous ceux du territoire."""
    if keys:
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
                   count: int) -> str:
    """Requête WFS 2.0 GetFeature en GeoJSON limitée à une emprise (ouest, sud, est, nord) :
    une seule requête HTTP, bien plus rapide que l'ouverture d'une couche WFS par QGIS.
    BBOX en urn EPSG:4326 : ordre latitude, longitude ; le GeoJSON renvoyé est en
    longitude, latitude."""
    west, south, east, north = bbox_wgs84
    params = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
              "TYPENAMES": typename, "OUTPUTFORMAT": "application/json", "COUNT": str(count),
              "SRSNAME": "urn:ogc:def:crs:EPSG::4326",
              "BBOX": f"{south},{west},{north},{east},urn:ogc:def:crs:EPSG::4326"}
    separator = "&" if "?" in base_url else "?"
    return base_url + separator + urlencode(params)
