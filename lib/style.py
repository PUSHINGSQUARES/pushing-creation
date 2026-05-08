"""Parse style.md STYLE_ and NEG_ blocks."""
from __future__ import annotations
import re
from pathlib import Path


def parse(path: Path) -> dict[str, str]:
    """Return a dict mapping block name -> prompt fragment."""
    text = path.read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    current: str | None = None
    body_lines: list[str] = []

    for line in text.splitlines():
        # Block header: ## STYLE_FOO or ## NEG_BAR
        m = re.match(r"^##\s+((?:STYLE|NEG)_\S+)", line)
        if m:
            if current is not None:
                blocks[current] = "\n".join(body_lines).strip()
            current = m.group(1)
            body_lines = []
            continue

        if current is not None:
            # Skip HTML comments and blank lines at the start
            if not body_lines and (not line.strip() or line.strip().startswith("<!--")):
                continue
            if line.strip().startswith("<!--") or line.strip() == "-->":
                continue
            # End if we hit another ## heading that isn't a block
            if line.startswith("## ") and not re.match(r"^##\s+((?:STYLE|NEG)_)", line):
                blocks[current] = "\n".join(body_lines).strip()
                current = None
                body_lines = []
                continue
            body_lines.append(line)

    if current is not None:
        blocks[current] = "\n".join(body_lines).strip()

    return blocks


def resolve(block_names: list[str], blocks: dict[str, str]) -> str:
    """Join the bodies of the named blocks into a single prompt fragment."""
    parts = []
    for name in block_names:
        body = blocks.get(name)
        if body:
            parts.append(body)
    return ", ".join(parts)
