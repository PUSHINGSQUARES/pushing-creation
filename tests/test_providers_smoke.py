"""Provider smoke tests using real Keychain entries.

These tests require Ari's Keychain entries to be populated.
Run with: python3 -m pytest tests/test_providers_smoke.py -v

Tests that find no Keychain entry will skip automatically.
"""
import sys
import os
import time
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import keychain
from lib.providers import REGISTRY, get_provider
from lib.providers.base import GenRequest

_TEST_PROMPT = (
    "a single ripe peach on a clean linen surface, "
    "soft window light from frame left, shallow depth of field"
)
_ASPECT = "1:1"
_TEST_DIR = Path(tempfile.gettempdir()) / f"pc-test-{int(time.time())}"


def _req(provider_name: str, kind: str) -> GenRequest:
    _TEST_DIR.mkdir(parents=True, exist_ok=True)
    out = _TEST_DIR / f"{provider_name}-{kind}"
    return GenRequest(
        prompt=_TEST_PROMPT,
        negative_prompt=None,
        refs=[],
        aspect_ratio=_ASPECT,
        out_path=out,
        extras={},
    )


def _get_key(provider_name: str):
    return keychain.get_key(provider_name)


@pytest.mark.parametrize("provider_name", ["gemini", "openai", "openrouter", "imagen"])
def test_image_generation(provider_name):
    api_key = _get_key(provider_name)
    if api_key is None:
        pytest.skip(f"No Keychain entry for pushing-creation:{provider_name}")

    p = get_provider(provider_name)
    if not p.supports_image:
        pytest.skip(f"{provider_name} does not support image generation")

    req = _req(provider_name, "image")
    try:
        result = p.generate_image(req, api_key)
    except (NotImplementedError, ValueError) as e:
        pytest.skip(str(e))

    assert result.out_path.exists(), f"Output file not created: {result.out_path}"
    assert result.out_path.stat().st_size > 10_000, "Output file too small (< 10KB)"
    # Check PNG or JPEG header
    header = result.out_path.read_bytes()[:4]
    assert header[:2] in (b"\xff\xd8", b"\x89PNG"[:2]), f"Not a valid image: {header!r}"
    # Cleanup
    result.out_path.unlink(missing_ok=True)


@pytest.mark.parametrize("provider_name", ["gemini", "kling", "seedance"])
def test_video_generation(provider_name):
    api_key = _get_key(provider_name)
    if api_key is None:
        pytest.skip(f"No Keychain entry for pushing-creation:{provider_name}")

    p = get_provider(provider_name)
    if not p.supports_video:
        pytest.skip(f"{provider_name} does not support video generation")

    req = _req(provider_name, "video")
    req.extras["duration"] = "5"
    try:
        result = p.generate_video(req, api_key)
    except (NotImplementedError, ValueError) as e:
        pytest.skip(str(e))

    assert result.out_path.exists(), f"Output file not created: {result.out_path}"
    assert result.out_path.stat().st_size > 50_000, "Video file too small (< 50KB)"
    # Check MP4 header (ftyp box)
    header = result.out_path.read_bytes()[:12]
    assert b"ftyp" in header or header[:4] == b"\x00\x00\x00\x1c", f"Not a valid MP4: {header!r}"
    result.out_path.unlink(missing_ok=True)


@pytest.mark.parametrize("provider_name", ["seedream"])
def test_seedream_image(provider_name):
    api_key = _get_key(provider_name)
    if api_key is None:
        pytest.skip(f"No Keychain entry for pushing-creation:{provider_name}")

    p = get_provider(provider_name)
    req = _req(provider_name, "image")
    try:
        result = p.generate_image(req, api_key)
    except (NotImplementedError, ValueError) as e:
        pytest.skip(str(e))

    assert result.out_path.exists()
    assert result.out_path.stat().st_size > 10_000
    result.out_path.unlink(missing_ok=True)


@pytest.mark.parametrize("provider_name", list(REGISTRY.keys()))
def test_ping(provider_name):
    api_key = _get_key(provider_name)
    if api_key is None:
        pytest.skip(f"No Keychain entry for pushing-creation:{provider_name}")

    p = get_provider(provider_name)
    try:
        ok = p.ping(api_key)
    except NotImplementedError:
        pytest.skip(f"{provider_name} ping not implemented")
    assert ok, f"{provider_name} ping failed — key may be invalid"
