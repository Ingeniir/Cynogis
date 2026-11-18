import subprocess
import sys
from pathlib import Path
from threading import Event

import pytest

from cynogis.core.landcover_execution import (
    PreparationCancelledError,
    PreparationControl,
    SegmentationCancelledError,
    SegmentationControl,
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


# --- SegmentationControl ---------------------------------------------------------------
def test_segmentation_control_sans_callback():
    control = SegmentationControl()

    assert control.on_progress is None and control.is_cancelled is None
    control.checkpoint(0)
    control.checkpoint(99)


def test_segmentation_progression_flottante():
    received = []
    SegmentationControl(on_progress=received.append).checkpoint(35)

    assert received == [35.0] and type(received[0]) is float


def test_segmentation_annulation_deja_demandee():
    received = []
    control = SegmentationControl(on_progress=received.append, is_cancelled=lambda: True)

    with pytest.raises(SegmentationCancelledError, match="Segmentation OBIA annulée"):
        control.checkpoint(20)
    assert received == []


def test_segmentation_annulation_pendant_le_callback():
    cancelled = Event()
    received = []

    def progress(value):
        received.append(value)
        cancelled.set()

    control = SegmentationControl(on_progress=progress, is_cancelled=cancelled.is_set)
    with pytest.raises(SegmentationCancelledError):
        control.checkpoint(20)
    assert received == [20.0]


def test_segmentation_erreur_du_callback_non_convertie():
    def progress(_value):
        raise RuntimeError("Échec du callback")

    with pytest.raises(RuntimeError, match="Échec du callback") as caught:
        SegmentationControl(on_progress=progress).checkpoint(20)
    assert not isinstance(caught.value, SegmentationCancelledError)


def test_preparation_conserve_son_exception_historique():
    with pytest.raises(PreparationCancelledError) as caught:
        PreparationControl(is_cancelled=lambda: True).checkpoint(0)
    assert not isinstance(caught.value, SegmentationCancelledError)


def test_exceptions_d_annulation_distinctes():
    assert not issubclass(SegmentationCancelledError, PreparationCancelledError)
    assert not issubclass(PreparationCancelledError, SegmentationCancelledError)


def test_import_du_controle_sans_dependances_lourdes():
    script = (
        "import sys; sys.path.insert(0, sys.argv[1]);"
        "from cynogis.core.landcover_execution import SegmentationControl;"
        "print(sorted(m for m in ('qgis', 'osgeo', 'numpy', 'skimage') if m in sys.modules))"
    )
    plugin = Path(__file__).resolve().parents[2] / "plugin"
    # -I : ignore PYTHONHOME/PYTHONPATH éventuellement hérités (stdlib d'un autre Python).
    result = subprocess.run([sys.executable, "-I", "-c", script, str(plugin)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"
