import json

from cynogis.core.audit import MAX_PARAMS_CHARS, AuditLog


def test_writes_jsonl_and_filters(tmp_path):
    audit = AuditLog(tmp_path)
    audit.record(tool="a", level=0, params={}, ok=True, duration_ms=1)
    audit.record(tool="b", level=1, params={"x": 1}, ok=False, duration_ms=2, error_code="E")
    lines = next(tmp_path.glob("*.jsonl")).read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["tool"] for line in lines] == ["a", "b"]
    assert [e["tool"] for e in audit.recent()] == ["b", "a"]
    assert [e["tool"] for e in audit.recent(tool="a")] == ["a"]


def test_long_params_truncated(tmp_path):
    audit = AuditLog(None)
    audit.record(tool="a", level=0, params={"wkt": "x" * 10_000}, ok=True, duration_ms=1)
    assert len(audit.recent(1)[0]["params"]["_truncated"]) == MAX_PARAMS_CHARS
