import asyncio

import pytest

from cynogis_server import app
from cynogis_server.client import BridgeError, BridgeResult


class ScriptedClient:
    """Faux pont avec une succession explicite de réponses."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    async def call(self, method, params=None):
        self.calls.append((method, params))

        if not self.script:
            raise AssertionError(f"Appel inattendu : {method}")

        expected_method, answer = self.script.pop(0)
        assert method == expected_method

        if isinstance(answer, Exception):
            raise answer

        return answer


def install_client(monkeypatch, script):
    client = ScriptedClient(script)
    monkeypatch.setattr(app, "_client", client)
    monkeypatch.setattr(app, "CANCEL_POLL_S", 0)
    return client


def test_cancel_waits_for_final_confirmation(monkeypatch):
    client = install_client(monkeypatch, [
        (
            "cancel_job",
            BridgeResult({
                "status": "running",
                "cancellation_requested": True,
            }),
        ),
        (
            "get_job_status",
            BridgeResult(
                {"status": "running", "cancellation_requested": True},
                job_id="job-1",
            ),
        ),
        (
            "get_job_status",
            BridgeError("CANCELLED", "Arrêt confirmé."),
        ),
    ])

    report = asyncio.run(app._cancel_and_observe("job-1"))

    assert report["request_acknowledged"] is True
    assert report["stop_confirmed"] is True
    assert report["outcome"] == "cancelled"
    assert len(client.calls) == 3
    assert client.script == []


def test_late_cancellation_preserves_output_details(monkeypatch):
    details = {
        "retained_output_directory": "completed-output",
        "outputs_loaded": False,
    }

    install_client(monkeypatch, [
        ("cancel_job", BridgeResult({"status": "cancelled"})),
        (
            "get_job_status",
            BridgeError("CANCELLED", "Fichiers conservés.", details),
        ),
    ])

    report = asyncio.run(app._cancel_and_observe("job-1"))

    assert report["outcome"] == "cancelled"
    assert report["error"]["details"] == details


def test_cleanup_error_is_not_reported_as_clean_cancellation(monkeypatch):
    install_client(monkeypatch, [
        ("cancel_job", BridgeResult({"status": "running"})),
        (
            "get_job_status",
            BridgeError("INTERNAL_ERROR", "Nettoyage incomplet."),
        ),
    ])

    report = asyncio.run(app._cancel_and_observe("job-1"))

    assert report["outcome"] == "observation_error"
    assert report["stop_confirmed"] is False
    assert report["error"]["code"] == "INTERNAL_ERROR"
    assert report["error"]["message"] == "Nettoyage incomplet."


def test_bridge_failure_does_not_confirm_stop(monkeypatch):
    install_client(monkeypatch, [
        (
            "cancel_job",
            BridgeError("QGIS_UNAVAILABLE", "Pont fermé."),
        ),
    ])

    report = asyncio.run(app._cancel_and_observe("job-1"))

    assert report["request_acknowledged"] is False
    assert report["stop_confirmed"] is False
    assert report["error"]["stage"] == "cancel_job"


def test_job_completed_before_cancellation_took_effect(monkeypatch):
    final_data = {"output_directory": "finished-output"}

    install_client(monkeypatch, [
        ("cancel_job", BridgeResult({"status": "done"})),
        ("get_job_status", BridgeResult(final_data)),
    ])

    report = asyncio.run(app._cancel_and_observe("job-1"))

    assert report["outcome"] == "completed"
    assert report["stop_confirmed"] is True
    assert report["terminal_result"] == final_data


def test_observation_has_bounded_wait(monkeypatch):
    class SlowClient:
        async def call(self, method, params=None):
            if method == "cancel_job":
                return BridgeResult({"status": "running"})

            await asyncio.sleep(3600)
            raise AssertionError("L'attente aurait dû être interrompue.")

    monkeypatch.setattr(app, "_client", SlowClient())
    monkeypatch.setattr(app, "CANCEL_GRACE_S", 0.01)

    async def scenario():
        return await asyncio.wait_for(
            app._cancel_and_observe("job-1"),
            timeout=2,
        )

    report = asyncio.run(scenario())

    assert report["outcome"] == "grace_expired"
    assert report["request_acknowledged"] is True
    assert report["stop_confirmed"] is False


def test_wait_job_timeout_includes_confirmation(monkeypatch):
    install_client(monkeypatch, [
        ("cancel_job", BridgeResult({"status": "cancelled"})),
        (
            "get_job_status",
            BridgeError("CANCELLED", "Arrêt confirmé."),
        ),
    ])

    monkeypatch.setattr(app, "_progress_token", lambda: None)
    monkeypatch.setattr(app, "JOB_TIMEOUT_S", -1)

    with pytest.raises(BridgeError) as caught:
        asyncio.run(app._wait_job(
            BridgeResult({"status": "running"}, job_id="job-1")
        ))

    assert caught.value.code == "TIMEOUT"
    observation = caught.value.details["cancellation"]
    assert observation["outcome"] == "cancelled"
    assert observation["stop_confirmed"] is True


def test_wait_job_normal_success_is_unchanged(monkeypatch):
    client = install_client(monkeypatch, [
        ("get_job_status", BridgeResult({"result": "ok"})),
    ])

    monkeypatch.setattr(app, "_progress_token", lambda: None)
    monkeypatch.setattr(app, "POLL_FIRST_S", 0)

    result = asyncio.run(app._wait_job(
        BridgeResult({"status": "running"}, job_id="job-1")
    ))

    assert result.data == {"result": "ok"}
    assert [method for method, _ in client.calls] == ["get_job_status"]


def test_timeout_preserves_cleanup_error_without_claiming_cancellation(monkeypatch):
    details = {"residual_directory": "incomplete-output"}

    install_client(monkeypatch, [
        ("cancel_job", BridgeResult({"status": "running"})),
        (
            "get_job_status",
            BridgeError(
                "INTERNAL_ERROR",
                "Nettoyage incomplet.",
                details,
            ),
        ),
    ])

    monkeypatch.setattr(app, "_progress_token", lambda: None)
    monkeypatch.setattr(app, "JOB_TIMEOUT_S", -1)

    with pytest.raises(BridgeError) as caught:
        asyncio.run(app._wait_job(
            BridgeResult({"status": "running"}, job_id="job-1")
        ))

    error = caught.value
    assert error.code == "TIMEOUT"

    observation = error.details["cancellation"]
    assert observation["outcome"] == "observation_error"
    assert observation["stop_confirmed"] is False
    assert observation["error"]["code"] == "INTERNAL_ERROR"
    assert observation["error"]["details"] == details

    assert "Une erreur a été reçue" in error.message
    assert "Annulation confirmée" not in error.message
    assert "peut encore être actif" not in error.message
