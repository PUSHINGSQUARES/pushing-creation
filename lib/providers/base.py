from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GenRequest:
    prompt: str
    negative_prompt: str | None
    refs: list[Path]
    aspect_ratio: str
    out_path: Path
    extras: dict = field(default_factory=dict)


@dataclass
class GenResult:
    out_path: Path
    duration_seconds: float
    cost_estimate_usd: float | None
    provider_metadata: dict = field(default_factory=dict)


class Provider(ABC):
    name: str
    supports_image: bool
    supports_video: bool
    keychain_service: str

    @abstractmethod
    def generate_image(self, req: GenRequest, api_key: str) -> GenResult: ...

    @abstractmethod
    def generate_video(self, req: GenRequest, api_key: str) -> GenResult: ...

    def ping(self, api_key: str) -> bool:
        """Cheapest possible call to verify the key works. Returns True on success."""
        raise NotImplementedError
