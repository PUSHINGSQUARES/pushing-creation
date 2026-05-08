"""Gemini Flash image generation + Veo 3 video via Google AI Studio API."""
from __future__ import annotations
import base64
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

from .base import Provider, GenRequest, GenResult
from ..scrub import scrub

_BASE = "https://generativelanguage.googleapis.com/v1beta"
_IMAGE_MODEL = "gemini-2.0-flash-preview-image-generation"
_VIDEO_MODEL = "veo-2.0-generate-001"


def _api(path: str, payload: dict | None, api_key: str) -> dict:
    url = f"{_BASE}/{path}?key={api_key}"
    if payload is not None:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"Gemini HTTP {e.code}: {body}") from None


class GeminiProvider(Provider):
    name = "gemini"
    supports_image = True
    supports_video = True
    keychain_service = "pushing-creation:gemini"

    def generate_image(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        ar_map = {
            "1:1": "1:1", "16:9": "16:9", "9:16": "9:16",
            "4:3": "4:3", "3:4": "3:4",
        }
        aspect = ar_map.get(req.aspect_ratio, "16:9")
        payload = {
            "contents": [{"parts": [{"text": req.prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imagenConfig": {"aspectRatio": aspect},
            },
        }
        if req.negative_prompt:
            payload["generationConfig"]["imagenConfig"]["negativePrompt"] = req.negative_prompt

        resp = _api(f"models/{_IMAGE_MODEL}:generateContent", payload, api_key)
        # Extract inline image data
        parts = resp.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        img_data = None
        mime = "image/png"
        for part in parts:
            if "inlineData" in part:
                img_data = base64.b64decode(part["inlineData"]["data"])
                mime = part["inlineData"].get("mimeType", mime)
                break
        if img_data is None:
            raise RuntimeError(f"No image data in response: {scrub(str(resp))}")

        ext = "jpg" if "jpeg" in mime else "png"
        out = req.out_path.with_suffix(f".{ext}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(img_data)
        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": _IMAGE_MODEL, "mime": mime},
        )

    def generate_video(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        ar_map = {"16:9": "16:9", "9:16": "9:16", "1:1": "1:1"}
        aspect = ar_map.get(req.aspect_ratio, "16:9")
        payload = {
            "model": _VIDEO_MODEL,
            "prompt": req.prompt,
            "config": {"aspectRatio": aspect, "numberOfVideos": 1},
        }
        resp = _api("models/veo-2.0-generate-001:predictLongRunning", payload, api_key)
        operation_name = resp.get("name", "")
        if not operation_name:
            raise RuntimeError(f"No operation name in Veo response: {scrub(str(resp))}")

        # Poll until done
        for _ in range(120):
            time.sleep(5)
            status = _api(f"operations/{operation_name.split('/')[-1]}", {}, api_key)
            if status.get("done"):
                break
        else:
            raise RuntimeError("Veo generation timed out after 10 minutes")

        error = status.get("error")
        if error:
            raise RuntimeError(f"Veo error: {scrub(str(error))}")

        videos = (status.get("response") or {}).get("generatedSamples", [])
        if not videos:
            raise RuntimeError(f"No video in Veo response: {scrub(str(status))}")

        video_uri = videos[0].get("video", {}).get("uri", "")
        if not video_uri:
            raise RuntimeError("No video URI in Veo response")

        # Download video
        dl_req = urllib.request.Request(f"{video_uri}&key={api_key}")
        out = req.out_path.with_suffix(".mp4")
        out.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(dl_req, timeout=300) as resp_dl:
            out.write_bytes(resp_dl.read())

        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": _VIDEO_MODEL},
        )

    def ping(self, api_key: str) -> bool:
        try:
            _api("models", None, api_key)
        except Exception:
            return False
        return True
