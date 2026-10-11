import pytest

from cynogis.core.palettes import (
    all_palettes,
    get_palette,
    load_user_palettes,
    resolve_colors,
    validate_palette,
)
from cynogis.core.style import (
    build_categories,
    describe_options,
    normalize_geometry,
    validate_labels,
    validate_symbol,
)
from cynogis.core.stylehistory import StyleHistory

# --- Symboles --------------------------------------------------------------

def test_validate_symbol_polygone_defaut():
    resultat = validate_symbol({}, "polygon")
    assert resultat["properties"]["style"] == "solid"
    assert "outline_color" in resultat["properties"]


def test_validate_symbol_motif_francais():
    resultat = validate_symbol({"pattern": "hachures_horizontales"}, "polygon")
    assert resultat["properties"]["style"] == "horizontal"


def test_validate_symbol_motif_inconnu():
    with pytest.raises(ValueError, match="Motif"):
        validate_symbol({"pattern": "zigzag"}, "polygon")


def test_validate_symbol_point_forme_francaise():
    resultat = validate_symbol({"shape": "etoile", "size": 4}, "point")
    assert resultat["properties"]["name"] == "star"
    assert resultat["properties"]["size"] == "4.0"


def test_validate_symbol_opacite_hors_bornes():
    with pytest.raises(ValueError, match="opacité"):
        validate_symbol({"opacity": 2}, "polygon")


def test_validate_symbol_propriete_inconnue_signalee():
    resultat = validate_symbol({"fill_color": "#1a9641", "brillance": 3}, "polygon")
    assert resultat["warnings"]


def test_normalize_geometry():
    assert normalize_geometry("surfacique") == "polygon"
    assert normalize_geometry(0) == "point"
    with pytest.raises(ValueError):
        normalize_geometry("raster")


# --- Catégories ------------------------------------------------------------

def test_build_categories_couleurs_automatiques():
    categories = build_categories(["a", "b", "c"], "polygon")
    assert len(categories) == 3
    assert len({entry["color"] for entry in categories}) == 3


def test_build_categories_couleurs_imposees():
    categories = build_categories(
        ["foret", "canne"],
        "polygon",
        categories=[{"value": "foret", "color": "#1a9641", "label": "Forêt"}],
    )
    foret = next(entry for entry in categories if entry["value"] == "foret")
    assert foret["color"] == "#1a9641"
    assert foret["label"] == "Forêt"


def test_build_categories_sans_value():
    with pytest.raises(ValueError, match="value"):
        build_categories(["a"], "polygon", categories=[{"color": "#000000"}])


# --- Étiquettes ------------------------------------------------------------

def test_validate_labels_sans_source():
    with pytest.raises(ValueError):
        validate_labels({})


def test_validate_labels_halo_deduit():
    resultat = validate_labels({"field": "nom", "color": "#000000"})
    assert resultat["halo_color"] == "#ffffff"


def test_validate_labels_placement_inconnu():
    with pytest.raises(ValueError, match="Placement"):
        validate_labels({"field": "nom", "placement": "en_biais"})


def test_describe_options_contenu():
    options = describe_options()
    assert "solid" in options["fill_patterns"]
    assert "circle" in options["marker_shapes"]


# --- Palettes --------------------------------------------------------------

def test_get_palette_etiree():
    assert len(get_palette("vert", 8)) == 8


def test_get_palette_inconnue():
    with pytest.raises(ValueError, match="Palette inconnue"):
        get_palette("arc_en_ciel_magique")


def test_resolve_colors_priorite_aux_couleurs():
    couleurs = resolve_colors(2, palette="vert", colors=["#000000", "#ffffff"])
    assert couleurs[0].startswith("#000000")


def test_resolve_colors_sans_rien():
    assert len(resolve_colors(4)) == 4


def test_validate_palette_trop_courte():
    with pytest.raises(ValueError, match="deux couleurs"):
        validate_palette("test", ["#000000"])


def test_load_user_palettes_ignore_les_erreurs():
    rapport = load_user_palettes(
        {"bonne": ["#000000", "#ffffff"], "mauvaise": ["pas_une_couleur", "#fff"]}
    )
    assert "bonne" in rapport["loaded"]
    assert rapport["rejected"] == ["mauvaise"]
    assert "bonne" in all_palettes()


# --- Historique ------------------------------------------------------------

def test_history_push_pop():
    historique = StyleHistory()
    historique.push("L1", "Parcelles", "<xml1/>", "symbole unique")
    historique.push("L1", "Parcelles", "<xml2/>", "catégories")
    assert historique.depth("L1") == 2
    assert historique.pop("L1").xml == "<xml2/>"
    assert historique.depth("L1") == 1


def test_history_profondeur_limitee():
    historique = StyleHistory(max_depth=3)
    for index in range(6):
        historique.push("L1", "Parcelles", f"<xml{index}/>")
    assert historique.depth("L1") == 3
    assert historique.pop("L1").xml == "<xml5/>"


def test_history_derniere_couche():
    historique = StyleHistory()
    historique.push("L1", "A", "<a/>")
    historique.push("L2", "B", "<b/>")
    assert historique.last_layer() == "L2"
    historique.pop("L2")
    assert historique.last_layer() == "L1"


def test_history_pop_vide():
    assert StyleHistory().pop("inconnu") is None


def test_history_ignore_xml_vide():
    historique = StyleHistory()
    historique.push("L1", "A", "")
    assert historique.depth("L1") == 0


def test_validate_symbol_ignore_les_none():
    # apply_single_style transmet None pour les paramètres non fournis
    assert validate_symbol({"fill_color": None, "size": None}, "polygon")["properties"]["color"]


def test_build_categories_lignes_colorees():
    categories = build_categories(["a", "b"], "line", colors=["#ff0000", "#0000ff"])
    assert [c["symbol"]["properties"]["color"] for c in categories] == [
        "255,0,0,255", "0,0,255,255"]
