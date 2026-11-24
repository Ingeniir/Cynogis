"""Configuration, étapes de job et annulations de la délimitation OBIA (sans QGIS)."""
from pathlib import Path

import pytest

from cynogis.core.jobs import (
    LANDCOVER_STEPS,
    DelineateLandcover,
    ExtractLandcoverFeatures,
)
from cynogis.core.landcover import DelineationConfig
from cynogis.core.landcover_execution import (
    LANDCOVER_CANCELLED,
    DelineationCancelledError,
    DelineationControl,
    FeatureExtractionCancelledError,
    FeatureExtractionControl,
)

ABS = Path(__file__).resolve().parent


@pytest.mark.parametrize("kwargs", [
    {"color_distance_max": -1}, {"color_distance_max": 443}, {"color_distance_max": True},
    {"min_mapping_area_m2": -0.1}, {"min_mapping_area_m2": float("nan")},
])
def test_config_refusee(kwargs):
    with pytest.raises(ValueError):
        DelineationConfig(**kwargs)


def test_config_bornes_acceptees():
    assert DelineationConfig(0, 0).to_dict() == {"color_distance_max": 0,
                                                 "min_mapping_area_m2": 0}
    DelineationConfig(442, 1e6)


def test_etapes_chemins_absolus():
    with pytest.raises(ValueError, match="absolu"):
        ExtractLandcoverFeatures(Path("relatif"), ABS, ABS)
    with pytest.raises(ValueError, match="DelineationConfig"):
        DelineateLandcover(ABS, ABS, ABS, ABS, config={"color_distance_max": 1})
    step = DelineateLandcover(ABS, ABS, ABS, ABS, DelineationConfig())
    assert isinstance(step, LANDCOVER_STEPS)
    assert isinstance(ExtractLandcoverFeatures(ABS, ABS, ABS), LANDCOVER_STEPS)


@pytest.mark.parametrize(("control", "error"), [
    (FeatureExtractionControl, FeatureExtractionCancelledError),
    (DelineationControl, DelineationCancelledError),
])
def test_annulation_specifique(control, error):
    received = []
    with pytest.raises(error):
        control(on_progress=received.append, is_cancelled=lambda: bool(received)).checkpoint(5)
    assert received == [5.0]
    assert error in LANDCOVER_CANCELLED
