"""OpenAI GPT-image-1 image generation."""
from __future__ import annotations
import base64
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

from .base import Provider, GenRequest, GenResult
from ..scrub import scrub

_BASE = "https://api.openai.com/v1"
_IMAGE_MODEL = "gpt-image-1"


def _api(path: str, payload: dict, api_key: str) -> dict:
    url = f"{_BASE}/{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"OpenAI HTTP {e.code}: {body}") from None


def _get(path: str, api_key: str) -> dict:
    url = f"{_BASE}/{path}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"OpenAI HTTP {e.code}: {body}") from None


class OpenAIProvider(Provider):
    name = "openai"
    supports_image = True
    supports_video = False
    keychain_service = "pushing-creation:openai"

    def generate_image(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        # gpt-image-1 supports 1024x1024, 1536x1024, 1024x1536, auto
        size_map = {
            "1:1": "1024x1024",
            "16:9": "1536x1024",
            "9:16": "1024x1536",
            "4:3": "1536x1024",
        }
        size = size_map.get(req.aspect_ratio, "1024x1024")
        prompt = req.prompt
        if req.negative_prompt:
            prompt = f"{prompt}\n\nAvoid: {req.negative_prompt}"

        payload = {
            "model": _IMAGE_MODEL,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "output_format": "png",
        }
        resp = _api("images/generations", payload, api_key)
        img_item = (resp.get("data") or [{}])[0]
        b64 = img_item.get("b64_json") or img_item.get("b64")
        url_val = img_item.get("url")

        out = req.out_path.with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)

        if b64:
            out.write_bytes(base64.b64decode(b64))
        elif url_val:
            with urllib.request.urlopen(url_val, timeout=120) as dl:
                out.write_bytes(dl.read())
        else:
            raise RuntimeError(f"No image data in OpenAI response: {scrub(str(resp))}")

        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": _IMAGE_MODEL, "size": size},
        )

    def generate_video(self, req: GenRequest, api_key: str) -> GenResult:
        raise NotImplementedError("OpenAI does not support video generation")

    def ping(self, api_key: str) -> bool:
        try:
            _get("models", api_key)
        except Exception:
            return False
        return True
