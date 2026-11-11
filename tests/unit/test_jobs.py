import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from cynogis.bridge.protocol import PROTOCOL_VERSION, Response, decode_request
from cynogis.core.audit import AuditLog
from cynogis.core.dispatcher import Dispatcher, ToolResult
from cynogis.core.errors import ErrorCode, ToolError
from cynogis.core.jobs import (
    AlgCall,
    DetachedJobOutcome,
    Fetch,
    JobManager,
    Pacer,
    Pause,
    PrepareLandcover,
    _finish_detached_job,
    note,
    run_now,
)
from cynogis.core.landcover import PreparationConfig
from cynogis.core.landcover_execution import PreparationCancelledError
from cynogis.core.policy import PermissionPolicy
from cynogis.core.registry import Level, ToolRegistry, tool
from cynogis.core.schema import Param


def _req(method, **params):
    raw = {"v": PROTOCOL_VERSION, "id": "1", "method": method, "params": params, "token": "t"}
    return decode_request(json.dumps(raw).encode())


class FakeExecutor:
    """Étapes terminées à la main par le test, comme le ferait une QgsTask."""

    def __init__(self, fail_start=False):
        self.started, self.cancelled, self.fail_start = [], [], fail_start
        self.paused = []

    def start(self, step, done):
        if self.fail_start:
            raise ToolError(ErrorCode.PROCESSING_FAILED, "paramètres refusés")
        self.started.append((step, done))
        return len(self.started)

    def progress(self, handle):
        return 50.0

    def cancel(self, handle):
        self.cancelled.append(handle)

    def pause(self, resume):
        self.paused.append(resume)

    def finish(self, value=None, error=None):
        self.started[-1][1](value, error)

    def resume(self):
        self.paused.pop(0)()


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


@tool(level=Level.READ, params={"n": Param("integer", "Nombre")})
def boucle(n):
    """Boucle Python avec points de pause."""
    pace = Pacer("boucle", n, interval_s=0)
    total = 0
    for i in range(n):
        yield from pace(i)
        total += i
    return {"total": total}


@tool(level=Level.READ)
def telechargement():
    """Téléchargement puis traitement."""
    fields, features = yield Fetch("https://exemple/wfs", None, "téléchargement de rnn",
                                   geojson=True)
    return {"champs": fields, "entites": len(features)}


@tool(level=Level.READ)
def lecture():
    """Lecture seule."""
    return "ok"


def make(tmp_path, executor=None):
    registry = ToolRegistry()
    registry.register(calcul, sans_etape, erreur_avant, boucle, telechargement, lecture)
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


def test_boucle_avec_pauses(tmp_path):
    d, ex, _ = make(tmp_path)
    resp = d.dispatch(_req("boucle", n=4))
    assert resp.job_id and resp.data["algorithm"] == "boucle" and resp.data["progress"] == 0
    ex.resume()
    ex.resume()
    status = d.dispatch(_req("get_job_status", job_id=resp.job_id))
    assert status.data["progress"] == 50.0 and status.data["step"] == 0
    ex.resume()
    ex.resume()
    final = d.dispatch(_req("get_job_status", job_id=resp.job_id))
    assert final.data == {"total": 6} and not ex.paused


def test_annulation_pendant_une_pause(tmp_path):
    d, ex, _ = make(tmp_path)
    job_id = d.dispatch(_req("boucle", n=4)).job_id
    d.dispatch(_req("cancel_job", job_id=job_id))
    ex.resume()  # la reprise programmée arrive après l'annulation : ignorée
    assert not ex.paused
    assert d.dispatch(_req("get_job_status", job_id=job_id)).error["code"] == "CANCELLED"


def test_telechargement(tmp_path):
    d, ex, _ = make(tmp_path)
    resp = d.dispatch(_req("telechargement"))
    assert resp.data["algorithm"] == "téléchargement de rnn" and resp.data["step"] == 1
    assert isinstance(ex.started[0][0], Fetch)
    ex.finish((["nom"], [1, 2, 3]))
    final = d.dispatch(_req("get_job_status", job_id=resp.job_id))
    assert final.data == {"champs": ["nom"], "entites": 3}


