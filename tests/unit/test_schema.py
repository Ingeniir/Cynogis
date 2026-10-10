import pytest

from cynogis.core.errors import ErrorCode, ToolError
from cynogis.core.schema import Param, object_schema, validate_params

SPEC = {
    "layer_id": Param("string", "Couche"),
    "limit": Param("integer", "Max", required=False, default=50, minimum=1, maximum=500),
    "mode": Param("string", "Mode", required=False, default="all", enum=("all", "vector")),
    "fields": Param("array", "Champs", required=False, items="string"),
}


def test_defaults_applied():
    assert validate_params(SPEC, {"layer_id": "a"}) == {
        "layer_id": "a", "limit": 50, "mode": "all", "fields": None}


def test_integer_float_coerced():
    assert validate_params(SPEC, {"layer_id": "a", "limit": 10.0})["limit"] == 10


@pytest.mark.parametrize("raw, fragment", [
    ({}, "layer_id : paramètre obligatoire"),
    ({"layer_id": 3}, "type string attendu"),
    ({"layer_id": "a", "limit": 0}, "minimum"),
    ({"layer_id": "a", "limit": True}, "type integer attendu"),
    ({"layer_id": "a", "mode": "x"}, "non autorisée"),
    ({"layer_id": "a", "fields": ["ok", 2]}, "éléments"),
    ({"layer_id": "a", "oops": 1}, "inconnus"),
])
def test_invalid(raw, fragment):
    with pytest.raises(ToolError) as exc:
        validate_params(SPEC, raw)
    assert exc.value.code is ErrorCode.INVALID_PARAMS
    assert fragment in exc.value.message


def test_object_schema():
    schema = object_schema(SPEC)
    assert schema["required"] == ["layer_id"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["fields"]["items"] == {"type": "string"}

def test_items_enum():
    spec = {"metrics": Param("array", "M", items="string", items_enum=("area", "length"))}
    assert validate_params(spec, {"metrics": ["area"]}) == {"metrics": ["area"]}
    with pytest.raises(ToolError, match="non autorisées"):
        validate_params(spec, {"metrics": ["volume"]})
    assert object_schema(spec)["properties"]["metrics"]["items"]["enum"] == ["area", "length"]
