"""Parse storyboard.md shot tables into structured records."""
from __future__ import annotations
import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Shot:
    id: str
    number: int          # 1-indexed position in table
    provider: str
    model: str
    camera: str
    lens: str
    aspect: str
    action: str
    refs: list[str]      # filenames from the Refs column
    style: list[str]     # STYLE_ block names
    neg: list[str]       # NEG_ block names
    mode: str            # "image" or "video"
    duration: str        # e.g. "5s" or ""
    raw: dict[str, str] = field(default_factory=dict)


_HEADER_COLS = ["shot", "provider", "model", "camera", "lens", "aspect",
                "action", "refs", "style", "neg", "mode", "duration"]


def _split_row(line: str) -> list[str]:
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def parse(path: Path) -> list[Shot]:
    text = path.read_text(encoding="utf-8")
    shots: list[Shot] = []
    in_table = False
    col_map: dict[str, int] = {}
    row_number = 0

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                in_table = False
            continue

        cells = _split_row(line)
        if not cells:
            continue

        if not in_table:
            # Try to treat this as a header row
            lower = [c.lower() for c in cells]
            if "shot" in lower and "action" in lower:
                col_map = {h: i for i, h in enumerate(lower) if h in _HEADER_COLS}
                in_table = True
            continue

        # Skip separator row
        if all(re.match(r"^[-:]+$", c) for c in cells if c):
            continue

        def cell(name: str) -> str:
            idx = col_map.get(name)
            if idx is None or idx >= len(cells):
                return ""
            return cells[idx]

        shot_id = cell("shot")
        if not shot_id:
            continue

        row_number += 1
        mode = cell("mode").lower() or ("video" if cell("duration") else "image")
        refs_raw = cell("refs")
        style_raw = cell("style")
        neg_raw = cell("neg")

        shots.append(Shot(
            id=shot_id,
            number=row_number,
            provider=cell("provider"),
            model=cell("model"),
            camera=cell("camera"),
            lens=cell("lens"),
            aspect=cell("aspect") or "16:9",
            action=cell("action"),
            refs=[r.strip() for r in refs_raw.split(",") if r.strip()],
            style=[s.strip() for s in style_raw.split(",") if s.strip()],
            neg=[n.strip() for n in neg_raw.split(",") if n.strip()],
            mode=mode,
            duration=cell("duration"),
            raw={k: cell(k) for k in col_map},
        ))

    return shots


def get_by_id(shots: list[Shot], shot_id: str) -> "Shot | None":
    for s in shots:
        if s.id == shot_id:
            return s
    return None


def get_by_number(shots: list[Shot], n: int) -> "Shot | None":
    for s in shots:
        if s.number == n:
            return s
    return None
