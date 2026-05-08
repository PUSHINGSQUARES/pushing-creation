"""Unit tests for keychain.py — mocks the security subprocess, never calls real Keychain."""
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import keychain


def _mock_run(stdout: bytes, returncode: int = 0):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = b""
    return m


def test_get_returns_value(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(b"mysecretvalue\n"))
    result = keychain.get("pushing-creation:test")
    assert result == "mysecretvalue"


def test_get_returns_none_on_failure(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(b"", returncode=44))
    result = keychain.get("pushing-creation:missing")
    assert result is None


def test_has_returns_true(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(b"ok", returncode=0))
    assert keychain.has("pushing-creation:gemini") is True


def test_has_returns_false(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(b"", returncode=44))
    assert keychain.has("pushing-creation:missing") is False


def test_get_empty_string_returns_none(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(b"\n"))
    result = keychain.get("pushing-creation:empty")
    assert result is None


def test_list_services_parses_output(monkeypatch):
    dump = b'''keychain: "/Users/thor/Library/Keychains/login.keychain-db"
version: 512
class: "genp"
attributes:
    "svce"<blob>="pushing-creation:gemini"
    "acct"<blob>="pushing-creation"
class: "genp"
attributes:
    "svce"<blob>="pushing-creation:openai"
    "acct"<blob>="pushing-creation"
class: "genp"
attributes:
    "svce"<blob>="other-app:something"
    "acct"<blob>="user"
'''
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(dump))
    services = keychain.list_services("pushing-creation:")
    assert "pushing-creation:gemini" in services
    assert "pushing-creation:openai" in services
    assert "other-app:something" not in services
