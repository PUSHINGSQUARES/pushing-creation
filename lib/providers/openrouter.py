"""OpenRouter pass-through provider for image generation."""
from __future__ import annotations
import base64
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

from .base import Provider, GenRequest, GenResult
from ..scrub import scrub

_BASE = "https://openrouter.ai/api/v1"
_DEFAULT_IMAGE_MODEL = "google/gemini-2.5-flash-image"


def _api(path: str, payload: dict, api_key: str) -> dict:
    url = f"{_BASE}/{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/PUSHINGSQUARES/pushing-creation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"OpenRouter HTTP {e.code}: {body}") from None


def _get(path: str, api_key: str) -> dict:
    url = f"{_BASE}/{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/PUSHINGSQUARES/pushing-creation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"OpenRouter HTTP {e.code}: {body}") from None


class OpenRouterProvider(Provider):
    name = "openrouter"
    supports_image = True
    supports_video = False
    keychain_service = "pushing-creation:openrouter"

    def generate_image(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        model = req.extras.get("model", _DEFAULT_IMAGE_MODEL)
        prompt = req.prompt
        if req.negative_prompt:
            prompt = f"{prompt} --no {req.negative_prompt}"

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = _api("chat/completions", payload, api_key)
        msg = (resp.get("choices") or [{}])[0].get("message", {})
        content = msg.get("content", "")
        images = msg.get("images") or []

        out = req.out_path.with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)

        def _save_img_url(url_str: str) -> None:
            if url_str.startswith("data:"):
                _, b64 = url_str.split(",", 1)
                out.write_bytes(base64.b64decode(b64))
            else:
                with urllib.request.urlopen(url_str, timeout=120) as dl:
                    out.write_bytes(dl.read())

        # Some models return images in the dedicated 'images' field
        if images:
            first = images[0]
            if isinstance(first, dict) and first.get("type") == "image_url":
                _save_img_url(first["image_url"]["url"])
            elif isinstance(first, str):
                _save_img_url(first)
            else:
                raise RuntimeError(f"Unexpected OpenRouter images format: {scrub(str(first)[:200])}")
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "image_url":
                    _save_img_url(part["image_url"].get("url", ""))
                    break
            else:
                raise RuntimeError(f"No image_url part in OpenRouter content list")
        elif isinstance(content, str) and content.startswith("http"):
            _save_img_url(content.strip())
        else:
            raise RuntimeError(f"Unexpected OpenRouter response format: {scrub(str(content)[:200])}")

        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": model},
        )

    def generate_video(self, req: GenRequest, api_key: str) -> GenResult:
        raise NotImplementedError("OpenRouter video generation not supported in this build")

    def ping(self, api_key: str) -> bool:
        try:
            resp = _get("auth/key", api_key)
            return bool(resp.get("data"))
        except Exception:
            return False
