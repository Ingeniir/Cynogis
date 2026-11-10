"""Cycle de vie du pont : BridgeServer et CynogisPlugin (arrêt, échecs, reprise).

Nécessite PyQGIS. Sous pytest sans QGIS, le module est ignoré. Le Python de QGIS
n'embarquant pas pytest, le fichier s'exécute aussi directement :

    "C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" tests/integration/test_bridge_lifecycle.py

Aucun essai ne touche le pont ni le fichier de connexion de la session de l'utilisateur :
CONNECTION_FILE pointe vers un dossier temporaire, le pont du plugin est un double, et le
seul vrai BridgeServer écoute sur un port éphémère.

- test_bridge_* : vrai BridgeServer, sockets et serveur d'écoute remplacés par des doubles ;
- test_real_socket_* : vrai BridgeServer et vraies sockets Qt (QTcpSocket) ;
- test_plugin_* : vrai CynogisPlugin, pont, interface et fichier de connexion en doubles.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import ClassVar

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plugin"))
else:
    import pytest

    pytest.importorskip("qgis.core", exc_type=ImportError)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtNetwork import QAbstractSocket, QTcpSocket

_QGS = QgsApplication.instance()
if _QGS is None:
    _QGS = QgsApplication([], True)
    _QGS.initQgis()

import cynogis.plugin as plugin_mod  # noqa: E402
from cynogis.bridge import connection  # noqa: E402
from cynogis.bridge.protocol import PROTOCOL_VERSION, Response  # noqa: E402
from cynogis.bridge.server import HOST, BridgeServer  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="cynogis_bridge_test_"))


# --- Outils -------------------------------------------------------------------------------
@contextlib.contextmanager
def patched(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)


@contextlib.contextmanager
def raises(exc_type, match=None):
    try:
        yield
    except exc_type as exc:
        if match is not None:
            assert match in str(exc), f"{match!r} absent de {exc!r}"
        return
    raise AssertionError(f"{exc_type.__name__} attendue")


def spin(condition, timeout=5.0) -> bool:
    deadline = time.monotonic() + timeout
    while not condition() and time.monotonic() < deadline:
        QCoreApplication.processEvents()
        time.sleep(0.005)
    return condition()


def request_line(token: str, request_id: str, method: str = "ping") -> bytes:
    return (json.dumps({"v": PROTOCOL_VERSION, "id": request_id, "token": token,
                        "method": method, "params": {}}) + "\n").encode()


class FakeDispatcher:
    def __init__(self, on_dispatch=None):
        self.calls, self.on_dispatch = [], on_dispatch

    def dispatch(self, request):
        self.calls.append(request.id)
        if self.on_dispatch is not None:
            self.on_dispatch(request)
        return Response(request.id, True, {"pong": True})


# --- BridgeServer avec doubles ------------------------------------------------------------
class FakeListener:
    def __init__(self, log, bridge):
        self.log, self.bridge = log, bridge

    def close(self):
        self.log.append(("server.close", self.bridge._stopping))


class FakeSocket:
    def __init__(self, name, log, bridge=None, fail_abort=False, data=b""):
        self.name, self.log, self.bridge = name, log, bridge
        self.fail_abort, self.data, self.written = fail_abort, data, []

    def readAll(self):
        data, self.data = self.data, b""
        return data

    def state(self):
        return QAbstractSocket.SocketState.ConnectedState

    def write(self, payload):
        self.written.append(bytes(payload))

    def flush(self):
        return True

    def abort(self):
        self.log.append((f"{self.name}.abort", self.bridge._stopping if self.bridge else None))
        if self.fail_abort:
            raise RuntimeError(f"abort {self.name} refusé (double)")

    def deleteLater(self):
        self.log.append((f"{self.name}.deleteLater", None))

    def disconnectFromHost(self):
        self.log.append((f"{self.name}.disconnectFromHost", None))


def make_bridge(token="t", dispatcher=None):
    return BridgeServer(dispatcher or FakeDispatcher(), token)


def test_bridge_stopping_set_before_any_close_and_listener_first():
    log = []
    bridge = make_bridge()
    bridge._server = FakeListener(log, bridge)
    for name in ("s1", "s2"):
        bridge._buffers[FakeSocket(name, log, bridge)] = bytearray()
    bridge.stop()
    assert [event for event, _ in log] == [
        "server.close", "s1.abort", "s1.deleteLater", "s2.abort", "s2.deleteLater"]
    assert all(stopping for event, stopping in log if event.endswith(("close", "abort")))
    assert bridge._buffers == {}


def test_bridge_socket_failure_does_not_block_others_and_is_retained():
    log = []
    bridge = make_bridge()
    bridge._server = FakeListener(log, bridge)
    bad = FakeSocket("bad", log, bridge, fail_abort=True)
    good = FakeSocket("good", log, bridge)
    bridge._buffers[bad] = bytearray()
    bridge._buffers[good] = bytearray()
    with raises(RuntimeError, "fermeture de la connexion 1"):
        bridge.stop()
    assert ("good.abort", True) in log and ("good.deleteLater", None) in log
    assert ("bad.deleteLater", None) not in log
    assert list(bridge._buffers) == [bad]  # conservée pour une nouvelle tentative
    bad.fail_abort = False
    bridge.stop()
    assert bridge._buffers == {}
    assert ("bad.deleteLater", None) in log


def test_bridge_no_dispatch_after_stop_request():
    log = []
    dispatcher = FakeDispatcher()
    bridge = make_bridge("t", dispatcher)
    bridge._server = FakeListener(log, bridge)
    sock = FakeSocket("s", log, bridge, fail_abort=True)
    bridge._buffers[sock] = bytearray()
    with raises(RuntimeError):
        bridge.stop()  # la socket reste suivie : on peut encore lui envoyer des octets
    sock.data = request_line("t", "1")
    bridge._on_ready_read(sock)
    bridge._on_new_connection()
    assert dispatcher.calls == []
    assert sock.written == []
    busy = bridge._handle_line(request_line("t", "2").strip())
    assert busy.ok is False and busy.error["code"] == "BUSY"
    assert dispatcher.calls == []


def test_bridge_stop_during_handle_line_drops_response_and_next_lines():
    log = []
    holder = {}
    dispatcher = FakeDispatcher(on_dispatch=lambda _req: holder["bridge"].stop())
    bridge = make_bridge("t", dispatcher)
    holder["bridge"] = bridge
    bridge._server = FakeListener(log, bridge)
    sock = FakeSocket("s", log, bridge, data=request_line("t", "1") + request_line("t", "2"))
    bridge._buffers[sock] = bytearray()
    bridge._on_ready_read(sock)
    assert dispatcher.calls == ["1"]  # la seconde ligne du même tampon n'est pas traitée
    assert sock.written == []         # aucune réponse après la demande d'arrêt


def test_bridge_stopped_instance_cannot_restart():
    bridge = make_bridge()
    bridge.start(0)
    bridge.stop()
    with raises(RuntimeError, "redémarrer"):
        bridge.start(0)
    bridge.deleteLater()


# --- Vrai BridgeServer, vraies sockets Qt -------------------------------------------------
def test_real_socket_cycle_on_ephemeral_port():
    conn_file = TMP / "real_cycle" / "connection.json"
    token = connection.new_token()
    dispatcher = FakeDispatcher()
    with patched(connection, "CONNECTION_FILE", conn_file):
        bridge = BridgeServer(dispatcher, token)
        bridge.start(0)
        port = bridge.port
        assert port > 0
        connection.write_connection_file(HOST, port, token)
        assert json.loads(conn_file.read_text(encoding="utf-8"))["port"] == port

        client = QTcpSocket()
        client.connectToHost(HOST, port)
        assert spin(lambda: client.state() == QAbstractSocket.SocketState.ConnectedState)
        assert spin(lambda: len(bridge._buffers) == 1)
        client.write(request_line(token, "r1"))
        assert spin(lambda: client.canReadLine())
        answer = json.loads(bytes(client.readLine()).decode())
        assert answer["ok"] is True and answer["id"] == "r1"
        assert answer["data"] == {"pong": True}

        idle = QTcpSocket()
        idle.connectToHost(HOST, port)
        assert spin(lambda: len(bridge._buffers) == 2)

        bridge.stop()
        assert bridge._buffers == {}
        unconnected = QAbstractSocket.SocketState.UnconnectedState
        assert spin(lambda: client.state() == unconnected and idle.state() == unconnected)

        assert bridge._server.isListening() is False
        late = QTcpSocket()
        late.connectToHost(HOST, port)
        # Windows réessaie plusieurs fois avant de signaler un refus de connexion.
        assert spin(lambda: late.state() == unconnected, timeout=15)
        assert late.error() == QAbstractSocket.SocketError.ConnectionRefusedError
        assert dispatcher.calls == ["r1"]

        connection.remove_connection_file(token, strict=True)
        assert not conn_file.exists()
        with raises(RuntimeError):
            bridge.start(0)
        bridge.deleteLater()
        for sock in (client, idle, late):
            sock.abort()


# --- CynogisPlugin avec doubles -----------------------------------------------------------
CFG: dict = {}
EVENTS: list = []


class FakeBridgeServer:
    instances: ClassVar[list] = []

    def __init__(self, dispatcher, token, parent=None):
        self.token, self.events, self.port = token, [], 4242
        FakeBridgeServer.instances.append(self)

    def start(self, port=0):
        self.events.append("start")
        if CFG.get("fail_start"):
            raise RuntimeError("écoute refusée (double)")

    def stop(self):
        self.events.append("stop")
        hook = CFG.pop("stop_hook", None)
        if hook is not None:
            hook()
        if CFG.get("stop_failures", 0) > 0:
            CFG["stop_failures"] -= 1
            raise RuntimeError("stop refusé (double)")

    def deleteLater(self):
        self.events.append("deleteLater")


def fake_write(host, port, token):
    EVENTS.append(("write", token))
    if CFG.get("fail_write"):
        raise OSError("écriture refusée (double)")


def fake_remove(token, *, strict=False):
    EVENTS.append(("remove", token, strict))
    if CFG.get("remove_failures", 0) > 0:
        CFG["remove_failures"] -= 1
        raise PermissionError(13, "suppression refusée (double)")


class Bar:
    def pushMessage(self, _title, message, level=None, duration=None):
        EVENTS.append(("push", message, level))


class Iface:
    def mainWindow(self):
        return None

    def messageBar(self):
        return Bar()

    def addToolBarIcon(self, _action):
        EVENTS.append(("addToolBarIcon",))

    def addPluginToMenu(self, _menu, _action):
        EVENTS.append(("addPluginToMenu",))

    def removeToolBarIcon(self, _action):
        EVENTS.append(("removeToolBarIcon",))

    def removePluginMenu(self, _menu, _action):
        EVENTS.append(("removePluginMenu",))


@contextlib.contextmanager
def plugin_env():
    CFG.clear()
    EVENTS.clear()
    FakeBridgeServer.instances.clear()
    with contextlib.ExitStack() as stack:
        stack.enter_context(patched(plugin_mod, "BridgeServer", FakeBridgeServer))
        stack.enter_context(patched(plugin_mod, "write_connection_file", fake_write))
        stack.enter_context(patched(plugin_mod, "remove_connection_file", fake_remove))
        stack.enter_context(patched(plugin_mod, "DATA_DIR", TMP / "data"))
        stack.enter_context(patched(connection, "CONNECTION_FILE", TMP / "unused.json"))
        plugin = plugin_mod.CynogisPlugin(Iface())
        plugin.initGui()
        EVENTS.clear()
        try:
            yield plugin
        finally:
            CFG.clear()
            if not plugin._unloading:
                plugin.unload()


def pushes(text=None):
    return [e for e in EVENTS if e[0] == "push" and (text is None or text in e[1])]


def critical():
    return [e for e in pushes() if e[2] == plugin_mod.Qgis.MessageLevel.Critical]


def test_plugin_stop_failure_keeps_bridge_and_still_removes_file():
    with plugin_env() as plugin:
        plugin._start_bridge()
        bridge, token = plugin._bridge, plugin._token
        EVENTS.clear()
        CFG["stop_failures"] = 1
        with raises(RuntimeError, "Arrêt du pont incomplet"):
            plugin._stop_bridge()
        assert bridge.events == ["start", "stop"]          # pas de deleteLater
        assert plugin._bridge is bridge                     # référence conservée
        recorded = list(EVENTS)
        assert recorded == [("remove", token, True)]       # suppression tentée, strict
        assert plugin._token is None
        assert plugin._bridge_cleanup_pending is True
        assert pushes("Serveur arrêté") == []
        # nouvelle tentative hors déchargement
        plugin._stop_bridge()
        assert bridge.events == ["start", "stop", "stop", "deleteLater"]
        assert plugin._bridge is None and plugin._bridge_cleanup_pending is False
        assert len(pushes("Serveur arrêté")) == 1


def test_plugin_remove_failure_keeps_token():
    with plugin_env() as plugin:
        plugin._start_bridge()
        bridge, token = plugin._bridge, plugin._token
        EVENTS.clear()
        CFG["remove_failures"] = 1
        with raises(RuntimeError, "suppression du fichier de connexion"):
            plugin._stop_bridge()
        assert bridge.events == ["start", "stop", "deleteLater"]
        assert plugin._bridge is None
        assert plugin._token == token
        assert pushes("Serveur arrêté") == []
        plugin._stop_bridge()
        removes = [e for e in EVENTS if e[0] == "remove"]
        assert removes == [("remove", token, True), ("remove", token, True)]
        assert plugin._token is None and plugin._bridge_cleanup_pending is False


def test_plugin_no_new_bridge_while_previous_cleanup_fails():
    with plugin_env() as plugin:
        plugin._start_bridge()
        old = plugin._bridge
        CFG["stop_failures"] = 3
        with raises(RuntimeError):
            plugin._stop_bridge()
        with raises(RuntimeError):
            plugin._start_bridge()
        EVENTS.clear()
        plugin._on_toggled(True)                            # interceptée, notifiée
        assert len(FakeBridgeServer.instances) == 1
        assert plugin._bridge is old
        assert len(critical()) == 1
        assert plugin._action.isChecked() is False
        CFG["stop_failures"] = 0
        plugin._on_toggled(True)
        assert len(FakeBridgeServer.instances) == 2
        assert plugin._bridge is FakeBridgeServer.instances[1]
        assert old.events[-1] == "deleteLater"


def test_plugin_partial_start_failure_keeps_tracked_references():
    with plugin_env() as plugin:
        CFG["fail_start"] = True
        CFG["stop_failures"] = 1
        plugin._on_toggled(True)
        bridge = FakeBridgeServer.instances[0]
        assert plugin._bridge is bridge                     # toujours suivie
        assert plugin._bridge_cleanup_pending is True
        assert ("remove", bridge.token, True) in EVENTS
        assert len(critical()) == 1 and "nettoyage reste incomplet" in critical()[0][1]
        assert pushes("Serveur arrêté") == []
        assert plugin._action.isChecked() is False


def test_plugin_start_failure_with_clean_cleanup_releases_references():
    with plugin_env() as plugin:
        CFG["fail_write"] = True
        plugin._on_toggled(True)
        bridge = FakeBridgeServer.instances[0]
        assert bridge.events == ["start", "stop", "deleteLater"]
        assert plugin._bridge is None and plugin._token is None
        assert plugin._bridge_cleanup_pending is False
        assert len(critical()) == 1
        assert pushes("Serveur arrêté") == []               # serveur jamais disponible


def test_plugin_normal_stop_notifies_once():
    with plugin_env() as plugin:
        plugin._start_bridge()
        bridge, token = plugin._bridge, plugin._token
        assert len(pushes("Serveur démarré")) == 1
        EVENTS.clear()
        plugin._on_toggled(False)
        assert bridge.events == ["start", "stop", "deleteLater"]
        assert ("remove", token, True) in EVENTS
        assert plugin._bridge is None and plugin._token is None
        assert len(pushes("Serveur arrêté")) == 1
        assert critical() == []


def test_plugin_toggle_off_failure_is_notified_without_stopped_message():
    with plugin_env() as plugin:
        plugin._start_bridge()
        EVENTS.clear()
        CFG["stop_failures"] = 1
        plugin._on_toggled(False)                           # aucune exception
        assert len(critical()) == 1
        assert pushes("Serveur arrêté") == []


def test_plugin_reentrant_stop_is_refused():
    with plugin_env() as plugin:
        plugin._start_bridge()
        bridge = plugin._bridge
        inner = []

        def reenter():
            try:
                plugin._stop_bridge()
            except RuntimeError as exc:
                inner.append(str(exc))

        CFG["stop_hook"] = reenter
        plugin._stop_bridge()
        assert inner == ["Un arrêt du pont est déjà en cours."]
        assert bridge.events == ["start", "stop", "deleteLater"]
        assert plugin._bridge is None and plugin._bridge_stop_in_progress is False


def test_plugin_unload_continues_and_keeps_errors():
    with plugin_env() as plugin:
        plugin._start_bridge()
        bridge = plugin._bridge
        EVENTS.clear()
        CFG["stop_failures"] = 99
        plugin.unload()
        assert any(f.startswith("arrêt du pont") for f in plugin._unload_failures)
        assert ("removeToolBarIcon",) in EVENTS and ("removePluginMenu",) in EVENTS
        assert ("remove", bridge.token, True) in EVENTS
        assert pushes() == []                               # aucune notification
        assert plugin._bridge is bridge and plugin._action is None
        count = len(EVENTS)
        plugin.unload()
        assert len(EVENTS) == count                         # second unload sans effet


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in list(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
        else:
            print(f"PASS {name}")
    print(f"{len(tests) - failed} réussis, {failed} échoués")
    sys.exit(1 if failed else 0)
