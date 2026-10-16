import asyncio
import json

import pytest

from cynogis.bridge.protocol import PROTOCOL_VERSION, Response, decode_request
from cynogis.core.audit import AuditLog
from cynogis.core.dispatcher import Dispatcher, ToolResult
from cynogis.core.errors import ErrorCode, ToolError
from cynogis.core.jobs import AlgCall
from cynogis.core.registry import Level, ToolRegistry, tool
from cynogis.core.schema import Param


def _req(method, **params):
    raw = {"v": PROTOCOL_VERSION, "id": "1", "method": method, "params": params, "token": "t"}
    return decode_request(json.dumps(raw).encode())


class FakeExecutor:
    """Étapes terminées à la main par le test, comme le ferait une QgsTask."""

    def __init__(self, fail_start=False):
        self.started, self.cancelled, self.fail_start = [], [], fail_start

    def start(self, step, done):
        if self.fail_start:
            raise ToolError(ErrorCode.PROCESSING_FAILED, "paramètres refusés")
        self.started.append((step, done))
        return len(self.started)

    def progress(self, handle):
        return 50.0

    def cancel(self, handle):
        self.cancelled.append(handle)

    def finish(self, value=None, error=None):
        self.started[-1][1](value, error)


@tool(level=Level.CREATE, params={"n": Param("integer", "Nombre")})
def calcul(n):
    """Deux étapes Processing."""
    first = yield AlgCall("native:a", {"N": n})
    second = yield AlgCall("native:b", {"IN": first["OUTPUT"]})
    return ToolResult({"total": second["OUTPUT"]}, ["attention"], outputs=["sortie.gpkg"])


@tool(level=Level.CREATE)
def sans_etape():
    """Générateur qui finit sans Processing."""
    if False:
        yield
    return {"fait": True}


@tool(level=Level.CREATE)
def erreur_avant():
    """Erreur métier avant la première étape."""
    raise ToolError(ErrorCode.LAYER_NOT_FOUND, "absente")
    yield


@tool(level=Level.READ)
def lecture():
    """Lecture seule."""
    return "ok"


def make(tmp_path, executor=None):
    registry = ToolRegistry()
    registry.register(calcul, sans_etape, erreur_avant, lecture)
    executor = executor or FakeExecutor()
    audit = AuditLog(tmp_path)
    return Dispatcher(registry, audit=audit, executor=executor), executor, audit


def test_job_en_deux_etapes(tmp_path):
    d, ex, audit = make(tmp_path)
    resp = d.dispatch(_req("calcul", n=3))
    assert resp.ok and resp.job_id and resp.data["status"] == "running"
    assert resp.data["algorithm"] == "native:a" and audit.recent(5) == []

    status = d.dispatch(_req("get_job_status", job_id=resp.job_id))
    assert status.job_id == resp.job_id and status.data["progress"] == 50.0

    ex.finish({"OUTPUT": 1})
    assert ex.started[1][0] == AlgCall("native:b", {"IN": 1})
    ex.finish({"OUTPUT": 7})

    final = d.dispatch(_req("get_job_status", job_id=resp.job_id))
    assert final.ok and final.job_id is None and final.data == {"total": 7}
    assert final.warnings == ["attention"]
    entry = audit.recent(5)[0]  # un seul enregistrement, à la fin
    assert len(audit.recent(5)) == 1 and entry["outputs"] == ["sortie.gpkg"]
    assert final.audit_id == entry["audit_id"]


def test_echec_d_une_etape(tmp_path):
    d, ex, audit = make(tmp_path)
    job_id = d.dispatch(_req("calcul", n=1)).job_id
    ex.finish(error=ToolError(ErrorCode.PROCESSING_FAILED, "native:a : échec"))
    final = d.dispatch(_req("get_job_status", job_id=job_id))
    assert not final.ok and final.error["code"] == "PROCESSING_FAILED"
    assert audit.recent(1)[0]["ok"] is False


def test_verrou_pendant_un_job(tmp_path):
    d, _, _ = make(tmp_path)
    d.dispatch(_req("calcul", n=1))
    busy = d.dispatch(_req("calcul", n=2))
    assert not busy.ok and busy.error["code"] == "BUSY"
    assert d.dispatch(_req("lecture")).data == "ok"  # les lectures passent


