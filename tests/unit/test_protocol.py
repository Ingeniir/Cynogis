import json

import pytest

from cynogis.bridge.protocol import PROTOCOL_VERSION, decode_request
from cynogis.core.dispatcher import Dispatcher, ToolResult
from cynogis.core.errors import ErrorCode, ToolError


def _line(**overrides) -> bytes:
    base = {"v": PROTOCOL_VERSION, "id": "1", "method": "ping", "params": {}, "token": "t"}
    base.update(overrides)
    return json.dumps(base).encode()


def _request(method="ping", params=None):
    return decode_request(_line(method=method, params=params or {}))


def test_decode_valid():
    req = decode_request(_line(params={"a": 1}))
    assert (req.id, req.method, req.params, req.token) == ("1", "ping", {"a": 1}, "t")


@pytest.mark.parametrize("raw", [b"pas du json", b"[]", _line(v=99), _line(id=""),
                                 _line(method=None), _line(params=[])])
def test_decode_invalid(raw):
    with pytest.raises(ToolError) as exc:
        decode_request(raw)
    assert exc.value.code is ErrorCode.PROTOCOL_ERROR


def test_missing_token_is_unauthorized():
    with pytest.raises(ToolError) as exc:
        decode_request(_line(token=None))
    assert exc.value.code is ErrorCode.UNAUTHORIZED


def test_dispatch_success_with_warnings():
    d = Dispatcher()
    d.register("ping", lambda p: ToolResult({"pong": True}, ["attention"]))
    payload = json.loads(d.dispatch(_request()).encode())
    assert payload["ok"] and payload["data"] == {"pong": True}
    assert payload["warnings"] == ["attention"]


def test_dispatch_plain_return_is_ok():
    d = Dispatcher()
    d.register("ping", lambda p: {"pong": True})
    payload = json.loads(d.dispatch(_request()).encode())
    assert payload["ok"] and payload["data"] == {"pong": True}


def test_dispatch_unknown_method():
    resp = Dispatcher().dispatch(_request("inconnue"))
    assert not resp.ok and resp.error["code"] == "UNKNOWN_METHOD"


def test_dispatch_tool_error_and_crash():
    d = Dispatcher()

    def boom(_):
        raise ToolError(ErrorCode.LAYER_NOT_FOUND, "absente")

    d.register("metier", boom)
    d.register("crash", lambda p: 1 / 0)
    assert d.dispatch(_request("metier")).error["code"] == "LAYER_NOT_FOUND"
    assert d.dispatch(_request("crash")).error["code"] == "INTERNAL_ERROR"


def test_register_twice_fails():
    d = Dispatcher()
    d.register("x", lambda p: None)
    with pytest.raises(ValueError):
        d.register("x", lambda p: None)
