import json

import pytest

from cynogis.bridge.protocol import PROTOCOL_VERSION, decode_request
from cynogis.core.audit import AuditLog
from cynogis.core.dispatcher import Dispatcher, ToolResult
from cynogis.core.errors import ErrorCode, ToolError
from cynogis.core.policy import PermissionPolicy
from cynogis.core.registry import Level, ToolRegistry, tool
from cynogis.core.schema import Param


def _req(method, **params):
    raw = {"v": PROTOCOL_VERSION, "id": "1", "method": method, "params": params, "token": "t"}
    return decode_request(json.dumps(raw).encode())


@tool(level=Level.READ, params={"n": Param("integer", "Nombre")})
def double(n):
    """Double n."""
    return ToolResult({"value": n * 2}, ["attention"], outputs=["couche_1"])


@tool(level=Level.READ)
def crash():
    """Plante."""
    return 1 / 0


@tool(level=Level.READ)
def metier():
    """Erreur métier."""
    raise ToolError(ErrorCode.LAYER_NOT_FOUND, "absente")


@tool(level=Level.DESTROY)
def supprimer():
    """Action irréversible."""
    return "fait"


def make(tmp_path, confirm=None, max_level=Level.DESTROY):
    registry = ToolRegistry()
    registry.register(double, crash, metier, supprimer)
    audit = AuditLog(tmp_path)
    return Dispatcher(registry, PermissionPolicy(max_level, confirm), audit), audit


def test_success_is_audited(tmp_path):
    d, audit = make(tmp_path)
    resp = d.dispatch(_req("double", n=21))
    assert resp.ok and resp.data == {"value": 42} and resp.warnings == ["attention"]
    entry = audit.recent(1)[0]
    assert resp.audit_id == entry["audit_id"] and entry["outputs"] == ["couche_1"]


@pytest.mark.parametrize("method, params, code", [
    ("double", {"n": "x"}, "INVALID_PARAMS"),
    ("inconnu", {}, "UNKNOWN_METHOD"),
    ("crash", {}, "INTERNAL_ERROR"),
    ("metier", {}, "LAYER_NOT_FOUND"),
    ("supprimer", {}, "PERMISSION_DENIED"),  # aucun confirmateur → refus
])
def test_errors(tmp_path, method, params, code):
    d, _ = make(tmp_path)
    resp = d.dispatch(_req(method, **params))
    assert not resp.ok and resp.error["code"] == code


def test_destroy_with_confirmation(tmp_path):
    d, _ = make(tmp_path, confirm=lambda spec, params: True)
    assert d.dispatch(_req("supprimer")).ok


def test_max_level_blocks(tmp_path):
    d, _ = make(tmp_path, confirm=lambda s, p: True, max_level=Level.CREATE)
    assert d.dispatch(_req("supprimer")).error["code"] == "PERMISSION_DENIED"


def test_list_tools_hides_internal(tmp_path):
    d, _ = make(tmp_path)
    names = [t["name"] for t in d.dispatch(_req("list_tools")).data["tools"]]
    assert "list_tools" not in names and {"double", "get_audit_log"} <= set(names)


def test_decorator_checks():
    with pytest.raises(ValueError, match="docstring"):
        tool(level=Level.READ)(lambda: None)
    with pytest.raises(ValueError, match="signature"):
        @tool(level=Level.READ, params={"a": Param("string", "a")})
        def f(b):
            """Doc."""


def test_register_module_without_tools_fails():
    import types

    with pytest.raises(ValueError):
        ToolRegistry().register_module(types.ModuleType("vide"))
