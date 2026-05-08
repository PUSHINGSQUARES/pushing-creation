"""Tests for storyboard.md parsing."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.storyboard import parse, get_by_id, get_by_number

_SAMPLE_STORYBOARD = """\
---
title: Test Project
---

# Shots

| Shot | Provider | Model | Camera | Lens | Aspect | Action | Refs | Style | Neg | Mode | Duration |
|------|----------|-------|--------|------|--------|--------|------|-------|-----|------|----------|
| opening_wide | gemini | gemini-flash | ARRI Alexa 35 | 50mm T1.5 | 16:9 | Establishing shot of mountain range. | mountain_ref.jpg | STYLE_PHOTOREAL_BASE, STYLE_CINEMATIC | NEG_HUMAN | image | |
| car_drift | seedream | seedream-v3 | RED Komodo 6K | 24mm T2.8 | 21:9 | Sports car drifting through corner. | | STYLE_PHOTOREAL_BASE | NEG_CAR | image | |
| flyover | kling | kling-v2 | DJI aerial | 14mm | 16:9 | Aerial drone flyover of coastline. | coast.jpg | STYLE_GUIDE | NEG_HUMAN | video | 5s |
"""


def _write_tmp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    f.write(content)
    f.close()
    return Path(f.name)


def test_parse_shot_count():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    assert len(shots) == 3


def test_parse_shot_ids():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    ids = [s.id for s in shots]
    assert "opening_wide" in ids
    assert "car_drift" in ids
    assert "flyover" in ids


def test_parse_shot_fields():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    shot = shots[0]
    assert shot.camera == "ARRI Alexa 35"
    assert shot.aspect == "16:9"
    assert "STYLE_PHOTOREAL_BASE" in shot.style
    assert "STYLE_CINEMATIC" in shot.style
    assert "NEG_HUMAN" in shot.neg
    assert shot.mode == "image"


def test_parse_refs_split():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    shot = shots[0]
    assert "mountain_ref.jpg" in shot.refs


def test_get_by_id():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    shot = get_by_id(shots, "car_drift")
    assert shot is not None
    assert shot.id == "car_drift"


def test_get_by_id_missing():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    assert get_by_id(shots, "nonexistent") is None


def test_get_by_number():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    shot = get_by_number(shots, 1)
    assert shot is not None
    assert shot.id == "opening_wide"


def test_get_by_number_third():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    shot = get_by_number(shots, 3)
    assert shot is not None
    assert shot.id == "flyover"


def test_video_shot_mode():
    path = _write_tmp(_SAMPLE_STORYBOARD)
    shots = parse(path)
    video_shot = get_by_id(shots, "flyover")
    assert video_shot is not None
    assert video_shot.mode == "video"
    assert video_shot.duration == "5s"


def test_parse_template_storyboard():
    """Verify the real template storyboard parses cleanly."""
    template_path = Path(__file__).parent.parent / "templates" / "storyboard.md"
    if not template_path.exists():
        return
    shots = parse(template_path)
    assert len(shots) >= 1
    for shot in shots:
        assert shot.id
        assert shot.number >= 1
