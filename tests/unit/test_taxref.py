import zipfile

from cynogis.core.taxref import (
    TAXREF_FILE,
    find_file,
    match_taxa,
    name_key,
    open_table,
    read_statuses,
)

TAXREF = [
    ["CD_NOM", "CD_REF", "LB_NOM", "NOM_COMPLET", "NOM_VALIDE", "NOM_VERN", "REU", "MAY"],
    ["528679", "528679", "Phelsuma inexpectata", "Phelsuma inexpectata Mertens, 1966",
     "Phelsuma inexpectata Mertens, 1966", "Gecko vert de Manapany", "E", "A"],
    ["442300", "442300", "Pycnonotus jocosus", "Pycnonotus jocosus (Linnaeus, 1758)",
     "Pycnonotus jocosus (Linnaeus, 1758)", "Merle de Maurice, Bulbul orphée", "J", "Y"],
    ["999", "442300", "Otocompsa jocosa", "Otocompsa jocosa", "Pycnonotus jocosus (Linnaeus, "
     "1758)", "", "", ""],
    # Homonyme absent de La Réunion : écarté au profit du taxon présent.
    ["1", "1", "Eulemur fulvus", "Eulemur fulvus", "Eulemur fulvus Foo", "Maki brun, Maki", "A",
     "I"],
    ["2", "2", "Lemur catta", "Lemur catta", "Lemur catta Bar", "Maki", "", "I"],
]


def test_match_taxa():
    names = ["phelsuma  INEXPECTATA", "Bulbul orphée", "Otocompsa jocosa", "528679", "Inconnu",
             "Maki"]
    taxa, ambiguous = match_taxa(TAXREF, names, "reunion")
    assert taxa["phelsuma  INEXPECTATA"].statut_bio == "E"
    assert taxa["Bulbul orphée"].cd_ref == 442300 and taxa["Bulbul orphée"].match == "vernaculaire"
    assert taxa["Otocompsa jocosa"].cd_ref == 442300 and taxa["Otocompsa jocosa"].statut_bio == "J"
    assert taxa["528679"].match == "cd_nom"
    assert "Inconnu" not in taxa
    assert ambiguous == {"Maki": ["Eulemur fulvus Foo", "Lemur catta Bar"]}  # tous deux absents


def test_match_taxa_mayotte_prefere_le_taxon_present():
    taxa, ambiguous = match_taxa([*TAXREF[:5], [*TAXREF[5][:7], "A"]], ["Maki"],
                                 "mayotte")
    assert taxa["Maki"].cd_ref == 1 and not ambiguous


BDC = [
    ["CD_NOM", "CD_REF", "CD_TYPE_STATUT", "CODE_STATUT", "CD_ISO3166_2", "FULL_CITATION"],
    ["528679", "528679", "PD", "REUEA2", "FR-RE", "Arrêté ministériel du 17 février 1989"],
    ["528679", "528679", "LRN", "CR", "FR-RE", "UICN France 2010"],
    ["528679", "528679", "LRM", "CR", "", "IUCN 2023"],
    ["528679", "528679", "PD", "MAYX", "FR-YT", "Arrêté Mayotte"],
    ["442300", "442300", "REGLLUTTE", "X", "FR-RE", "Arrêté préfectoral"],
    ["77338", "77338", "PN", "PNTM3", "", "Arrêté du 10 novembre 2022 <em>tortues</em>"],
]


def test_read_statuses():
    found = read_statuses(BDC, {528679, 442300, 77338}, "reunion")
    gecko = found[528679]
    assert (gecko.lr_terr, gecko.lr_mond) == ("CR", "CR")
    assert gecko.prot_terr == {"Arrêté ministériel du 17 février 1989"}   # pas celui de Mayotte
    assert found[442300].lutte
    assert found[77338].prot_nat == {"Arrêté du 10 novembre 2022 tortues"}


def test_open_table_zip(tmp_path):
    archive = tmp_path / "TAXREF_v18_2025.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("TAXREFv18.txt", "CD_NOM\tLB_NOM\n1\tÉpervier\n")
    with open_table(archive, r"TAXREFv\d+\.txt") as handle:
        assert handle.read().splitlines()[1] == "1\tÉpervier"
    (tmp_path / "TAXREF_LIENS.txt").write_text("")
    assert find_file(tmp_path, TAXREF_FILE) == archive
    assert name_key("<i>Phelsuma</i>  Inexpectata") == "phelsuma inexpectata"
