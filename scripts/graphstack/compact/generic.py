"""Generic compaction for test runners and unknown commands."""

from __future__ import annotations

import re

from .base import (
    _DEFAULT_MAX_LINES,
    dedupe_consecutive,
    is_critical_line,
    truncate_preserving_critical,
)

_PYTEST_SUMMARY_RE = re.compile(
    r"(?i)=+\s*(FAILURES|ERRORS|short test summary|passed|failed)\s*=+"
)


def compact_pytest(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return ""

    keep: list[str] = []
    in_failure_block = False
    failure_blocks: list[list[str]] = []
    current_block: list[str] = []

    for line in lines:
        if _PYTEST_SUMMARY_RE.search(line) or line.startswith("FAILED ") or line.startswith("ERROR "):
            in_failure_block = True
        if in_failure_block:
            current_block.append(line)
            if line.strip() == "" and len(current_block) > 3:
                failure_blocks.append(current_block)
                current_block = []
                in_failure_block = False
            continue
        if is_critical_line(line):
            keep.append(line)
        elif "passed" in line.lower() and "failed" in line.lower():
            keep.append(line)

    if current_block:
        failure_blocks.append(current_block)

    # Last lines often hold the summary
    tail = lines[-15:] if len(lines) > 15 else lines
    for line in tail:
        if line not in keep and (is_critical_line(line) or "passed" in line.lower()):
            keep.append(line)

    out: list[str] = []
    for block in failure_blocks[-5:]:
        out.extend(block[:40])
    out.extend(keep)
    out = dedupe_consecutive(out)

    if len(out) > _DEFAULT_MAX_LINES:
        out, omitted = truncate_preserving_critical(out)
        out.append(f"... [{omitted} lines omitted — use: graphstack run --raw -- pytest ...]")

    if not out:
        return compact_generic(text)
    return "\n".join(out)


def compact_generic(text: str, *, max_lines: int = _DEFAULT_MAX_LINES) -> str:
    lines = text.splitlines()
    if not lines:
        return ""

    # Strip obvious noise (progress bars, download meters)
    filtered: list[str] = []
    for line in lines:
        if re.search(r"[\|/#\-]{4,}.*\d+%", line):
            continue
        if re.match(r"^\s*$", line) and filtered and filtered[-1] == "":
            continue
        filtered.append(line)

    filtered = dedupe_consecutive(filtered)
    if len(filtered) <= max_lines:
        return "\n".join(filtered)

    trimmed, omitted = truncate_preserving_critical(filtered, max_lines=max_lines)
    trimmed.append(
        f"... [{omitted} lines omitted — use: graphstack run --raw -- <command> for full output]"
    )
    return "\n".join(trimmed)
