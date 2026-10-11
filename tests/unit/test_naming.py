from cynogis.core.naming import clean_name, normalize, unique_path


def test_clean_name():
    assert clean_name("Zones tampon 50 m (Saint-Paul)") == "zones_tampon_50_m_saint_paul"
    assert clean_name("Écart à l'île") == "ecart_a_l_ile"
    assert clean_name("../../etc/passwd") == "etc_passwd"
    assert clean_name("***") == "sortie"
    assert clean_name("CON") == "con_"
    assert len(clean_name("a" * 200)) == 60


def test_unique_path_never_overwrites(tmp_path):
    first = unique_path(tmp_path, "buffer", ".gpkg")
    assert first.name == "buffer.gpkg"
    first.touch()
    second = unique_path(tmp_path, "buffer", ".gpkg")
    assert second.name == "buffer_2.gpkg"
    second.touch()
    assert unique_path(tmp_path, "buffer", ".gpkg").name == "buffer_3.gpkg"


def test_normalize():
    assert normalize("  Forêt   d'ÉTANG ") == "foret d'etang"
