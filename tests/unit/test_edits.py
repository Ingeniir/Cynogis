import pytest

from cynogis.core.edits import EditJournal, check_batch_size, describe_summary


def journal():
    j = EditJournal()
    j.record("L1", "Parcelles", "add_features", 3)
    j.record("L1", "Parcelles", "update_attributes", 10, "type")
    j.record("L2", "Ravines", "delete_features", 2)
    return j


def test_summary_par_couche():
    bilan = journal().summary()
    assert bilan["layer_count"] == 2
    assert bilan["total_operations"] == 15


def test_summary_filtre():
    bilan = journal().summary("L1")
    assert bilan["layer_count"] == 1
    assert bilan["layers"][0]["operations"]["add_features"] == 3


def test_count_for_operations():
    assert journal().count_for("L1", ["update_attributes"]) == 10


def test_clear_cible():
    j = journal()
    assert j.clear("L1") == 2
    assert j.layer_ids() == ["L2"]


def test_describe_summary_lisible():
    lignes = describe_summary(journal().summary("L2"))
    assert any("Ravines" in ligne for ligne in lignes)
    assert any("supprimées" in ligne for ligne in lignes)


def test_describe_summary_vide():
    assert describe_summary({"layers": []}) == ["Aucune modification en attente."]


def test_check_batch_size():
    check_batch_size(10, limit=10)
    with pytest.raises(ValueError):
        check_batch_size(11, limit=10)
