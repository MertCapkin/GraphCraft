"""Shared handoff/BRIEF/REVIEW helpers for gate, validate, and cycle."""

from __future__ import annotations

import re
from pathlib import Path

from .constants import HANDOFF_DIR

BRIEF_PATH = HANDOFF_DIR / "BRIEF.md"
REVIEW_PATH = HANDOFF_DIR / "REVIEW.md"

BRIEF_TEMPLATE_MARKERS = (
    "[Feature/Change Name]",
    "YYYY-MM-DD",
    "> One sentence. What outcome does the user want?",
)
BRIEF_READY_STATUSES = ("Ready for Builder", "In Review", "Complete")

STATUS_LINE_RE = re.compile(r"\*\*Status:\*\*\s*(.+)", re.MULTILINE)


def read_brief_text() -> str | None:
    try:
        return BRIEF_PATH.read_text(encoding="utf-8")
    except OSError:
        return None


def brief_is_template(text: str) -> bool:
    return any(marker in text for marker in BRIEF_TEMPLATE_MARKERS)


def brief_status(text: str) -> str | None:
    match = STATUS_LINE_RE.search(text)
    if not match:
        return None
    return match.group(1).strip()


def brief_is_draft() -> bool:
    text = read_brief_text()
    if text is None or brief_is_template(text):
        return True
    status = brief_status(text)
    return status is None or status.startswith("Draft")


def brief_is_ready_for_builder() -> bool:
    text = read_brief_text()
    if text is None or brief_is_template(text):
        return False
    status = brief_status(text)
    if not status:
        return False
    return any(marker in status for marker in BRIEF_READY_STATUSES)


def set_brief_status(new_status: str) -> bool:
    """Update **Status:** line in BRIEF.md. Returns False if file missing."""
    try:
        text = BRIEF_PATH.read_text(encoding="utf-8")
    except OSError:
        return False
    if STATUS_LINE_RE.search(text):
        text = STATUS_LINE_RE.sub(f"**Status:** {new_status}", text, count=1)
    else:
        text = f"**Status:** {new_status}\n\n{text}"
    BRIEF_PATH.write_text(text, encoding="utf-8")
    return True


def _review_last_section() -> str:
    try:
        text = REVIEW_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    sections = re.split(r"^## ", text, flags=re.MULTILINE)
    if len(sections) <= 1:
        return ""
    return sections[-1]


def review_last_has_verdict() -> bool:
    """True when the latest ## section in REVIEW.md contains a Verdict line."""
    last = _review_last_section()
    return bool(last) and "Verdict:" in last


def review_last_verdict_approved() -> bool:
    """True when the latest ## section in REVIEW.md contains Verdict: Approved."""
    last = _review_last_section()
    return "Verdict: Approved" in last
