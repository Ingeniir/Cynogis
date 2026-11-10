import pytest

from cynogis.core.cleanup import run_cleanup_steps


def test_cleanup_executes_every_step_in_order():
    calls = []

    failures = run_cleanup_steps([
        ("première", lambda: calls.append(1)),
        ("deuxième", lambda: calls.append(2)),
    ])

    assert calls == [1, 2]
    assert failures == []


def test_cleanup_continues_after_failure(caplog):
    calls = []
    original_error = RuntimeError("Arrêt impossible")

    def fail():
        calls.append("échec")
        raise original_error

    failures = run_cleanup_steps([
        ("arrêt", fail),
        ("suite", lambda: calls.append("suite")),
    ])

    assert calls == ["échec", "suite"]
    assert len(failures) == 1
    assert failures[0][0] == "arrêt"
    assert failures[0][1] is original_error
    assert "Échec du nettoyage : arrêt" in caplog.text


def test_cleanup_collects_multiple_errors():
    first = ValueError("première erreur")
    second = OSError("seconde erreur")

    def fail_first():
        raise first

    def fail_second():
        raise second

    failures = run_cleanup_steps([
        ("première", fail_first),
        ("deuxième", fail_second),
    ])

    assert failures == [
        ("première", first),
        ("deuxième", second),
    ]


def test_cleanup_accepts_empty_sequence():
    assert run_cleanup_steps([]) == []


@pytest.mark.parametrize("error_type", [KeyboardInterrupt, SystemExit])
def test_cleanup_does_not_swallow_process_interruptions(error_type):
    calls = []

    def interrupt():
        raise error_type()

    with pytest.raises(error_type):
        run_cleanup_steps([
            ("interruption", interrupt),
            ("suite", lambda: calls.append("suite")),
        ])

    assert calls == []
