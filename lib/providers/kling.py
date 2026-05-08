"""Kling video generation via Kling AI API."""
from __future__ import annotations
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

from .base import Provider, GenRequest, GenResult
from ..scrub import scrub

_BASE = "https://api.klingai.com/v1"


def _api(path: str, payload: dict | None, api_key: str, method: str = "POST") -> dict:
    url = f"{_BASE}/{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        raise RuntimeError(f"Kling HTTP {e.code}: {body}") from None


class KlingProvider(Provider):
    name = "kling"
    supports_image = False
    supports_video = True
    keychain_service = "pushing-creation:kling"

    def generate_image(self, req: GenRequest, api_key: str) -> GenResult:
        raise NotImplementedError("Kling does not support image generation")

    def generate_video(self, req: GenRequest, api_key: str) -> GenResult:
        t0 = time.monotonic()
        ar_map = {
            "16:9": "16:9", "9:16": "9:16", "1:1": "1:1",
        }
        aspect = ar_map.get(req.aspect_ratio, "16:9")
        duration = req.extras.get("duration", "5")

        payload = {
            "model": "kling-v2-master",
            "prompt": req.prompt,
            "negative_prompt": req.negative_prompt or "",
            "cfg_scale": 0.5,
            "mode": "std",
            "duration": str(duration),
            "aspect_ratio": aspect,
        }
        resp = _api("videos/text2video", payload, api_key)
        task_id = (resp.get("data") or {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"No task_id in Kling response: {scrub(str(resp))}")

        # Poll for completion
        for _ in range(120):
            time.sleep(5)
            status = _api(f"videos/text2video/{task_id}", None, api_key, method="GET")
            task_status = (status.get("data") or {}).get("task_status", "")
            if task_status == "succeed":
                break
            if task_status == "failed":
                msg = (status.get("data") or {}).get("task_status_msg", "unknown")
                raise RuntimeError(f"Kling task failed: {scrub(msg)}")
        else:
            raise RuntimeError("Kling generation timed out after 10 minutes")

        videos = (status.get("data") or {}).get("task_result", {}).get("videos", [])
        if not videos:
            raise RuntimeError(f"No video in Kling result: {scrub(str(status))}")
        video_url = videos[0].get("url", "")
        if not video_url:
            raise RuntimeError("No video URL in Kling result")

        out = req.out_path.with_suffix(".mp4")
        out.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(video_url, timeout=300) as dl:
            out.write_bytes(dl.read())

        return GenResult(
            out_path=out,
            duration_seconds=time.monotonic() - t0,
            cost_estimate_usd=None,
            provider_metadata={"model": "kling-v2-master", "task_id": task_id},
        )

    def ping(self, api_key: str) -> bool:
        try:
            resp = _api("account/costs", None, api_key, method="GET")
            return resp.get("code") == 0 or "data" in resp
        except Exception:
            return False
