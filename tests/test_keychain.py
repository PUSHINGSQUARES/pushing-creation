"""Unit tests for keychain.py — mocks the security subprocess, never calls real Keychain."""
import sys
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import keychain


def _mock_run(stdout: bytes, returncode: int = 0):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = b""
    return m


# ---------------------------------------------------------------------------
# Low-level get() / has() / list_services() — unchanged behaviour
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Hybrid get_key() — primary first, fallback second
# ---------------------------------------------------------------------------

def test_get_key_primary_hit(monkeypatch):
    calls: list = []

    def mock_run(cmd, **kwargs):
        calls.append(list(cmd))
        return _mock_run(b"primarykey\n", returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = keychain.get_key("gemini")
    assert result == "primarykey"
    # Only one subprocess call — primary succeeded, fallback never tried
    assert len(calls) == 1
    assert "com.shadow.control" in calls[0]
    assert "apiKey_gemini" in calls[0]


def test_get_key_primary_miss_fallback_hit(monkeypatch):
    call_count = [0]

    def mock_run(cmd, **kwargs):
        call_count[0] += 1
        if "com.shadow.control" in cmd:
            return _mock_run(b"", returncode=44)
        return _mock_run(b"legacykey\n", returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = keychain.get_key("openrouter")
    assert result == "legacykey"
    # Two subprocess calls: primary (fail) then fallback (success)
    assert call_count[0] == 2


def test_get_key_both_miss_returns_none(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(b"", returncode=44))
    result = keychain.get_key("unknown")
    assert result is None


def test_get_key_primary_empty_falls_to_fallback(monkeypatch):
    call_count = [0]

    def mock_run(cmd, **kwargs):
        call_count[0] += 1
        if "com.shadow.control" in cmd:
            return _mock_run(b"\n", returncode=0)  # empty value returned
        return _mock_run(b"fallbackkey\n", returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = keychain.get_key("test")
    assert result == "fallbackkey"
    assert call_count[0] == 2


# ---------------------------------------------------------------------------
# has_key() — union of both schemes
# ---------------------------------------------------------------------------

def test_has_key_primary_hit(monkeypatch):
    def mock_run(cmd, **kwargs):
        if "com.shadow.control" in cmd:
            return _mock_run(b"ok", returncode=0)
        return _mock_run(b"", returncode=44)

    monkeypatch.setattr(subprocess, "run", mock_run)
    assert keychain.has_key("gemini") is True


def test_has_key_fallback_hit(monkeypatch):
    call_count = [0]

    def mock_run(cmd, **kwargs):
        call_count[0] += 1
        if "com.shadow.control" in cmd:
            return _mock_run(b"", returncode=44)
        return _mock_run(b"ok", returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    assert keychain.has_key("openrouter") is True
    assert call_count[0] == 2


def test_has_key_both_miss(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(b"", returncode=44))
    assert keychain.has_key("noprovider") is False


# ---------------------------------------------------------------------------
# set_key() — writes to primary scheme only
# ---------------------------------------------------------------------------

def test_set_key_writes_to_primary(monkeypatch):
    captured: list = []

    def mock_run(cmd, **kwargs):
        captured.append(list(cmd))
        return _mock_run(b"", returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    keychain.set_key("newprovider", "sk-test123")

    assert len(captured) == 1
    cmd = captured[0]
    assert "com.shadow.control" in cmd
    assert "apiKey_newprovider" in cmd
    assert "sk-test123" in cmd


def test_set_key_does_not_use_legacy_scheme(monkeypatch):
    captured: list = []

    def mock_run(cmd, **kwargs):
        captured.append(list(cmd))
        return _mock_run(b"", returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    keychain.set_key("gemini", "AIzaXXXX")

    cmd = captured[0]
    assert "pushing-creation:gemini" not in cmd
    assert "com.shadow.control" in cmd


# ---------------------------------------------------------------------------
# list_providers() — union of both schemes
# ---------------------------------------------------------------------------

def test_list_providers_primary_and_legacy(monkeypatch):
    dump = b'''keychain: "/Users/thor/Library/Keychains/login.keychain-db"
version: 512
class: "genp"
attributes:
    "svce"<blob>="com.shadow.control"
    "acct"<blob>="apiKey_gemini"
class: "genp"
attributes:
    "svce"<blob>="com.shadow.control"
    "acct"<blob>="apiKey_openai"
class: "genp"
attributes:
    "svce"<blob>="pushing-creation:kling"
    "acct"<blob>="thor"
class: "genp"
attributes:
    "svce"<blob>="other-app:something"
    "acct"<blob>="user"
'''
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(dump))
    providers = keychain.list_providers()
    assert "gemini" in providers
    assert "openai" in providers
    assert "kling" in providers
    assert "something" not in providers


def test_list_providers_deduplicates(monkeypatch):
    dump = b'''class: "genp"
attributes:
    "svce"<blob>="com.shadow.control"
    "acct"<blob>="apiKey_gemini"
class: "genp"
attributes:
    "svce"<blob>="pushing-creation:gemini"
    "acct"<blob>="thor"
'''
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _mock_run(dump))
    providers = keychain.list_providers()
    assert providers.count("gemini") == 1


# ---------------------------------------------------------------------------
# remove_key() — removes from both schemes
# ---------------------------------------------------------------------------

def test_remove_key_removes_both(monkeypatch):
    captured: list = []

    def mock_run(cmd, **kwargs):
        captured.append(list(cmd))
        return _mock_run(b"", returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = keychain.remove_key("gemini")

    assert result["primary"] is True
    assert result["fallback"] is True
    assert len(captured) == 2
    cmds_flat = [" ".join(c) for c in captured]
    assert any("com.shadow.control" in c for c in cmds_flat)
    assert any("pushing-creation:gemini" in c for c in cmds_flat)


def test_remove_key_reports_which_were_removed(monkeypatch):
    def mock_run(cmd, **kwargs):
        if "com.shadow.control" in cmd:
            return _mock_run(b"", returncode=0)
        return _mock_run(b"", returncode=44)  # fallback not found

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = keychain.remove_key("gemini")
    assert result["primary"] is True
    assert result["fallback"] is False
