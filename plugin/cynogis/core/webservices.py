"""Catalogue des services web (WMS, WFS) et lecture de leurs GetCapabilities. Python pur.

L'IA désigne un service par son identifiant, jamais par une URL : seuls les serveurs du
catalogue intégré et de ~/.cynogis/web_services.json sont interrogés. Aucun identifiant de
connexion dans ce fichier : un service protégé désigne une configuration d'authentification
QGIS (authcfg, gestionnaire d'authentification), chiffrée par QGIS.

Exemple de fichier (les couches sont découvertes par GetCapabilities ; « layers » restreint
le service à une liste fermée) :
    {"services": [{"id": "ign_bdtopo", "type": "wfs", "title": "BD TOPO IGN",
                   "url": "https://data.geopf.fr/wfs/ows", "max_features": 5000,
                   "layers": ["BDTOPO_V3:batiment"]}]}
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

from .naming import normalize

SERVICES_FILE = Path.home() / ".cynogis" / "web_services.json"
KINDS = ("wms", "wfs")
DEFAULT_MAX_FEATURES = 5_000
MAX_FEATURES_LIMIT = 50_000
_VERSIONS = {"wms": "1.3.0", "wfs": "2.0.0"}
_ID = re.compile(r"^[a-z0-9_]{1,40}$")
_AUTHCFG = re.compile(r"^[A-Za-z0-9]{7}$")
_EPSG = re.compile(r"EPSG(?::|::|/\d+/)(\d+)$", re.IGNORECASE)
# Paramètres d'URL qui trahissent un secret : à mettre dans une configuration authcfg.
_SECRET_KEYS = {"apikey", "api_key", "key", "token", "access_token", "password", "passwd",
                "pwd", "secret", "user", "username"}
_KEYS = {"id", "type", "title", "url", "layers", "format", "max_features", "authcfg", "crs"}
_ABSTRACT_CHARS = 300


@dataclass(frozen=True)
class WebService:
    id: str
    kind: str                       # wms ou wfs
    title: str
    url: str
    layers: tuple[str, ...] = ()    # vide : toutes les couches annoncées par le service
    format: str = "image/png"       # WMS
    max_features: int = DEFAULT_MAX_FEATURES  # WFS : plafond d'entités par requête
    authcfg: str | None = None
    crs: str | None = None          # SCR préféré si le projet n'en impose pas
    builtin: bool = False

    def allows(self, layer: str) -> bool:
        return not self.layers or layer in self.layers

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["type"] = data.pop("kind")
        data["layers"] = list(self.layers) or "toutes (GetCapabilities)"
        data["protected"] = data.pop("authcfg") is not None
        if self.kind == "wms":
            data.pop("max_features")
        else:
            data.pop("format")
        return data


BUILTIN = {s.id: s for s in (
    WebService("geopf_wms", "wms", "Géoplateforme IGN - WMS raster (orthophotos, cartes, "
               "plans, altitude…)", "https://data.geopf.fr/wms-r/wms", builtin=True),
    WebService("geopf_wfs", "wfs", "Géoplateforme IGN - WFS (BD TOPO, cadastre, limites "
               "administratives, zonages…)", "https://data.geopf.fr/wfs/ows", builtin=True),
)}


def check_url(url: str) -> str:
    """URL de service acceptée : https, sans identifiant ni secret dans l'adresse."""
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise ValueError("URL https:// attendue")
    if "@" in parts.netloc:
        raise ValueError("identifiants dans l'URL interdits : utiliser authcfg")
    secrets = [k for k, _ in parse_qsl(parts.query) if k.lower() in _SECRET_KEYS]
    if secrets:
        raise ValueError(f"paramètre secret dans l'URL ({', '.join(secrets)}) : utiliser authcfg")
    return url


