"""Google Imagen via Vertex AI API.

Key format in Keychain: "<project_id>:<access_token>"
Access tokens expire after 1 hour. Obtain with: gcloud auth print-access-token
For long-term use, store a service account JSON key: "<project_id>:<b64_service_account_json>"
"""
from __future__ import annotations
import base64
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

from .base import Provider, GenRequest, GenResult
from ..scrub import scrub

_LOCATION = "us-central1"
_IMAGE_MODEL = "imagegeneration@006"


def _api(project_id: str, token: str, path: str, payload: dict) -> dict:
    url = f"https://{_LOCATION}-aiplatform.googleapis.com/v1/{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"Imagen HTTP {e.code}: {body}") from None


def _parse_key(api_key: str) -> tuple[str, str]:
    """Returns (project_id, access_token)."""
    if ":" not in api_key:
        raise ValueError("Imagen key must be 'project_id:access_token'")
    project_id, token = api_key.split(":", 1)
    return project_id, token


class ImagenProvider(Provider):
    name = "imagen"
    supports_image = True
    supports_video = False
    keychain_service = "pushing-creation:imagen"

    def generate_image(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        project_id, token = _parse_key(api_key)
        ar_map = {
            "1:1": "1:1", "16:9": "16:9", "9:16": "9:16",
            "4:3": "4:3", "3:4": "3:4",
        }
        aspect = ar_map.get(req.aspect_ratio, "1:1")
        payload = {
            "instances": [{"prompt": req.prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": aspect,
                "negativePrompt": req.negative_prompt or "",
            },
        }
        path = f"projects/{project_id}/locations/{_LOCATION}/publishers/google/models/{_IMAGE_MODEL}:predict"
        resp = _api(project_id, token, path, payload)
        predictions = resp.get("predictions") or []
        if not predictions:
            raise RuntimeError(f"No predictions in Imagen response: {scrub(str(resp))}")

        b64 = predictions[0].get("bytesBase64Encoded", "")
        if not b64:
            raise RuntimeError("No image bytes in Imagen prediction")

        out = req.out_path.with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(base64.b64decode(b64))
        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": _IMAGE_MODEL, "project": project_id},
        )

    def generate_video(self, req: GenRequest, api_key: str) -> GenResult:
        raise NotImplementedError("Use gemini provider for Veo 3 video generation")

    def ping(self, api_key: str) -> bool:
        try:
            project_id, token = _parse_key(api_key)
            path = f"projects/{project_id}/locations/{_LOCATION}/publishers/google/models/{_IMAGE_MODEL}"
            _api(project_id, token, path, {})
        except RuntimeError as e:
            # 404 or similar means key is valid but model not accessible
            return "404" not in str(e) and "403" not in str(e)
        except Exception:
            return False
        return True
