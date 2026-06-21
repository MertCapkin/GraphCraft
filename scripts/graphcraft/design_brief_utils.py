"""Design brief status helpers."""

from __future__ import annotations

import re
from pathlib import Path

from .constants import HANDOFF_DESIGN

_STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(.+)$", re.MULTILINE)


def read_design_brief_text(root: Path | None = None) -> str | None:
    path = HANDOFF_DESIGN if root is None else root / HANDOFF_DESIGN
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def design_brief_status(text: str | None = None, root: Path | None = None) -> str | None:
    if text is None:
        text = read_design_brief_text(root)
    if text is None:
        return None
    match = _STATUS_RE.search(text)
    return match.group(1).strip() if match else None


def design_brief_is_ready(root: Path | None = None) -> bool:
    status = design_brief_status(root=root)
    return status is not None and "ready for builder" in status.lower()


def set_design_brief_status(status: str, root: Path | None = None) -> bool:
    path = HANDOFF_DESIGN if root is None else root / HANDOFF_DESIGN
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if _STATUS_RE.search(text):
        new_text = _STATUS_RE.sub(f"**Status:** {status}", text, count=1)
    else:
        new_text = text.replace("---\n", f"**Status:** {status}\n\n---\n", 1)
    path.write_text(new_text, encoding="utf-8")
    return True