def parse_service(raw: Mapping[str, Any]) -> WebService:
    """Valide une entrée du fichier utilisateur ; ValueError avec un message lisible sinon."""
    unknown = set(raw) - _KEYS
    if unknown:
        raise ValueError(f"clés inconnues {sorted(unknown)}")
    sid, kind = raw.get("id"), raw.get("type")
    if not isinstance(sid, str) or not _ID.match(sid):
        raise ValueError("id attendu : minuscules, chiffres, _ (40 caractères max)")
    if kind not in KINDS:
        raise ValueError(f"type attendu : {' ou '.join(KINDS)}")
    url = raw.get("url")
    if not isinstance(url, str):
        raise ValueError("url manquante")
    check_url(url)
    layers = raw.get("layers", [])
    if not isinstance(layers, list) or not all(isinstance(x, str) and x for x in layers):
        raise ValueError("layers : liste de noms de couches attendue")
    fmt = raw.get("format", "image/png")
    if not isinstance(fmt, str) or not fmt.startswith("image/"):
        raise ValueError("format attendu : image/png, image/jpeg…")
    max_features = raw.get("max_features", DEFAULT_MAX_FEATURES)
    if (not isinstance(max_features, int) or isinstance(max_features, bool)
            or not 1 <= max_features <= MAX_FEATURES_LIMIT):
        raise ValueError(f"max_features : entier de 1 à {MAX_FEATURES_LIMIT}")
    authcfg = raw.get("authcfg")
    if authcfg is not None and (not isinstance(authcfg, str) or not _AUTHCFG.match(authcfg)):
        raise ValueError("authcfg : identifiant QGIS de 7 caractères attendu")
    crs = raw.get("crs")
    if crs is not None and normalize_crs(crs) is None:
        raise ValueError("crs attendu sous la forme EPSG:2975")
    title = raw.get("title") or sid
    return WebService(sid, kind, str(title), url, tuple(dict.fromkeys(layers)), fmt,
                      max_features, authcfg, normalize_crs(crs) if crs else None)


def catalog(user_data: Any = None) -> tuple[dict[str, WebService], list[str]]:
    """Catalogue intégré complété (ou surchargé, à id égal) par le fichier utilisateur.
    Renvoie aussi les entrées rejetées, avec la raison."""
    services = dict(BUILTIN)
    rejected: list[str] = []
    if user_data is None:
        return services, rejected
    entries = user_data.get("services") if isinstance(user_data, Mapping) else None
    if not isinstance(entries, list):
        return services, ["fichier : objet {\"services\": [...]} attendu"]
    for i, raw in enumerate(entries):
        label = raw.get("id", f"#{i + 1}") if isinstance(raw, Mapping) else f"#{i + 1}"
        try:
            if not isinstance(raw, Mapping):
                raise ValueError("objet attendu")
            service = parse_service(raw)
        except ValueError as exc:
            rejected.append(f"{label} : {exc}")
            continue
        services[service.id] = service
    return services, rejected


def capabilities_url(service: WebService) -> str:
    query = urlencode({"SERVICE": service.kind.upper(), "REQUEST": "GetCapabilities",
                       "VERSION": _VERSIONS[service.kind]})
    return f"{service.url}{'&' if '?' in service.url else '?'}{query}"


def normalize_crs(text: str) -> str | None:
    """« urn:ogc:def:crs:EPSG::2975 », « EPSG:2975 », « …/EPSG/0/2975 » → « EPSG:2975 »."""
    match = _EPSG.search(text.strip())
    return f"EPSG:{match.group(1)}" if match else None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(elem: ET.Element, name: str) -> str | None:
    for child in elem:
        if _local(child.tag) == name:
            return (child.text or "").strip() or None
    return None


def _children_text(elem: ET.Element, names: Iterable[str]) -> list[str]:
    wanted = set(names)
    return [(c.text or "").strip() for c in elem if _local(c.tag) in wanted and c.text]


def _crs_list(texts: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(c for c in map(normalize_crs, texts) if c))


def _short(text: str | None) -> str | None:
    if not text:
        return None
    text = " ".join(text.split())
    return text if len(text) <= _ABSTRACT_CHARS else text[:_ABSTRACT_CHARS - 1] + "…"


