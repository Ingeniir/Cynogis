"""remove_connection_file sur de vrais fichiers temporaires (jamais le fichier de l'utilisateur)."""
import json
from pathlib import Path

import pytest

from cynogis.bridge import connection


@pytest.fixture
def conn_file(tmp_path, monkeypatch):
    path = tmp_path / "connection.json"
    monkeypatch.setattr(connection, "CONNECTION_FILE", path)
    return path


def write(path, payload):
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload),
                    encoding="utf-8")


def test_removes_own_file(conn_file):
    connection.write_connection_file("127.0.0.1", 1234, "mine")
    connection.remove_connection_file("mine")
    assert not conn_file.exists()


def test_strict_removes_own_file(conn_file):
    write(conn_file, {"token": "mine"})
    connection.remove_connection_file("mine", strict=True)
    assert not conn_file.exists()


@pytest.mark.parametrize("strict", [False, True])
def test_missing_file_is_accepted(conn_file, strict):
    connection.remove_connection_file("mine", strict=strict)
    assert not conn_file.exists()


@pytest.mark.parametrize("strict", [False, True])
def test_other_instance_file_is_kept(conn_file, strict):
    write(conn_file, {"token": "other", "port": 9})
    connection.remove_connection_file("mine", strict=strict)
    assert json.loads(conn_file.read_text(encoding="utf-8"))["token"] == "other"


@pytest.mark.parametrize("payload", ["{pas du json", "[1, 2]"])
def test_invalid_json_ignored_by_default(conn_file, payload):
    write(conn_file, payload)
    connection.remove_connection_file("mine")
    assert conn_file.read_text(encoding="utf-8") == payload


@pytest.mark.parametrize("payload", ["{pas du json", "[1, 2]"])
def test_invalid_json_raises_in_strict_mode(conn_file, payload):
    write(conn_file, payload)
    with pytest.raises(ValueError):
        connection.remove_connection_file("mine", strict=True)
    assert conn_file.read_text(encoding="utf-8") == payload


def _deny_unlink(monkeypatch, target):
    real_unlink = Path.unlink

    def unlink(self, *args, **kwargs):
        if self == target:
            raise PermissionError(13, "Accès refusé (simulé)", str(self))
        return real_unlink(self, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", unlink)


def test_permission_error_on_delete_is_silent_by_default(conn_file, monkeypatch):
    write(conn_file, {"token": "mine"})
    _deny_unlink(monkeypatch, conn_file)
    connection.remove_connection_file("mine")
    assert conn_file.exists()


def test_permission_error_on_delete_raises_in_strict_mode(conn_file, monkeypatch):
    write(conn_file, {"token": "mine"})
    _deny_unlink(monkeypatch, conn_file)
    with pytest.raises(PermissionError):
        connection.remove_connection_file("mine", strict=True)
    assert conn_file.exists()


def test_permission_error_on_read_raises_in_strict_mode(conn_file, monkeypatch):
    write(conn_file, {"token": "mine"})
    real_read = Path.read_text

    def read_text(self, *args, **kwargs):
        if self == conn_file:
            raise PermissionError(13, "Lecture refusée (simulée)", str(self))
        return real_read(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    connection.remove_connection_file("mine")  # historique : silencieux
    with pytest.raises(PermissionError):
        connection.remove_connection_file("mine", strict=True)
    assert conn_file.exists()
