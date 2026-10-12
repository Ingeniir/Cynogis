from __future__ import annotations

from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    PROTOCOL_ERROR = "PROTOCOL_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    UNKNOWN_METHOD = "UNKNOWN_METHOD"
    INVALID_PARAMS = "INVALID_PARAMS"
    LAYER_NOT_FOUND = "LAYER_NOT_FOUND"
    CRS_GEOGRAPHIC = "CRS_GEOGRAPHIC"
    INVALID_GEOMETRY = "INVALID_GEOMETRY"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    ALGORITHM_NOT_ALLOWED = "ALGORITHM_NOT_ALLOWED"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    READ_ONLY = "READ_ONLY"
    EDIT_FAILED = "EDIT_FAILED"
    PENDING_EDITS = "PENDING_EDITS"
    TOO_MANY_FEATURES = "TOO_MANY_FEATURES"
    COMMIT_FAILED = "COMMIT_FAILED"
    WRITE_FAILED = "WRITE_FAILED"
    NETWORK_ERROR = "NETWORK_ERROR"
    EXECUTION_FAILED = "EXECUTION_FAILED"

class ToolError(Exception):
    """Erreur « métier » renvoyée à l'IA avec un code exploitable."""

    def __init__(self, code: ErrorCode, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code.value, "message": self.message, "details": self.details}