def test_echec_reseau(tmp_path):
    d, ex, _ = make(tmp_path)
    job_id = d.dispatch(_req("telechargement")).job_id
    ex.finish(error=ToolError(ErrorCode.NETWORK_ERROR, "Service injoignable"))
    assert d.dispatch(_req("get_job_status", job_id=job_id)).error["code"] == "NETWORK_ERROR"


@tool(level=Level.READ)
def mesure_invalide():
    """Helper qui note deux géométries réparées."""
    note("{n} géométrie(s) réparée(s)")
    note("{n} géométrie(s) réparée(s)")
    return ToolResult({"ok": True}, ["attention"])


@tool(level=Level.CREATE)
def job_invalide():
    """Notes avant et après une étape Processing."""
    note("{n} réparée(s)")
    yield AlgCall("native:a", {})
    note("{n} réparée(s)")
    return {"fait": True}


def test_notes_ajoutees_aux_warnings(tmp_path):
    registry = ToolRegistry()
    registry.register(mesure_invalide, job_invalide)
    ex = FakeExecutor()
    d = Dispatcher(registry, executor=ex)
    resp = d.dispatch(_req("mesure_invalide"))
    assert resp.warnings == ["attention", "2 géométrie(s) réparée(s)"]

    job_id = d.dispatch(_req("job_invalide")).job_id
    # lecture pendant le job : ses notes ne se mélangent pas à celles du job
    assert d.dispatch(_req("mesure_invalide")).warnings[-1] == "2 géométrie(s) réparée(s)"
    ex.finish({})
    final = d.dispatch(_req("get_job_status", job_id=job_id))
    assert final.ok and final.warnings == ["2 réparée(s)"]
    note("{n} hors appel")  # hors outil : sans effet ni erreur


def test_pacer_ne_cede_qu_apres_l_intervalle():
    lent = Pacer("x", interval_s=3600)
    assert list(lent()) == []
    rapide = Pacer("x", total=8, interval_s=0)
    assert list(rapide(2)) == [Pause("x", 25.0)]


def test_run_now():
    def steps():
        yield Pause("x")
        return 42

    def algo():
        yield AlgCall("native:a", {})

    assert run_now(steps()) == 42
    with pytest.raises(TypeError):
        run_now(algo())


def test_response_encode_job_id():
    assert json.loads(Response("1", True, {}, job_id="abc").encode())["job_id"] == "abc"
    assert "job_id" not in json.loads(Response("1", True, {}).encode())


# --- Serveur MCP : attente du job ----------------------------------------------------------
class FakeClient:
    def __init__(self, statuses):
        from cynogis_server.client import BridgeResult
        self.result, self.statuses, self.calls = BridgeResult, list(statuses), []
        self.cancel_requested = False

    async def call(self, method, params=None):
        self.calls.append(method)
        if method == "cancel_job":
            self.cancel_requested = True
            return self.result({
                "status": "running",
                "cancellation_requested": True,
            })

        if method == "get_job_status" and self.cancel_requested:
            from cynogis_server.client import BridgeError

            raise BridgeError(
                "CANCELLED",
                "Annulation confirmée par le faux pont.",
            )
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
    assert client.calls == [
        "get_job_status",
        "get_job_status",
        "cancel_job",
        "get_job_status",
    ]


def test_wait_job_delai_depasse(app, monkeypatch):
    from cynogis_server.client import BridgeError, BridgeResult
    client = FakeClient(["running"] * 5)
    monkeypatch.setattr(app, "_client", client)
    monkeypatch.setattr(app, "JOB_TIMEOUT_S", -1)
    with pytest.raises(BridgeError) as err:
        asyncio.run(app._wait_job(BridgeResult({}, job_id="j1")))
    assert err.value.code == "TIMEOUT"
    assert client.calls == ["cancel_job", "get_job_status"]

    cancellation = err.value.details["cancellation"]
    assert cancellation["request_acknowledged"] is True
    assert cancellation["stop_confirmed"] is True
    assert cancellation["outcome"] == "cancelled"


