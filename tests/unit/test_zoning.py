import json
from datetime import date
from urllib.parse import parse_qs, urlsplit

import pytest

from cynogis.core import zoning
from cynogis.core.zoning import (
    BY_KEY,
    ZONINGS,
    Provenance,
    for_territory,
    getfeature_url,
    status,
)

TODAY = date(2026, 10, 21)
ISLAND = (55.2, -21.4, 55.9, -20.8)
PROJECT = (55.5, -21.2, 55.52, -21.18)


def test_catalogue():
    assert len(BY_KEY) == len(ZONINGS)
    assert all(z.territories and set(z.territories) <= {"reunion", "mayotte"} for z in ZONINGS)
    # Les zonages sans flux national sont explicitement à fournir en couche locale.
    assert {z.key for z in ZONINGS if z.typename is None} == {
        "ens", "sar_smvm", "loi_littoral", "zones_humides"}


def test_par_territoire():
    reunion = {z.key for z in for_territory("reunion")}
    mayotte = {z.key for z in for_territory("mayotte")}
    assert "pn_coeur" in reunion and "pn_coeur" not in mayotte
    assert "pnm" in mayotte and "pnm" not in reunion
    assert [z.key for z in for_territory("reunion", ["ebc", "rnn"])] == ["ebc", "rnn"]
    with pytest.raises(ValueError, match="outre-mer"):
        for_territory("reunion", ["natura2000"])
    with pytest.raises(ValueError, match="inconnus"):
        for_territory("reunion", ["inexistant"])


def test_statut():
    assert status(10.0, 0.0, 1000) == "intersecte"
    assert status(0.0, 350.4, 1000) == "à 350 m"
    assert status(0.0, 1500.0, 1000) == "absent"
    assert status(0.0, None, 1000) == "absent"


def test_url_getfeature():
    url = getfeature_url("https://data.geopf.fr/wfs/ows", "patrinat_rnn:rnn",
                         (55.26, -21.02, 55.30, -20.98), 100)
    query = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
    assert query["TYPENAMES"] == "patrinat_rnn:rnn" and query["COUNT"] == "100"
    assert query["BBOX"] == "-21.02,55.26,-20.98,55.3,urn:ogc:def:crs:EPSG::4326"
    assert "&SERVICE=" in getfeature_url("https://x/wfs?map=a", "t", (0, 0, 1, 1), 1)


def test_categories_et_implications():
    from cynogis.core.zoning import CATEGORIES
    assert all(z.category in CATEGORIES and z.implication for z in ZONINGS)


def test_pre_diagnostic():
    from cynogis.core.report import build_markdown
    from cynogis.core.zoning import assess, prescan_sections
    items = [BY_KEY[k] for k in ("rnn", "znieff1", "ebc", "ens")]
    rows = [["ZNIEFF de type I", "Zone A", "intersecte", 1.2, 10.0, 0.5, 0.0, None],
            ["Réserve naturelle nationale", "Étang", "à 350 m", None, None, None, 350.0, None],
            ["Espace boisé classé (PLU)", None, "absent (rayon 2000 m)", None, None, None,
             None, None],
            ["Espace naturel sensible (ENS)", None, "non vérifié : couche locale à fournir",
             None, None, None, None, None]]
    summary = assess(items, rows)
    assert summary["level"] == "fort" and summary["strong_hits"] == []
    assert summary["states"] == {"rnn": "proche", "znieff1": "intersecte", "ebc": "absent",
                                 "ens": "non vérifié"}
    assert summary["unchecked"] == ["Espace naturel sensible (ENS)"]
    # Une protection forte intersectée : niveau majeur ; rien à proximité : faible.
    assert assess(items, [[*rows[1][:2], "intersecte"]])["level"] == "majeur"
    assert assess(items, rows[2:])["level"] == "faible"

    flux = Provenance("flux", "Géoplateforme IGN (WFS)", "2026-10-20")
    provenance = {"rnn": [flux], "znieff1": [flux], "ebc": [flux],
                  "ens": [Provenance("aucune", "couche locale à fournir")]}
    sections = prescan_sections(items, rows, ["Zonage", "Zone", "Statut", "a", "b", "c", "d",
                                              "e"], summary, provenance, date(2026, 10, 20))
    examined = sections[1]["table"]["rows"]
    assert [r[1] for r in examined][:2] == ["ZNIEFF de type I", "Réserve naturelle nationale"]
    sources = {r[0]: r[2] for r in sections[3]["table"]["rows"]}
    assert sources["ZNIEFF de type I"] == "2026-10-20"
    assert sources["Espace naturel sensible (ENS)"] == ""
    note = build_markdown("Pré-diagnostic", sections)
    assert "## Sources et dates" in note and "**Fort**" in note