def test_annulation(tmp_path):
    d, ex, _ = make(tmp_path)
    job_id = d.dispatch(_req("calcul", n=1)).job_id
    status = d.dispatch(_req("cancel_job", job_id=job_id))
    assert status.data["status"] == "cancelled" and ex.cancelled == [1]
    ex.finish({"OUTPUT": 1})  # rappel tardif de la tâche : ignoré
    assert len(ex.started) == 1
    final = d.dispatch(_req("get_job_status", job_id=job_id))
    assert final.error["code"] == "CANCELLED"
    assert d.dispatch(_req("calcul", n=2)).job_id  # plus de verrou


def test_generateur_sans_etape_ou_en_erreur_repond_tout_de_suite(tmp_path):
    d, _, _ = make(tmp_path)
    resp = d.dispatch(_req("sans_etape"))
    assert resp.ok and resp.job_id is None and resp.data == {"fait": True}
    resp = d.dispatch(_req("erreur_avant"))
    assert not resp.ok and resp.error["code"] == "LAYER_NOT_FOUND"


def test_lancement_refuse_par_l_executeur(tmp_path):
    d, _, _ = make(tmp_path, FakeExecutor(fail_start=True))
    resp = d.dispatch(_req("calcul", n=1))
    assert not resp.ok and resp.job_id is None and resp.error["code"] == "PROCESSING_FAILED"
    assert d.jobs.running is None


def test_job_inconnu_et_outils_internes_caches(tmp_path):
    d, _, _ = make(tmp_path)
    resp = d.dispatch(_req("get_job_status", job_id="absent"))
    assert resp.error["code"] == "JOB_NOT_FOUND"
    assert "get_job_status" not in d.registry.names and "cancel_job" not in d.registry.names


def test_response_encode_job_id():
    assert json.loads(Response("1", True, {}, job_id="abc").encode())["job_id"] == "abc"
    assert "job_id" not in json.loads(Response("1", True, {}).encode())


# --- Serveur MCP : attente du job ----------------------------------------------------------
class FakeClient:
    def __init__(self, statuses):
        from cynogis_server.client import BridgeResult
        self.result, self.statuses, self.calls = BridgeResult, list(statuses), []

    async def call(self, method, params=None):
        self.calls.append(method)
        if method == "cancel_job":
            return self.result({})
        status = self.statuses.pop(0)
        if status == "bloque":
            await asyncio.sleep(3600)
        if status == "running":
            return self.result({"progress": 10, "step": 1, "algorithm": "native:a"},
                               job_id="j1")
        return self.result({"total": 7}, ["attention"], "a1")


@pytest.fixture
def app(monkeypatch):
    from cynogis_server import app
    monkeypatch.setattr(app, "POLL_FIRST_S", 0)
    return app


def test_wait_job_interroge_jusqu_au_resultat(app, monkeypatch):
    from cynogis_server.client import BridgeResult
    client = FakeClient(["running", "running", "final"])
    monkeypatch.setattr(app, "_client", client)
    result = asyncio.run(app._wait_job(BridgeResult({}, job_id="j1")))
    assert result.data == {"total": 7} and result.job_id is None
    assert client.calls == ["get_job_status"] * 3


def test_wait_job_annule_dans_qgis(app, monkeypatch):
    from cynogis_server.client import BridgeResult
    client = FakeClient(["running", "bloque"])
    monkeypatch.setattr(app, "_client", client)

    async def scenario():
        task = asyncio.create_task(app._wait_job(BridgeResult({}, job_id="j1")))
        while len(client.calls) < 2:
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())
    assert client.calls[-1] == "cancel_job"


def test_wait_job_delai_depasse(app, monkeypatch):
    from cynogis_server.client import BridgeError, BridgeResult
    client = FakeClient(["running"] * 5)
    monkeypatch.setattr(app, "_client", client)
    monkeypatch.setattr(app, "JOB_TIMEOUT_S", -1)
    with pytest.raises(BridgeError) as err:
        asyncio.run(app._wait_job(BridgeResult({}, job_id="j1")))
    assert err.value.code == "TIMEOUT" and client.calls == ["cancel_job"]