@tool(level=Level.DESTROY)
def effacer():
    """Action irréversible."""
    return "fait"


def test_job_lance_pendant_la_confirmation(tmp_path):
    """La fenêtre de confirmation laisse tourner la boucle d'événements : un job peut démarrer
    avant le clic, l'action irréversible doit alors être refusée."""
    registry = ToolRegistry()
    registry.register(calcul, effacer)

    def confirm(spec, params):
        return d.dispatch(_req("calcul", n=1)).job_id is not None

    d = Dispatcher(registry, PermissionPolicy(confirm=confirm), executor=FakeExecutor())
    assert d.dispatch(_req("effacer")).error["code"] == "BUSY"


# --- Client du pont ------------------------------------------------------------------------
def test_constantes_du_protocole_identiques():
    from cynogis.bridge import protocol
    from cynogis_server import client
    assert client.PROTOCOL_VERSION == protocol.PROTOCOL_VERSION
    assert client.MAX_MESSAGE_BYTES == protocol.MAX_MESSAGE_BYTES


def test_client_reponse_illisible(tmp_path):
    from cynogis_server.client import BridgeError, QgisBridgeClient

    async def scenario():
        async def handle(reader, writer):
            await reader.readline()
            writer.write(b"pas du json\n")
            await writer.drain()
            writer.close()

        server = await asyncio.start_server(handle, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        conn = tmp_path / "connection.json"
        conn.write_text(json.dumps({"host": "127.0.0.1", "port": port, "token": "t"}))
        async with server:
            with pytest.raises(BridgeError) as err:
                await QgisBridgeClient(conn).call("ping")
        return err.value.code

    assert asyncio.run(scenario()) == "PROTOCOL_ERROR"


# --- Serveur MCP : catalogue en cache mémoire ---------------------------------------------
class CatalogClient:
    def __init__(self):
        self.conn, self.calls = {"port": 1, "token": "a"}, 0

    def _read_connection(self):
        return self.conn

    async def call(self, method, params=None):
        from cynogis_server.client import BridgeResult
        self.calls += 1
        return BridgeResult({"tools": [{"name": f"t{self.calls}"}]})


def test_catalogue_relu_seulement_si_le_pont_change(app, monkeypatch, tmp_path):
    client = CatalogClient()
    monkeypatch.setattr(app, "_client", client)
    monkeypatch.setattr(app, "_specs_cache", None)
    monkeypatch.setattr(app, "CACHE_FILE", tmp_path / "tools_cache.json")
    assert asyncio.run(app._fetch_specs()) == [{"name": "t1"}]
    assert asyncio.run(app._fetch_specs()) == [{"name": "t1"}] and client.calls == 1
    client.conn = {"port": 1, "token": "b"}  # pont redémarré
    assert asyncio.run(app._fetch_specs()) == [{"name": "t2"}] and client.calls == 2

def make_obia(tmp_path):
    dispatcher, executor, audit = make(tmp_path)
    published = []

    @tool(level=Level.CREATE)
    def obia_prepare_test():
        """Outil factice de préparation OBIA."""
        result = yield PrepareLandcover(
            raster_path=Path("source.tif"),
            aoi_wkb=b"test-only",
            aoi_crs_wkt="test-only",
            rgb_bands=(1, 2, 3),
            output_parent=tmp_path,
            config=PreparationConfig(
                validity_policy="respect_source_masks",
            ),
        )
        published.append(result)
        return result

    dispatcher.registry.register(obia_prepare_test)
    return dispatcher, executor, audit, published


def test_obia_job_success(tmp_path):
    dispatcher, executor, _, published = make_obia(tmp_path)

    response = dispatcher.dispatch(_req("obia_prepare_test"))
    assert response.job_id
    assert isinstance(executor.started[0][0], PrepareLandcover)

    report = {"status": "complete", "output_directory": "test-output"}
    executor.finish(report)

    final = dispatcher.dispatch(
        _req("get_job_status", job_id=response.job_id)
    )
    assert final.ok
    assert final.data == report
    assert published == [report]
    assert dispatcher.jobs.running is None


def test_obia_cancel_waits_for_worker(tmp_path):
    dispatcher, executor, _, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id

    response = dispatcher.dispatch(_req("cancel_job", job_id=job_id))

    assert response.data["status"] == "running"
    assert response.data["cancellation_requested"] is True
    assert dispatcher.jobs.running is not None
    assert executor.cancelled == [1]

    # Une lecture simple reste possible.
    assert dispatcher.dispatch(_req("lecture")).data == "ok"

    # Une écriture reste bloquée.
    blocked = dispatcher.dispatch(_req("calcul", n=1))
    assert blocked.error["code"] == "BUSY"

    # Même un outil READ ne doit pas démarrer un deuxième générateur.
    blocked_read_job = dispatcher.dispatch(_req("telechargement"))
    assert blocked_read_job.error["code"] == "BUSY"

    executor.finish(error=PreparationCancelledError("Arrêt confirmé."))

    final = dispatcher.dispatch(_req("get_job_status", job_id=job_id))
    assert final.error["code"] == "CANCELLED"
    assert dispatcher.jobs.running is None
    assert published == []

    # Le verrou est libéré seulement après la confirmation.
    assert dispatcher.dispatch(_req("calcul", n=2)).job_id


def test_obia_repeated_cancel_is_idempotent(tmp_path):
    dispatcher, executor, _, _ = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id

    dispatcher.dispatch(_req("cancel_job", job_id=job_id))
    dispatcher.dispatch(_req("cancel_job", job_id=job_id))

    assert executor.cancelled == [1]
    assert dispatcher.jobs.running is not None

    executor.finish(error=PreparationCancelledError("Arrêt confirmé."))
    assert dispatcher.jobs.running is None


def test_obia_cleanup_failure_remains_failure(tmp_path):
    dispatcher, executor, _, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id

    dispatcher.dispatch(_req("cancel_job", job_id=job_id))

    error = RuntimeError("Nettoyage incomplet : test-output")
    error.__cause__ = PreparationCancelledError("Annulé.")
    executor.finish(error=error)

    final = dispatcher.dispatch(_req("get_job_status", job_id=job_id))

    assert final.error["code"] == "INTERNAL_ERROR"
    assert "Nettoyage incomplet" in final.error["message"]
    assert dispatcher.jobs.get(job_id).status == "failed"
    assert dispatcher.jobs.running is None
    assert published == []


def test_obia_late_cancellation_retains_complete_outputs(tmp_path):
    dispatcher, executor, _, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id

    dispatcher.dispatch(_req("cancel_job", job_id=job_id))
    executor.finish({
        "status": "complete",
        "output_directory": "completed-output",
    })

    final = dispatcher.dispatch(_req("get_job_status", job_id=job_id))

    assert final.error["code"] == "CANCELLED"
    assert final.error["details"] == {
        "retained_output_directory": "completed-output",
        "outputs_loaded": False,
    }
    assert published == []
    assert dispatcher.jobs.running is None


def test_obia_qgis_cancel_without_cancel_job(tmp_path):
    dispatcher, executor, _, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id

    executor.finish(
        error=PreparationCancelledError("Annulation depuis QGIS.")
    )

    final = dispatcher.dispatch(_req("get_job_status", job_id=job_id))

    assert final.error["code"] == "CANCELLED"
    assert dispatcher.jobs.get(job_id).status == "cancelled"
    assert published == []


def test_obia_duplicate_callback_does_not_publish_twice(tmp_path):
    dispatcher, executor, audit, published = make_obia(tmp_path)
    dispatcher.dispatch(_req("obia_prepare_test"))

    callback = executor.started[-1][1]
    report = {"status": "complete"}

    callback(report, None)
    callback(report, None)

    assert published == [report]
    assert len(audit.recent(10)) == 1


def test_obia_start_failure_releases_lock(tmp_path):
    dispatcher, executor, _, published = make_obia(tmp_path)
    executor.fail_start = True

    response = dispatcher.dispatch(_req("obia_prepare_test"))

    assert not response.ok
    assert response.error["code"] == "PROCESSING_FAILED"
    assert dispatcher.jobs.running is None
    assert published == []

def test_cancel_all_continues_after_one_job_fails(caplog):
    calls = []

    first = SimpleNamespace(id="first")
    second = SimpleNamespace(id="second")

    def cancel(job, reason):
        calls.append((job.id, reason))
        if job.id == "first":
            raise RuntimeError("Handle indisponible")

    manager = SimpleNamespace(
        _jobs={"first": first, "second": second},
        cancel=cancel,
    )

    JobManager.cancel_all(manager, "Déchargement du plugin.")

    assert calls == [
        ("first", "Déchargement du plugin."),
        ("second", "Déchargement du plugin."),
    ]
    assert "annulation du job first" in caplog.text
    assert "Handle indisponible" in caplog.text


# --- Détachement des finisseurs (déchargement du plugin) ---------------------------------
# Tests avec doubles (FakeExecutor) : aucune vraie QgsTask.
def _spy_manager():
    executor = FakeExecutor()
    manager = JobManager(executor)
    calls = []

    def finisher(result, error):
        calls.append((result, error))
        return ("réponse normale", result, error)

    def generator():
        value = yield AlgCall("native:a", {})
        return {"fin": value}

    gen = generator()
    job = manager.start("outil", gen, next(gen), finisher)
    return manager, executor, job, calls


def test_sans_detachement_le_finisseur_normal_est_appele():
    _, executor, job, calls = _spy_manager()

    executor.finish({"OUTPUT": 1})

    assert calls == [({"fin": {"OUTPUT": 1}}, None)]
    assert job.response == ("réponse normale", {"fin": {"OUTPUT": 1}}, None)
    assert job.status == "done"


def test_apres_detachement_le_finisseur_n_est_plus_appele():
    manager, executor, job, calls = _spy_manager()

    manager.detach_finishers()
    executor.finish({"OUTPUT": 1})

    assert calls == []
    assert isinstance(job.response, DetachedJobOutcome)
    # Le générateur n'est plus repris : fermé et clos en annulation, pas en succès.
    assert job.status == "cancelled"
    assert job.generator.gi_frame is None
    assert job.handle is None and job.finished is not None


def test_terminaison_detachee_sans_nouvel_audit(tmp_path):
    dispatcher, executor, audit = make(tmp_path)
    job_id = dispatcher.dispatch(_req("calcul", n=1)).job_id
    assert audit.recent(10) == []

    dispatcher.jobs.detach_finishers()
    executor.finish({"OUTPUT": 1})
    executor.finish({"OUTPUT": 2})

    job = dispatcher.jobs.get(job_id)
    assert job.status == "cancelled"  # la seconde étape n'est jamais lancée
    assert len(executor.started) == 1
    assert isinstance(job.response, DetachedJobOutcome)
    assert audit.recent(10) == []


def test_detachement_ne_demande_aucune_annulation_ni_ne_change_le_statut(tmp_path):
    dispatcher, executor, _, _ = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id
    job = dispatcher.jobs.get(job_id)

    dispatcher.jobs.detach_finishers()

    assert executor.cancelled == []
    assert job.cancellation_reason is None
    assert job.status == "running"
    assert dispatcher.jobs.running is job
    assert job.response is None


def test_callbacks_de_terminaison_restent_raccordes(tmp_path):
    dispatcher, executor, _, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id
    callback = executor.started[-1][1]

    dispatcher.jobs.detach_finishers()
    report = {"status": "complete", "output_directory": "sortie"}
    callback(report, None)  # même callback que celui confié à l'exécuteur

    job = dispatcher.jobs.get(job_id)
    assert job.status == "cancelled"
    assert dispatcher.jobs.running is None
    assert published == []  # après détachement, la publication est interdite
    assert job.response.retained_output_directory == "sortie"
    assert job.response.error_code == "CANCELLED"
    assert job.generator.gi_frame is None
    assert job.handle is None


def test_succes_detache_sans_sortie_complete():
    manager, executor, job, calls = _spy_manager()
    manager.detach_finishers()
    executor.finish({"OUTPUT": 1})
    assert job.response.retained_output_directory is None
    assert calls == []


def test_echec_de_fermeture_detache_reste_un_echec_technique():
    executor = FakeExecutor()
    manager = JobManager(executor)
    calls = []

    def generator():
        try:
            yield AlgCall("native:a", {})
        except GeneratorExit:
            raise RuntimeError("fermeture refusée") from None

    gen = generator()
    job = manager.start("outil", gen, next(gen), lambda r, e: calls.append((r, e)))
    manager.detach_finishers()
    executor.finish({"output_directory": "sortie"})

    assert job.status == "failed"
    assert calls == []
    assert job.response.error_type == "RuntimeError"
    assert job.response.error_code is None
    assert job.response.cause_type == "ToolError"
    assert "fermeture du générateur impossible" in job.response.error_message
    # Le détail structuré vient de la cause ToolError, pas du message.
    assert job.response.retained_output_directory == "sortie"


def test_callback_tardif_detache_ne_finalise_pas_deux_fois(tmp_path):
    dispatcher, executor, audit, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id
    callback = executor.started[-1][1]
    dispatcher.jobs.detach_finishers()

    callback({"status": "complete", "output_directory": "sortie"}, None)
    job = dispatcher.jobs.get(job_id)
    response, finished = job.response, job.finished

    callback(None, RuntimeError("callback tardif"))
    callback({"output_directory": "autre"}, None)

    assert job.response is response and job.finished == finished
    assert job.status == "cancelled"
    assert published == []
    assert audit.recent(10) == []


def test_annulation_obia_detachee_attend_le_callback_reel(tmp_path):
    dispatcher, executor, audit, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id
    job = dispatcher.jobs.get(job_id)

    dispatcher.jobs.detach_finishers()
    dispatcher.jobs.cancel_all("Déchargement du plugin.")

    assert executor.cancelled == [1]
    assert job.status == "running"
    assert job.response is None
    assert dispatcher.jobs.running is job

    executor.finish(error=PreparationCancelledError("Arrêt confirmé."))

    assert job.status == "cancelled"
    assert job.response.error_code == "CANCELLED"
    assert job.response.error_type == "ToolError"
    assert published == []
    assert audit.recent(10) == []


def test_erreur_technique_detachee_reste_un_echec(tmp_path):
    dispatcher, executor, audit, published = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id
    job = dispatcher.jobs.get(job_id)

    dispatcher.jobs.detach_finishers()
    dispatcher.jobs.cancel_all("Déchargement du plugin.")
    error = RuntimeError("Préparation échouée ; nettoyage incomplet de residu : bloqué")
    error.__cause__ = PreparationCancelledError("Annulé.")
    executor.finish(error=error)

    assert job.status == "failed"
    assert job.response.error_type == "RuntimeError"
    assert job.response.error_code is None
    assert job.response.cause_type == "PreparationCancelledError"
    # Le chemin n'existe que dans le texte du message : aucun répertoire déduit.
    assert job.response.residual_directory is None
    assert job.response.retained_output_directory is None
    assert published == []
    assert audit.recent(10) == []


def test_double_detachement_sans_effet_supplementaire(tmp_path):
    dispatcher, executor, _, _ = make_obia(tmp_path)
    job_id = dispatcher.dispatch(_req("obia_prepare_test")).job_id
    job = dispatcher.jobs.get(job_id)

    dispatcher.jobs.detach_finishers()
    finisher = job.finisher
    dispatcher.jobs.detach_finishers()

    assert job.finisher is finisher
    assert executor.cancelled == []
    assert job.status == "running"


def test_start_refuse_sur_un_gestionnaire_detache(tmp_path):
    manager = JobManager(FakeExecutor())
    manager.detach_finishers()

    def generator():
        yield AlgCall("native:a", {})

    gen = generator()
    with pytest.raises(ToolError) as caught:
        manager.start("outil", gen, next(gen), lambda r, e: None)
    assert caught.value.code == ErrorCode.BUSY
    assert manager.running is None
    assert manager.executor.started == []

    dispatcher, executor, _ = make(tmp_path)
    dispatcher.jobs.detach_finishers()
    response = dispatcher.dispatch(_req("calcul", n=1))
    assert response.error["code"] == "BUSY"
    assert executor.started == []


# --- DetachedJobOutcome : détails structurés uniquement ----------------------------------
def test_outcome_annulation_tardive_conserve_le_repertoire():
    error = ToolError(ErrorCode.CANCELLED, "Annulé.",
                      {"retained_output_directory": "complet", "outputs_loaded": False})
    outcome = _finish_detached_job(None, error)
    assert outcome == DetachedJobOutcome(
        error_type="ToolError", error_code="CANCELLED", error_message="Annulé.",
        cause_type=None, retained_output_directory="complet", residual_directory=None)


def test_outcome_runtime_error_causee_par_tool_error():
    cause = ToolError(ErrorCode.CANCELLED, "Annulé.",
                      {"retained_output_directory": "complet",
                       "residual_directory": "residu"})
    error = RuntimeError("Annulé. ; fermeture du générateur impossible : x")
    error.__cause__ = cause
    outcome = _finish_detached_job(None, error)
    assert outcome.error_type == "RuntimeError"
    assert outcome.error_code is None
    assert outcome.cause_type == "ToolError"
    assert outcome.retained_output_directory == "complet"
    assert outcome.residual_directory == "residu"


def test_outcome_details_de_l_erreur_principale_prioritaires():
    error = ToolError(ErrorCode.PROCESSING_FAILED, "échec",
                      {"retained_output_directory": "principal"})
    error.__cause__ = ToolError(ErrorCode.CANCELLED, "cause",
                                {"retained_output_directory": "cause",
                                 "residual_directory": "residu-cause"})
    outcome = _finish_detached_job(None, error)
    assert outcome.error_code == "PROCESSING_FAILED"
    assert outcome.retained_output_directory == "principal"
    assert outcome.residual_directory == "residu-cause"


def test_outcome_rejette_les_chemins_non_textuels():
    error = ToolError(ErrorCode.CANCELLED, "x",
                      {"retained_output_directory": Path("p"), "residual_directory": 3})
    outcome = _finish_detached_job({"output_directory": ["liste"]}, error)
    assert outcome.retained_output_directory is None
    assert outcome.residual_directory is None


def test_outcome_repli_sur_le_resultat():
    outcome = _finish_detached_job({"output_directory": "resultat"}, None)
    assert outcome == DetachedJobOutcome(
        error_type=None, error_code=None, error_message=None, cause_type=None,
        retained_output_directory="resultat", residual_directory=None)


def test_outcome_n_extrait_jamais_un_chemin_du_message():
    error = RuntimeError("nettoyage incomplet de C:/residu : bloqué")
    error.__cause__ = PreparationCancelledError("Annulé.")
    outcome = _finish_detached_job({"output_directory": 1}, error)
    assert outcome.residual_directory is None
    assert outcome.retained_output_directory is None
    assert all(not isinstance(v, BaseException) for v in vars(outcome).values())
