"""Tests for scrub.py. Fake key strings are split across concatenation to avoid
triggering the pre-push key-leak scan on literal patterns."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.scrub import scrub

# Fake key fragments combined at runtime to avoid literal key patterns in source.
_OPENAI_FAKE = "sk-" + "abcdefghijklmnopqrstuvwxyz1234567890"
_ANTHROPIC_FAKE = "sk-ant-" + "api03-abcdefghijklmnopqrstuvwxyz12345678"
_GOOGLE_FAKE = "AIza" + "SyAbcdefghijklmnopqrstuvwxyz12345"
_VOLC_FAKE = "volc_" + "abcdefghijklmnopqrstuvwxyz"


def test_scrub_openai_key():
    text = f"Authorization: Bearer {_OPENAI_FAKE}"
    result = scrub(text)
    assert _OPENAI_FAKE not in result


def test_scrub_anthropic_key():
    text = f"key={_ANTHROPIC_FAKE}"
    result = scrub(text)
    assert _ANTHROPIC_FAKE not in result


def test_scrub_google_key():
    text = f"Authorization: {_GOOGLE_FAKE}"
    result = scrub(text)
    assert _GOOGLE_FAKE not in result


def test_scrub_volc_key():
    text = f"api_key={_VOLC_FAKE}"
    result = scrub(text)
    assert _VOLC_FAKE not in result


def test_scrub_passthrough():
    text = "Hello, world! This is a normal message."
    assert scrub(text) == text


def test_scrub_short_string_passthrough():
    text = "status: ok"
    assert scrub(text) == text


def test_scrub_redact_marker_present():
    text = f"token={_OPENAI_FAKE}extra"
    result = scrub(text)
    assert "[REDACTED:" in result
