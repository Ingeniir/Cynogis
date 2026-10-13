from cynogis.core.project_audit import (
    audit,
    build_sections,
    layer_findings,
    project_findings,
    severity_counts,
    verdict,
)
from cynogis.core.report import build_html

PROJECT = {"file": "C:/etude/projet.qgz", "dirty": False, "crs": "EPSG:2975",
           "geographic": False, "reference_crs": "EPSG:2975", "territories": 1,
           "absolute_paths": False, "layer_count": 3, "territory": "reunion"}


def vector(**facts):
    base = {"id": "a", "name": "parcelles", "kind": "vector", "valid": True,
            "crs": "EPSG:2975", "reference_crs": "EPSG:2975", "geometry": "polygon",
            "feature_count": 10, "geometry_check": {"checked": 10, "invalid": 0,
                                                    "null_or_empty": 0, "multipart": 0}}
    return {**base, **facts}


def severities(findings):
    return [f["severity"] for f in findings]


def test_projet_sain_sans_anomalie():
    assert project_findings(PROJECT) == []
    assert layer_findings(vector(), "EPSG:2975") == []


def test_projet_non_enregistre_et_geographique():
    found = project_findings({**PROJECT, "file": None, "crs": "EPSG:4326", "geographic": True})
    assert "majeur" in severities(found)
    assert any("jamais enregistré" in f["message"] for f in found)


def test_couche_invalide_critique_et_seule():
    found = layer_findings(vector(valid=False))
    assert severities(found) == ["critique"]


def test_scr_geographique_et_geometries_invalides():
    found = layer_findings(vector(crs="EPSG:4326", geographic=True,
                                  geometry_check={"checked": 5, "invalid": 2, "null_or_empty": 1,
                                                  "error_types": {"Auto-intersection": 2}}))
    messages = " ".join(f["message"] for f in found)
    assert "géographique" in messages and "Auto-intersection (2)" in messages
    assert severities(found).count("majeur") == 2


def test_scr_different_de_la_reference():
    found = layer_findings(vector(crs="EPSG:4326"))
    assert severities(found) == ["mineur"]


def test_table_sans_geometrie_ignore_le_scr():
    assert layer_findings(vector(crs=None, geometry="none", geometry_check=None)) == []


def test_couche_memoire_modifiee_et_raster_sans_nodata():
    assert severities(layer_findings(vector(memory=True, modified=True))) == ["majeur", "majeur"]
    raster = {"name": "mnt", "kind": "raster", "valid": True, "crs": "EPSG:2975",
              "nodata": False}
    assert severities(layer_findings(raster)) == ["mineur"]


def test_audit_trie_par_gravite_et_detecte_doublons():
    layers = [vector(), vector(id="b", valid=False), vector(id="c", feature_count=0)]
    findings = audit(PROJECT, layers)
    assert severities(findings)[0] == "critique"
    assert any("Nom porté par 3 couches" in f["message"] for f in findings)
    counts = severity_counts(findings)
    assert counts["critique"] == 1 and "non livrable" in verdict(counts)


def test_sections_rendues_en_html():
    layers = [vector(), {"name": "mnt", "kind": "raster", "valid": True, "nodata": True,
                         "size": "10 x 10", "bands": 1, "pixel_size": "5 x 5"}]
    findings = audit(PROJECT, layers)
    sections = build_sections(PROJECT, layers, findings)
    headings = [s["heading"] for s in sections]
    assert headings[0] == "Synthèse" and "Rasters" in headings
    html = build_html("Audit", sections)
    assert "Inventaire des couches" in html and "parcelles" in html


def test_carte_d_ensemble_inseree_apres_le_projet():
    sections = build_sections(PROJECT, [vector()], [], map_image="audit_carte.png")
    assert sections[2]["heading"] == "Carte d'ensemble"
    html = build_html("Audit", sections)
    assert '<img src="audit_carte.png" width="640"' in html
    assert "Carte d'ensemble" not in [s["heading"] for s in build_sections(PROJECT, [], [])]
