from cynogis.core.shapefile import (
    MAX_SIZE_BYTES,
    export_plan,
    looks_like_mojibake,
    sidecar_messages,
    sidecar_report,
    size_messages,
)


def test_sidecar_complet():
    rapport = sidecar_report([".shp", ".shx", ".dbf", ".prj", ".cpg"])
    assert rapport.is_complete
    assert not rapport.missing_recommended


def test_sidecar_incomplet():
    rapport = sidecar_report([".shp", ".dbf"])
    assert ".shx" in rapport.missing_required
    assert not rapport.is_complete
    assert any("obligatoires" in message for message in sidecar_messages(rapport))


def test_sidecar_sans_prj():
    rapport = sidecar_report([".shp", ".shx", ".dbf"])
    messages = sidecar_messages(rapport)
    assert any("2975" in message for message in messages)


def test_size_messages_limite():
    messages = size_messages({".shp": MAX_SIZE_BYTES + 1})
    assert messages and "2 Go" in messages[0]


def test_size_messages_sous_seuil():
    assert size_messages({".shp": 1024}) == []


def test_mojibake():
    assert looks_like_mojibake(["ForÃªt"])
    assert not looks_like_mojibake(["Forêt", 12, None])


def test_export_plan_renommage():
    plan = export_plan(["occupation_du_sol", "occupation_du_sous_sol"], {})
    assert len(set(plan["field_mapping"].values())) == 2
    assert plan["renamed"]
    assert any("10 caractères" in message for message in plan["warnings"])


def test_export_plan_type_non_supporte():
    plan = export_plan(["actif"], {"actif": "boolean"})
    assert any("Shapefile" in message for message in plan["warnings"])
