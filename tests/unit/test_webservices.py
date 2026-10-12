import pytest

from cynogis.core.webservices import (
    BUILTIN,
    capabilities_url,
    catalog,
    choose_crs,
    normalize_crs,
    parse_capabilities,
    search_layers,
    wfs_params,
)

WMS = b"""<?xml version="1.0"?>
<WMS_Capabilities xmlns="http://www.opengis.net/wms" version="1.3.0"><Capability>
 <Layer><Title>Racine</Title><CRS>EPSG:2975</CRS><CRS>EPSG:3857</CRS>
  <Layer queryable="1"><Name>ORTHOIMAGERY.ORTHOPHOTOS</Name>
   <Title>Photographies a\xc3\xa9riennes</Title>
   <CRS>EPSG:4471</CRS></Layer>
 </Layer></Capability></WMS_Capabilities>"""

WFS = b"""<?xml version="1.0"?>
<wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0"><wfs:FeatureTypeList>
 <wfs:FeatureType><wfs:Name>BDTOPO_V3:batiment</wfs:Name>
  <wfs:Title>BDTOPO : B\xc3\xa2timents</wfs:Title>
  <wfs:DefaultCRS>urn:ogc:def:crs:EPSG::2154</wfs:DefaultCRS>
  <wfs:OtherCRS>urn:ogc:def:crs:EPSG::2975</wfs:OtherCRS></wfs:FeatureType>
 <wfs:FeatureType><wfs:Name>BDTOPO_V3:commune</wfs:Name><wfs:Title>Communes</wfs:Title>
 </wfs:FeatureType>
</wfs:FeatureTypeList></wfs:WFS_Capabilities>"""


def _user(**entry):
    return {"services": [{"id": "perso", "type": "wfs", "url": "https://ex.fr/wfs", **entry}]}


def test_catalog_keeps_builtins_and_adds_valid_user_service():
    services, rejected = catalog(_user(layers=["a:b"], max_features=100))
    assert rejected == []
    assert set(BUILTIN) < set(services)
    assert services["perso"].layers == ("a:b",) and services["perso"].max_features == 100


@pytest.mark.parametrize("entry", [
    {"url": "http://ex.fr/wfs"},                        # pas https
    {"url": "https://moi:secret@ex.fr/wfs"},            # identifiants dans l'URL
    {"url": "https://ex.fr/wfs?apikey=123"},            # secret dans l'URL
    {"type": "wmts"},
    {"max_features": 10**9},
    {"authcfg": "trop-long"},
    {"password": "x"},                                  # clé inconnue
])
def test_catalog_rejects_unsafe_or_invalid_entries(entry):
    services, rejected = catalog(_user(**entry))
    assert "perso" not in services and len(rejected) == 1


def test_catalog_rejects_malformed_file():
    assert catalog([1, 2])[1] and catalog({"services": "x"})[1]


@pytest.mark.parametrize("text, expected", [
    ("urn:ogc:def:crs:EPSG::2975", "EPSG:2975"), ("EPSG:4471", "EPSG:4471"),
    ("http://www.opengis.net/def/crs/EPSG/0/2975", "EPSG:2975"), ("CRS:84", None),
])
def test_normalize_crs(text, expected):
    assert normalize_crs(text) == expected


def test_parse_wms_inherits_crs_and_skips_unnamed_layers():
    (layer,) = parse_capabilities("wms", WMS)
    assert layer["name"] == "ORTHOIMAGERY.ORTHOPHOTOS" and layer["queryable"]
    assert layer["crs"] == ["EPSG:2975", "EPSG:3857", "EPSG:4471"]


def test_parse_wfs_and_search():
    layers = parse_capabilities("wfs", WFS)
    assert layers[0]["crs"] == ["EPSG:2154", "EPSG:2975"]
    found = search_layers(layers, BUILTIN["geopf_wfs"], "BATIMENTS bdtopo", 10)
    assert [x["name"] for x in found["layers"]] == ["BDTOPO_V3:batiment"]


def test_search_respects_service_allowlist():
    layers = parse_capabilities("wfs", WFS)
    restricted = catalog(_user(layers=["BDTOPO_V3:commune"]))[0]["perso"]
    assert [x["name"] for x in search_layers(layers, restricted, None, 10)["layers"]] == \
        ["BDTOPO_V3:commune"]


def test_parse_server_exception():
    with pytest.raises(ValueError, match="Layer inconnue"):
        parse_capabilities("wms", b"<ServiceExceptionReport><ServiceException>Layer inconnue"
                                  b"</ServiceException></ServiceExceptionReport>")


def test_choose_crs():
    assert choose_crs(["EPSG:2154", "EPSG:2975"], ["EPSG:2975"]) == ("EPSG:2975", None)
    crs, warning = choose_crs(["EPSG:2154"], ["EPSG:4471", None])
    assert crs == "EPSG:2154" and "EPSG:4471" in warning
    assert choose_crs([], [None, "EPSG:2975"]) == ("EPSG:2975", None)


def test_urls_and_wfs_params_cap_max_features():
    service = catalog(_user(max_features=100))[0]["perso"]
    assert capabilities_url(service) == ("https://ex.fr/wfs?SERVICE=WFS&REQUEST=GetCapabilities"
                                         "&VERSION=2.0.0")
    params = wfs_params(service, "a:b", "EPSG:2975", 10_000)
    assert params["maxNumFeatures"] == "100" and params["srsname"] == "EPSG:2975"
    assert "authcfg" not in params
