import json

import pytest

from cynogis.bridge.protocol import PROTOCOL_VERSION, Response, decode_request
from cynogis.core.errors import ErrorCode, ToolError


def _line(**overrides) -> bytes:
    base = {"v": PROTOCOL_VERSION, "id": "1", "method": "ping", "params": {}, "token": "t"}
    base.update(overrides)
    return json.dumps(base).encode()


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


def test_response_encode_has_audit_id():
    payload = json.loads(Response(id="1", ok=True, data={}, audit_id="x").encode())
    assert payload["audit_id"] == "x" and payload["ok"] is True
