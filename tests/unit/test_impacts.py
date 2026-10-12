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


def test_poids_enjeu():
    from cynogis.core.impacts import stake_weight
    assert stake_weight("4") == 4.0 and stake_weight("Très fort") == 4.0
    assert stake_weight("inconnu") == 1.0 and stake_weight(None) == 1.0
    assert stake_weight("Fort", {"Fort": 10}) == 10.0


def test_comparaison_variantes():
    from cynogis.core.impacts import compare_variants
    results = {
        "A": {"footprint": 30_000, "direct": 30_000, "indirect": 10_000,
              "by_stake": {"Fort": 20_000, "Faible": 10_000}, "habitats": 2,
              "points_direct": 3, "points_indirect": 1, "weighted": 70_000},
        "B": {"footprint": 30_000, "direct": 30_000, "indirect": 12_000,
              "by_stake": {"Faible": 30_000}, "habitats": 1,
              "points_direct": 0, "points_indirect": 2, "weighted": 30_000},
    }
    headers, rows = compare_variants(results, None, ["Fort", "Faible"])
    assert headers[-2] == "Direct évité / A (ha)"     # référence : la plus impactante
    assert [r[0] for r in rows] == ["B", "A"] and rows[0][1] == 1
    assert rows[0][5:7] == [0.0, 3.0] and rows[0][-1] == 57.1   # (7-3)/7
    assert rows[1][-2:] == [0.0, 0.0]
    with pytest.raises(ValueError):
        compare_variants(results, "C", [])
