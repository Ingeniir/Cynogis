import pytest

from cynogis.core.habref import load_typology, match_habitats

HABREF = [
    ["﻿CD_HAB", "FG_VALIDITE", "CD_TYPO", "LB_CODE", "LB_HAB_FR", "NIVEAU", "PATH_CD_HAB"],
    ["27962", "NR", "78", "5", "Habitats de l'étage mésotherme", "1", "/27962"],
    ["27979", "SUPPR", "78", "5.1", "Végétations mésothermes sur planèzes", "2",
     "/27962/27979"],
    ["30000", "NR", "78", "5.1", "Forêts mésothermes", "2", "/27962/30000"],
    ["26946", "NR", "88", "D2.0", "Falaises et rochers sans végétation vasculaire", "3",
     "/26892/26946"],
]


def test_load_typology_filtre_la_typologie():
    habitats = load_typology(HABREF, "78")
    assert [h.cd_hab for h in habitats] == [27962, 27979, 30000]
    assert habitats[1].path == (27962, 27979) and not habitats[1].valid


def test_match_habitats():
    habitats = load_typology(HABREF, "78")
    matched, unmatched = match_habitats(
        ["5.1", "habitats de l'ETAGE mesotherme", "Végétation mésotherme sur planèze", "Canne",
         "X"], habitats, {"X": "5"})
    assert matched["5.1"][0].cd_hab == 30000          # le nom de référence, pas le supprimé
    assert matched["habitats de l'ETAGE mesotherme"] == (habitats[0], "libellé")
    assert matched["X"] == (habitats[0], "mapping")
    assert unmatched["Végétation mésotherme sur planèze"][0]["cd_hab"] == 27979
    assert unmatched["Canne"] == []


def test_mapping_vers_code_inconnu():
    with pytest.raises(ValueError):
        match_habitats(["a"], load_typology(HABREF, "78"), {"a": "9.9"})
