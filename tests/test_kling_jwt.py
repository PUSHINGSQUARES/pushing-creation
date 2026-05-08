"""Unit tests for Kling JWT generation — deterministic with fixed timestamp."""
import base64
import hashlib
import hmac
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.providers.kling import _kling_jwt, _b64url, _parse_key


def _decode_b64url(s: str) -> bytes:
    pad = 4 - len(s) % 4
    if pad != 4:
        s += "=" * pad
    return base64.urlsafe_b64decode(s)


def test_b64url_no_padding():
    result = _b64url(b"hello")
    assert "=" not in result


def test_parse_key_valid():
    ak, sk = _parse_key("AKTEST123:secretXYZ")
    assert ak == "AKTEST123"
    assert sk == "secretXYZ"


def test_parse_key_secret_with_colon():
    ak, sk = _parse_key("AK:sec:ret")
    assert ak == "AK"
    assert sk == "sec:ret"


def test_parse_key_invalid():
    import pytest
    with pytest.raises(ValueError, match="access_key:secret_key"):
        _parse_key("nokeyformat")


def test_jwt_structure():
    with patch("lib.providers.kling.time.time", return_value=1_700_000_000):
        token = _kling_jwt("AKTEST", "sekrit")

    parts = token.split(".")
    assert len(parts) == 3, "JWT must have header.payload.signature"

    header = json.loads(_decode_b64url(parts[0]))
    assert header == {"alg": "HS256", "typ": "JWT"}

    payload = json.loads(_decode_b64url(parts[1]))
    assert payload["iss"] == "AKTEST"
    assert payload["exp"] == 1_700_000_000 + 1800
    assert payload["nbf"] == 1_700_000_000 - 5


def test_jwt_signature_correct():
    with patch("lib.providers.kling.time.time", return_value=1_700_000_000):
        token = _kling_jwt("AKTEST", "sekrit")

    parts = token.split(".")
    signing_input = f"{parts[0]}.{parts[1]}".encode()
    expected_sig = _b64url(
        hmac.new("sekrit".encode(), signing_input, hashlib.sha256).digest()
    )
    assert parts[2] == expected_sig


def test_jwt_deterministic_at_fixed_time():
    with patch("lib.providers.kling.time.time", return_value=1_700_000_000):
        t1 = _kling_jwt("AK1", "SK1")
        t2 = _kling_jwt("AK1", "SK1")
    assert t1 == t2


def test_jwt_different_keys_produce_different_tokens():
    with patch("lib.providers.kling.time.time", return_value=1_700_000_000):
        t1 = _kling_jwt("AK1", "SK1")
        t2 = _kling_jwt("AK2", "SK2")
    assert t1 != t2
