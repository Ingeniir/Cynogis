import pytest

from cynogis.core.privacy import is_sensitive_field
from cynogis.core.stats import (correlate, correlation_pairs, describe_categorical,
                                describe_full, linear_fit, ranks, weighted_stats)


def test_describe_full_shape():
    s = describe_full([1, 2, 3, 4, 5])
    assert s["skewness"] == 0 and s["kurtosis"] == pytest.approx(-1.2)
    assert s["range"] == 4 and s["variance"] == 2.5 and s["modes"] == []
    assert s["percentiles"]["p50"] == 3 and s["outliers"]["iqr_count"] == 0


def test_outlier_detected():
    assert describe_full([1, 2, 2, 3, 3, 3, 4, 100])["outliers"]["iqr_count"] == 1


def test_empty():
    assert describe_full([])["ci95_mean"] is None


def test_ranks_ties():
    assert ranks([10, 20, 20, 30]) == [1, 2.5, 2.5, 4]


def test_pearson_and_spearman():
    x = [1, 2, 3, 4, 5]
    assert correlate(x, [2 * v + 1 for v in x])["r"] == 1
    assert correlate(x, [v ** 3 for v in x], "spearman")["r"] == 1
    assert linear_fit(x, [2 * v + 1 for v in x]) == {"slope": 2, "intercept": 1, "r2": 1}


def test_pairs_skip_missing():
    rows = correlation_pairs({"a": [1, 2, None, 4, 5], "b": [2, 4, 6, None, 10]})
    assert rows[0]["n"] == 3


def test_weighted_median():
    assert weighted_stats([1, 2, 3], [1, 1, 10])["median"] == 3


def test_categorical_entropy():
    c = describe_categorical(["a", "a", "b", "b"])
    assert c["shannon"] == pytest.approx(0.693147) and c["evenness"] == 1


@pytest.mark.parametrize("name, expected", [
    ("Prénom", True), ("ddenom", True), ("code_habitat", False), ("surface", False)])
def test_sensitive(name, expected):
    assert is_sensitive_field(name) is expected
