"""Bytedance Seedream image generation via Volcano Engine API.

Key format in Keychain: "<access_key>:<secret_key>" (colon-separated).
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from .base import Provider, GenRequest, GenResult
from ..scrub import scrub

_HOST = "visual.volcengineapi.com"
_REGION = "cn-north-1"
_SERVICE = "cv"
_ACTION = "CVProcess"
_VERSION = "2022-08-31"


def _sign(access_key: str, secret_key: str, payload: dict) -> dict:
    """Volcano Engine signature v4."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    datetime_str = now.strftime("%Y%m%dT%H%M%SZ")

    body = json.dumps(payload).encode()
    body_hash = hashlib.sha256(body).hexdigest()

    canonical_headers = f"content-type:application/json\nhost:{_HOST}\nx-date:{datetime_str}\n"
    signed_headers = "content-type;host;x-date"
    canonical_request = "\n".join([
        "POST",
        "/",
        f"Action={_ACTION}&Version={_VERSION}",
        canonical_headers,
        signed_headers,
        body_hash,
    ])

    credential_scope = f"{date_str}/{_REGION}/{_SERVICE}/request"
    string_to_sign = "\n".join([
        "HMAC-SHA256",
        datetime_str,
        credential_scope,
        hashlib.sha256(canonical_request.encode()).hexdigest(),
    ])

    def hmac_sha256(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    signing_key = hmac_sha256(
        hmac_sha256(
            hmac_sha256(
                hmac_sha256(secret_key.encode(), date_str),
                _REGION,
            ),
            _SERVICE,
        ),
        "request",
    )
    signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()

    auth = (
        f"HMAC-SHA256 Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    return {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Host": _HOST,
        "X-Date": datetime_str,
        "body": body,
    }


def _post(access_key: str, secret_key: str, payload: dict) -> dict:
    headers = _sign(access_key, secret_key, payload)
    body = headers.pop("body")
    url = f"https://{_HOST}/?Action={_ACTION}&Version={_VERSION}"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"Seedream HTTP {e.code}: {err}") from None


def _parse_key(api_key: str) -> tuple[str, str]:
    if ":" not in api_key:
        raise ValueError("Seedream key must be 'access_key:secret_key'")
    access_key, secret_key = api_key.split(":", 1)
    return access_key, secret_key


class SeedreamProvider(Provider):
    name = "seedream"
    supports_image = True
    supports_video = False
    keychain_service = "pushing-creation:seedream"

    def generate_image(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        access_key, secret_key = _parse_key(api_key)
        ar_map = {
            "1:1": "1:1", "16:9": "16:9", "9:16": "9:16",
            "4:3": "4:3", "3:4": "3:4", "21:9": "21:9",
        }
        aspect = ar_map.get(req.aspect_ratio, "16:9")
        payload = {
            "req_key": "seedream_v3_i2i",
            "prompt": req.prompt,
            "negative_prompt": req.negative_prompt or "",
            "aspect_ratio": aspect,
            "return_url": True,
        }
        resp = _post(access_key, secret_key, payload)
        code = resp.get("ResponseMetadata", {}).get("Error", {})
        if code.get("Code"):
            raise RuntimeError(f"Seedream error {code.get('Code')}: {scrub(code.get('Message', ''))}")

        result = resp.get("Result") or {}
        image_urls = result.get("image_urls") or []
        if not image_urls:
            # Try binary data
            b64_images = result.get("binary_data_base64") or []
            if not b64_images:
                raise RuntimeError(f"No image in Seedream response: {scrub(str(resp))}")
            out = req.out_path.with_suffix(".png")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(base64.b64decode(b64_images[0]))
        else:
            out = req.out_path.with_suffix(".png")
            out.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(image_urls[0], timeout=120) as dl:
                out.write_bytes(dl.read())

        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": "seedream-v3"},
        )

    def generate_video(self, req: GenRequest, api_key: str) -> GenResult:
        raise NotImplementedError("Seedream is image-only. Use seedance for video.")

    def ping(self, api_key: str) -> bool:
        try:
            access_key, secret_key = _parse_key(api_key)
            # Smallest possible query: list models or check status
            payload = {"req_key": "seedream_v3_i2i", "prompt": "test", "return_url": True}
            resp = _post(access_key, secret_key, payload)
            # Any non-auth error is still a working key
            err = (resp.get("ResponseMetadata") or {}).get("Error") or {}
            code = err.get("Code", "")
            return "Auth" not in code and "InvalidKey" not in code
        except Exception:
            return False
