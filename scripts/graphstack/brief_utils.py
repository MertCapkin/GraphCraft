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


def _review_sections() -> list[str]:
    try:
        text = REVIEW_PATH.read_text(encoding="utf-8")
    except OSError:
        return []
    parts = re.split(r"^## ", text, flags=re.MULTILINE)
    if len(parts) <= 1:
        return []
    return parts[1:]


def _review_last_verdict_section() -> str:
    """Latest ## section that contains a Reviewer Verdict line."""
    for body in reversed(_review_sections()):
        if "Verdict:" in body:
            return body
    return ""


def review_last_has_verdict() -> bool:
    """True when REVIEW.md has a ## section with a Verdict line."""
    return bool(_review_last_verdict_section())


def review_last_verdict_approved() -> bool:
    """True when the latest Verdict section contains Verdict: Approved."""
    last = _review_last_verdict_section()
    return "Verdict: Approved" in last


def _review_last_qa_section() -> str:
    """Return the latest ## section whose heading contains 'QA Report'."""
    for body in reversed(_review_sections()):
        if body.lstrip().startswith("QA Report"):
            return body
    return ""


def review_last_has_qa_report() -> bool:
    return bool(_review_last_qa_section())


def review_last_qa_passed() -> bool:
    """True when latest QA Report has Overall PASS (not FAIL)."""
    qa = _review_last_qa_section()
    if not qa:
        return False
    for line in qa.splitlines():
        if "Overall:" not in line:
            continue
        if "FAIL" in line.upper() and "PASS" not in line.upper():
            return False
        if "PASS" in line.upper() or "✅" in line:
            return True
    return False


def review_last_qa_shippable() -> bool:
    """True when QA is PASS or acceptable PARTIAL (not FAIL)."""
    qa = _review_last_qa_section()
    if not qa:
        return False
    for line in qa.splitlines():
        if "Overall:" not in line:
            continue
        upper = line.upper()
        if "FAIL" in upper and "PASS" not in upper:
            return False
        if "PASS" in upper or "PARTIAL" in upper or "✅" in line or "⚠️" in line:
            return True
    return False
