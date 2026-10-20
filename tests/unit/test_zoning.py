from urllib.parse import parse_qs, urlsplit

import pytest

from cynogis.core.zoning import BY_KEY, ZONINGS, for_territory, getfeature_url, status


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
    with pytest.raises(ValueError):
        for_territory("reunion", ["natura2000"])


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

    sections = prescan_sections(items, rows, ["Zonage", "Zone", "Statut", "a", "b", "c", "d",
                                              "e"], summary, "2026-10-20", set())
    examined = sections[1]["table"]["rows"]
    assert [r[1] for r in examined][:2] == ["ZNIEFF de type I", "Réserve naturelle nationale"]
    sources = {r[0]: r[2] for r in sections[3]["table"]["rows"]}
    assert sources["ZNIEFF de type I"] == "2026-10-20"
    assert sources["Espace naturel sensible (ENS)"] == ""
    note = build_markdown("Pré-diagnostic", sections)
    assert "## Sources et dates" in note and "**Fort**" in note
