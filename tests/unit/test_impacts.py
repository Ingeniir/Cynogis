import pytest

from cynogis.core.impacts import build_table, direct_label, ring_labels


def test_anneaux():
    assert ring_labels([50, 200]) == ["indirect 0-50 m", "indirect 50-200 m"]
    assert ring_labels([]) == []
    with pytest.raises(ValueError):
        ring_labels([200, 50])
    with pytest.raises(ValueError):
        ring_labels([0, 50])


def test_tableau():
    categories = [direct_label("définitive"), direct_label("temporaire"), "indirect 0-50 m"]
    pieces = [("Forêt", "Fort", "direct - définitive", 20_000.0),
              ("Forêt", "Fort", "indirect 0-50 m", 5_000.0),
              ("Forêt", "Fort", "direct - temporaire", 10_000.0),
              ("Savane", None, "indirect 0-50 m", 8_000.0)]
    totals = {("Forêt", "Fort"): 300_000.0, ("Savane", None): 50_000.0}
    headers, rows = build_table(pieces, totals, categories)
    assert headers[-3:] == ["Impact direct total (ha)", "Surface de l'habitat (ha)",
                            "Part détruite (%)"]
    assert rows[0] == ["Forêt", "Fort", 2.0, 1.0, 0.5, 3.0, 30.0, 10.0]
    assert rows[1] == ["Savane", None, 0.0, 0.0, 0.8, 0.0, 5.0, 0.0]
    assert rows[-1] == ["Total", None, 2.0, 1.0, 1.3, 3.0, None, None]
