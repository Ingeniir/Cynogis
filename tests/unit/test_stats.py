import pytest

from cynogis.core.stats import describe, describe_groups, to_float


def test_describe_basic():
    s = describe([1, 2, 3, 4])
    assert (s["count"], s["sum"], s["mean"], s["median"]) == (4, 10, 2.5, 2.5)
    assert (s["q1"], s["q3"], s["iqr"]) == (1.75, 3.25, 1.5)
    assert s["std"] == pytest.approx(1.290994) and s["cv"] == pytest.approx(0.516398)


def test_describe_empty_and_single():
    assert describe([])["count"] == 0 and describe([])["mean"] is None
    single = describe([5.0])
    assert single["std"] is None and single["q1"] == 5.0 and single["cv"] is None


@pytest.mark.parametrize("raw, expected", [
    (3, 3.0), ("3.5", 3.5), (None, None), (True, None), ("abc", None), (float("nan"), None),
])
def test_to_float(raw, expected):
    assert to_float(raw) == expected


def test_groups_sorted_by_sum():
    rows = describe_groups({"a": [1.0], "b": [5.0, 5.0], "c": []})
    assert [r["group"] for r in rows] == ["b", "a", "c"]