def _wms_layers(elem: ET.Element, inherited: list[str], out: list[dict[str, Any]]) -> None:
    crs = list(dict.fromkeys(inherited + _crs_list(_children_text(elem, ("CRS", "SRS")))))
    name = _child_text(elem, "Name")
    if name:
        out.append({"name": name, "title": _child_text(elem, "Title"),
                    "abstract": _short(_child_text(elem, "Abstract")), "crs": crs,
                    "queryable": elem.get("queryable") == "1"})
    for child in elem:
        if _local(child.tag) == "Layer":
            _wms_layers(child, crs, out)


def parse_capabilities(kind: str, content: bytes) -> list[dict[str, Any]]:
    """Couches annoncées par un GetCapabilities WMS (1.1/1.3) ou WFS (1.x/2.0) :
    nom, titre, résumé, SCR proposés. ValueError si le serveur renvoie une exception."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ValueError(f"réponse XML illisible ({exc})") from exc
    if "Exception" in _local(root.tag):
        message = " ".join(t.strip() for t in root.itertext() if t.strip())
        raise ValueError(f"le serveur a répondu par une erreur : {message[:500]}")
    layers: list[dict[str, Any]] = []
    if kind == "wms":
        for capability in (e for e in root if _local(e.tag) == "Capability"):
            for top in (e for e in capability if _local(e.tag) == "Layer"):
                _wms_layers(top, [], layers)
        return layers
    for ft in root.iter():
        if _local(ft.tag) != "FeatureType":
            continue
        name = _child_text(ft, "Name")
        if name:
            layers.append({"name": name, "title": _child_text(ft, "Title"),
                           "abstract": _short(_child_text(ft, "Abstract")),
                           "crs": _crs_list(_children_text(
                               ft, ("DefaultCRS", "DefaultSRS", "SRS", "OtherCRS", "OtherSRS")))})
    return layers


def search_layers(layers: list[dict[str, Any]], service: WebService, text: str | None,
                  limit: int) -> dict[str, Any]:
    """Couches autorisées dont le nom ou le titre contient tous les mots de text."""
    words = normalize(text).split() if text else []
    matches = [layer for layer in layers if service.allows(layer["name"])
               and all(w in normalize(f"{layer['name']} {layer['title'] or ''}") for w in words)]
    return {"total": len(matches), "truncated": len(matches) > limit, "layers": matches[:limit]}


def choose_crs(supported: list[str], preferred: Iterable[str | None]
               ) -> tuple[str | None, str | None]:
    """Premier SCR préféré proposé par le service, sinon le premier du service (le SCR par
    défaut en WFS), avec un avertissement. (None, None) si le service n'annonce rien."""
    wanted = [c for c in preferred if c]
    for crs in wanted:
        if crs in supported:
            return crs, None
    if not supported:
        return (wanted[0] if wanted else None), None
    warning = (f"SCR {wanted[0]} non proposé par le service : couche en {supported[0]}, "
               "reprojetée à la volée par QGIS." if wanted else None)
    return supported[0], warning


def wms_params(service: WebService, layer: str, crs: str | None) -> dict[str, str]:
    params = {"url": service.url, "layers": layer, "styles": "", "format": service.format,
              "crs": crs or "EPSG:3857"}
    if service.authcfg:
        params["authcfg"] = service.authcfg
    return params


def wfs_params(service: WebService, layer: str, crs: str | None,
               max_features: int) -> dict[str, str]:
    """restrictToRequestBBOX : QGIS ne demande que l'emprise affichée ou filtrée."""
    params = {"url": service.url, "typename": layer, "version": "auto",
              "maxNumFeatures": str(min(max_features, service.max_features)),
              "restrictToRequestBBOX": "1"}
    if crs:
        params["srsname"] = crs
    if service.authcfg:
        params["authcfg"] = service.authcfg
    return params
