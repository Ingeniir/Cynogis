import json
from dataclasses import FrozenInstanceError

import pytest

from cynogis.core.landcover import LandcoverConfig


def test_default_config():
    config = LandcoverConfig()

    assert config.working_resolution_m == 0.5
    assert config.segment_min_area_m2 == 5.0
    assert config.min_mapping_area_m2 == 150.0
    assert config.simplification_m == 0.75
    assert config.preserve_linear_features is True


@pytest.mark.parametrize(
    "field",
    [
        "working_resolution_m",
        "segment_min_area_m2",
        "min_mapping_area_m2",
    ],
)
@pytest.mark.parametrize(
    "value",
    [0, -1, float("nan"), float("inf"), float("-inf"), True, "1", None],
)
def test_positive_parameters_reject_invalid_values(field, value):
    with pytest.raises(ValueError, match=field):
        LandcoverConfig(**{field: value})


@pytest.mark.parametrize(
    "value",
    [-1, float("nan"), float("inf"), float("-inf"), True, "1", None],
)
def test_simplification_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="simplification_m"):
        LandcoverConfig(simplification_m=value)


def test_zero_simplification_is_allowed():
    config = LandcoverConfig(simplification_m=0)

    assert config.simplification_m == 0


@pytest.mark.parametrize("value", [0, 1, "true", None])
def test_linear_protection_requires_boolean(value):
    with pytest.raises(ValueError, match="preserve_linear_features"):
        LandcoverConfig(preserve_linear_features=value)


def test_linear_protection_can_be_disabled():
    config = LandcoverConfig(preserve_linear_features=False)

    assert config.preserve_linear_features is False


def test_segments_cannot_be_coarser_than_mapping_units():
    with pytest.raises(ValueError, match="segment_min_area_m2"):
        LandcoverConfig(
            segment_min_area_m2=200,
            min_mapping_area_m2=100,
        )


def test_equal_area_thresholds_are_allowed():
    config = LandcoverConfig(
        segment_min_area_m2=100,
        min_mapping_area_m2=100,
    )

    assert config.segment_min_area_m2 == config.min_mapping_area_m2


def test_config_is_immutable():
    config = LandcoverConfig()

    with pytest.raises(FrozenInstanceError):
        config.working_resolution_m = 2.0


def test_config_is_json_serializable():
    config = LandcoverConfig()

    payload = json.dumps(config.to_dict(), allow_nan=False)

    assert json.loads(payload) == {
        "working_resolution_m": 0.5,
        "segment_min_area_m2": 5.0,
        "min_mapping_area_m2": 150.0,
        "simplification_m": 0.75,
        "preserve_linear_features": True,
    }


def test_serialized_data_is_independent():
    config = LandcoverConfig()
    data = config.to_dict()

    data["working_resolution_m"] = 20

    assert config.working_resolution_m == 0.5


def test_extremely_large_number_is_rejected():
    with pytest.raises(ValueError, match="working_resolution_m"):
        LandcoverConfig(working_resolution_m=10**1000)