def test_getfeature_url_pagination_and_cql():
    url = getfeature_url("https://x/wfs/ows", "wfs_du:prescription_surf",
                         (55.2, -21.4, 55.3, -21.3), 5000, start_index=5000,
                         cql_filter="typepsc='01'", sort_by="gid")
    assert "STARTINDEX=5000" in url and "CQL_FILTER=typepsc%3D%2701%27" in url
    assert "SORTBY=gid+ASC" in url
    assert "BBOX=-21.4%2C55.2%2C-21.3%2C55.3%2Curn" in url      # lat, lon


def test_getfeature_url_first_page_has_no_startindex():
    assert "STARTINDEX" not in getfeature_url("https://x", "t", (0, 0, 1, 1), 10)


def test_every_local_filter_has_server_filter():
    for z in ZONINGS:
        if z.filter:
            assert z.cql_filter, (f"{z.key} : filtre local sans filtre serveur "
                                  "(risque de troncature)")


def test_every_wfs_zoning_has_stable_sort():
    assert all(z.sort_by for z in ZONINGS if z.typename), "SORTBY requis pour paginer"


def test_provenance_roundtrip_and_kind_check():
    p = Provenance("cache", "cache local du 2026-09-01", "2026-09-01", True)
    assert Provenance.from_dict(p.to_dict()) == p
    with pytest.raises(ValueError):
        Provenance("autre", "x")


@pytest.mark.parametrize("p, expected", [
    (Provenance("flux", "o", "2026-10-21"), "du jour"),
    (Provenance("cache", "o", "2026-08-01"), "81 j"),
    (Provenance("cache", "o", "2025-01-01"), "à rafraîchir (658 j)"),
    (Provenance("locale", "o", ""), "date inconnue"),
    (Provenance("erreur", "o"), "—"),
    (Provenance("flux", "o", "2026-10-21", True), "du jour ; incomplète (plafond atteint)"),
])
def test_freshness(p, expected):
    assert zoning.freshness(p, TODAY) == expected


def test_age_never_negative_and_tolerates_garbage():
    assert zoning.age_days("2027-01-01", TODAY) == 0
    assert zoning.age_days("pas une date", TODAY) is None


def test_describe_multiple_sources_and_missing():
    provs = [Provenance("locale", "A", "2026-10-01"), Provenance("locale", "B")]
    assert zoning.describe_sources(provs, TODAY) == ["A ; B", "2026-10-01 ; inconnue",
                                                     "20 j ; date inconnue"]
    assert zoning.describe_sources([], TODAY)[0] == "non examiné"


def test_bbox_rules():
    assert zoning.bbox_covers(ISLAND, PROJECT)
    assert not zoning.bbox_covers(PROJECT, ISLAND)
    old = {"bbox_wgs84": list(ISLAND)}
    assert not zoning.should_replace_cache(old, PROJECT)   # île jamais écrasée par un projet
    assert zoning.should_replace_cache(old, ISLAND)        # rafraîchissement de l'île
    assert zoning.should_replace_cache(None, PROJECT)


def test_cache_meta_roundtrip_and_matching(tmp_path):
    item = BY_KEY["ebc"]
    meta = zoning.cache_meta(item, "2026-10-21", ISLAND, "EPSG:2975", 12, False)
    path = tmp_path / "ebc.json"
    path.write_text(json.dumps(meta), encoding="utf-8")
    assert zoning.read_cache_meta(path) == meta
    assert zoning.cache_matches(meta, item)
    assert not zoning.cache_matches({**meta, "cql_filter": None}, item)


@pytest.mark.parametrize("content", ["", "{", "[]", '{"fetched_on": "x"}',
                                     '{"fetched_on": "x", "features": 0, "bbox_wgs84": [1]}'])
def test_read_cache_meta_rejects_bad_files(tmp_path, content):
    path = tmp_path / "m.json"
    path.write_text(content, encoding="utf-8")
    assert zoning.read_cache_meta(path) is None
    assert zoning.read_cache_meta(tmp_path / "absent.json") is None


def test_cache_root_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("CYNOGIS_REFERENTIALS_DIR", str(tmp_path))
    assert zoning.cache_root() == tmp_path / "zonages"
    gpkg, meta = zoning.cache_paths(tmp_path, "reunion", "apb")
    assert gpkg.name == "apb.gpkg" and meta.parent.name == "reunion"


def test_prescan_sections_lists_sources_with_origin():
    apb, ens = BY_KEY["apb"], BY_KEY["ens"]
    summary = {"level": "faible", "states": {"apb": "absent", "ens": "non vérifié"},
               "strong_hits": [], "unchecked": [ens.label]}
    provenance = {"apb": [Provenance("cache", "cache local du 2026-09-01", "2026-09-01")],
                  "ens": [Provenance("aucune", "couche locale à fournir")]}
    sections = zoning.prescan_sections([apb, ens], [], [], summary, provenance, TODAY)
    sources = next(s for s in sections if s["heading"] == "Sources et dates")
    assert sources["table"]["rows"][0] == [apb.label, "cache local du 2026-09-01",
                                           "2026-09-01", "50 j"]
    assert sources["table"]["rows"][1] == [ens.label, "couche locale à fournir", "", "—"]
    assert any("Donnée hors ligne" in b for b in sections[0]["bullets"])
