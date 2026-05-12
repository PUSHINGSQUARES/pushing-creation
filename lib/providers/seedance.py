"""Bytedance Seedance video generation via Volcano Engine API.

Key format in Keychain: "<access_key>:<secret_key>" (colon-separated).
"""
from __future__ import annotations
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
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    datetime_str = now.strftime("%Y%m%dT%H%M%SZ")
    body = json.dumps(payload).encode()
    body_hash = hashlib.sha256(body).hexdigest()
    canonical_headers = f"content-type:application/json\nhost:{_HOST}\nx-date:{datetime_str}\n"
    signed_headers = "content-type;host;x-date"
    canonical_request = "\n".join([
        "POST", "/",
        f"Action={_ACTION}&Version={_VERSION}",
        canonical_headers, signed_headers, body_hash,
    ])
    credential_scope = f"{date_str}/{_REGION}/{_SERVICE}/request"
    string_to_sign = "\n".join([
        "HMAC-SHA256", datetime_str, credential_scope,
        hashlib.sha256(canonical_request.encode()).hexdigest(),
    ])

    def h(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    signing_key = h(h(h(h(secret_key.encode(), date_str), _REGION), _SERVICE), "request")
    signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
    auth = (
        f"HMAC-SHA256 Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    return {"Authorization": auth, "Content-Type": "application/json",
            "Host": _HOST, "X-Date": datetime_str, "body": body}


def _post(access_key: str, secret_key: str, payload: dict) -> dict:
    headers = _sign(access_key, secret_key, payload)
    body = headers.pop("body")
    url = f"https://{_HOST}/?Action={_ACTION}&Version={_VERSION}"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"Seedance HTTP {e.code}: {err}") from None


def _parse_key(api_key: str) -> tuple[str, str]:
    if ":" not in api_key:
        raise ValueError("Seedance key must be 'access_key:secret_key'")
    access_key, secret_key = api_key.split(":", 1)
    return access_key, secret_key


class SeedanceProvider(Provider):
    name = "seedance"
    supports_image = False
    supports_video = True
    keychain_service = "pushing-creation:seedance"

    def generate_image(self, req: GenRequest, api_key: str) -> GenResult:
        raise NotImplementedError("Seedance is video-only. Use seedream for images.")

    def generate_video(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        access_key, secret_key = _parse_key(api_key)
        ar_map = {"16:9": "16:9", "9:16": "9:16", "1:1": "1:1"}
        aspect = ar_map.get(req.aspect_ratio, "16:9")
        duration = int(req.extras.get("duration", 5))
        payload = {
            "req_key": "seedance_v1_lite_t2v",
            "prompt": req.prompt,
            "negative_prompt": req.negative_prompt or "",
            "aspect_ratio": aspect,
            "duration": duration,
            "return_url": True,
        }
        resp = _post(access_key, secret_key, payload)
        err = (resp.get("ResponseMetadata") or {}).get("Error") or {}
        if err.get("Code"):
            raise RuntimeError(f"Seedance error {err['Code']}: {scrub(err.get('Message', ''))}")

        # Seedance may return async task ID
        result = resp.get("Result") or {}
        task_id = result.get("task_id")
        if task_id:
            for _ in range(120):
                time.sleep(5)
                query_payload = {"req_key": "seedance_v1_lite_t2v_query", "task_id": task_id}
                status = _post(access_key, secret_key, query_payload)
                sr = (status.get("Result") or {})
                if sr.get("status") == "done":
                    result = sr
                    break
                if sr.get("status") == "failed":
                    raise RuntimeError(f"Seedance task failed: {scrub(str(sr))}")
            else:
                raise RuntimeError("Seedance generation timed out")

        video_urls = result.get("video_urls") or []
        if not video_urls:
            raise RuntimeError(f"No video in Seedance response: {scrub(str(resp))}")

        out = req.out_path.with_suffix(".mp4")
        out.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(video_urls[0], timeout=300) as dl:
            out.write_bytes(dl.read())

        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": "seedance-v1-lite"},
        )

    def ping(self, api_key: str) -> bool:
        try:
            _parse_key(api_key)
        except ValueError as e:
            raise NotImplementedError(
                f"Seedance ping requires access_key:secret_key format -- "
                f"key format not yet resolved for this Keychain entry: {e}"
            ) from e
        return True
