from threading import Event

import pytest

from cynogis.core.landcover_execution import (
    PreparationCancelledError,
    PreparationControl,
)


def test_default_control_does_nothing():
    control = PreparationControl()

    control.checkpoint(0)
    control.checkpoint(50)
    control.checkpoint(99)


def test_progress_is_forwarded():
    received = []
    control = PreparationControl(on_progress=received.append)

    control.checkpoint(0)
    control.checkpoint(35)
    control.checkpoint(99)

    assert received == [0.0, 35.0, 99.0]


def test_cancellation_before_callback():
    received = []
    control = PreparationControl(
        on_progress=received.append,
        is_cancelled=lambda: True,
    )

    with pytest.raises(PreparationCancelledError):
        control.checkpoint(20)

    assert received == []


def test_cancellation_requested_during_callback():
    cancelled = Event()

    def progress(_value):
        cancelled.set()

    control = PreparationControl(
        on_progress=progress,
        is_cancelled=cancelled.is_set,
    )

    with pytest.raises(PreparationCancelledError):
        control.checkpoint(20)


def test_callback_failure_is_not_hidden():
    def progress(_value):
        raise RuntimeError("Échec du callback")

    control = PreparationControl(on_progress=progress)

    with pytest.raises(RuntimeError, match="Échec du callback"):
        control.checkpoint(20)


def test_cancellation_check_failure_is_not_hidden():
    def cancelled():
        raise RuntimeError("Contrôle indisponible")

    control = PreparationControl(is_cancelled=cancelled)

    with pytest.raises(RuntimeError, match="Contrôle indisponible"):
        control.checkpoint(20)
