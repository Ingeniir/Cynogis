import pytest

from cynogis.core.report import (
    build_html,
    build_markdown,
    normalize_sections,
    normalize_table,
    table_to_rows,
)


def sections():
    return [
        {
            "heading": "Occupation du sol",
            "text": "La canne domine les bas de la zone d'étude.",
            "bullets": ["3 unités paysagères", "Imperméabilisation de 18 %"],
            "table": {
                "headers": ["Classe", "Surface (ha)"],
                "rows": [["Canne", 125.5], ["Forêt", 48.25]],
            },
        }
    ]

def test_normalize_table_depuis_dictionnaires():
    table = normalize_table({"rows": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]})
    assert table["headers"] == ["a", "b"]
    assert table["rows"] == [[1, 2], [3, 4]]


def test_normalize_table_complete_les_lignes_courtes():
    table = normalize_table({"headers": ["a", "b"], "rows": [[1], [2, 3]]})
    assert table["rows"][0] == [1, None]


def test_normalize_table_trop_grande():
    with pytest.raises(ValueError, match="volumineux"):
        normalize_table({"rows": [[1]] * 2001})


def test_normalize_sections_titre_par_defaut():
    assert normalize_sections([{}])[0]["heading"] == "Section 1"


def test_normalize_sections_refuse_non_objet():
    with pytest.raises(ValueError):
        normalize_sections(["du texte"])


def test_markdown_contient_titre_et_tableau():
    contenu = build_markdown("Diagnostic paysager", sections(), {"Commune": "Saint-Paul"})
    assert contenu.startswith("# Diagnostic paysager")
    assert "## Occupation du sol" in contenu
    assert "| Classe | Surface (ha) |" in contenu
    assert "125,50" in contenu          # formatage français
    assert "**Commune**" in contenu


def test_markdown_valeurs_absentes():
    contenu = build_markdown("T", [{"heading": "S", "table": {"rows": [[None]]}}])
    assert "—" in contenu


def test_html_echappe_les_balises():
    contenu = build_html("Test <script>", [{"heading": "A & B", "text": "x < y"}])
    assert "<script>" not in contenu.split("<title>")[1].split("</title>")[0]
    assert "A &amp; B" in contenu


def test_html_structure_minimale():
    contenu = build_html("Titre", sections())
    assert contenu.startswith("<!DOCTYPE html>")
    assert contenu.rstrip().endswith("</html>")
    assert "<table>" in contenu


def test_table_to_rows():
    table = table_to_rows([{"classe": "Canne", "surface": 12.0}], ["classe", "surface"])
    assert table["rows"] == [["Canne", 12.0]]


def test_table_to_rows_vide():
    assert table_to_rows([])["rows"] == []


def test_image_relative_et_markdown():
    section = [{"heading": "Carte", "image": r"dossier\carte.png", "caption": "Vue"}]
    assert normalize_sections(section)[0]["image"] == "dossier/carte.png"
    assert "![Vue](dossier/carte.png)" in build_markdown("Titre", section)
