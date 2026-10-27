from pathlib import Path

import pytest

from cynogis.core.territory import detect_territory, is_natura2000_layer, mentions_natura2000

ROOT = Path(__file__).parents[2]


@pytest.mark.parametrize("text, expected", [
    ("Site NATURA 2000", True), ("natura_2000", True), ("Natura-2000", True),
    ("ZNIEFF de type I", False), ("Réserve naturelle", False),
])
def test_mentions_natura2000(text, expected):
    assert mentions_natura2000(text) is expected


@pytest.mark.parametrize("text, expected", [
    ("patrinat_zps:zps", True), ("patrinat_sic:sic", True), ("ZSC", True), ("pSIC", True),
    ("Zones de protection spéciale", True), ("natura2000", True),
    ("patrinat_rnn:rnn", False), ("basic", False), ("BDTOPO_V3:batiment", False),
])
def test_is_natura2000_layer(text, expected):
    assert is_natura2000_layer(text) is expected


def test_natura2000_absent_du_code():
    """Roadmap 2.3 : Natura 2000 n'apparaît que dans les garde-fous et la consigne à l'IA."""
    allowed = {"plugin/cynogis/core/territory.py", "plugin/cynogis/core/webservices.py",
               "plugin/cynogis/core/zoning.py", "plugin/cynogis/tools/webservices.py",
               "plugin/cynogis/tools/export.py", "server/src/cynogis_server/app.py"}
    hits = {p.relative_to(ROOT).as_posix() for d in ("plugin", "server")
            for p in (ROOT / d).rglob("*.py")
            if mentions_natura2000(p.read_text(encoding="utf-8"))}
    assert hits == allowed


@pytest.mark.parametrize("bbox, expected", [
    ((55.44, -20.89, 55.46, -20.87), "reunion"),   # Saint-Denis
    ((55.20, -21.40, 55.85, -20.85), "reunion"),   # île entière
    ((45.22, -12.79, 45.24, -12.77), "mayotte"),   # Mamoudzou
    ((2.30, 48.80, 2.40, 48.90), None),            # Paris
    (None, None),
])
def test_detect(bbox, expected):
    terr = detect_territory(bbox)
    assert (terr.code if terr else None) == expected
