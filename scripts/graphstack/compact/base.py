"""Shared helpers for safe output compaction."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Lines matching these patterns are never dropped during truncation.
_CRITICAL_RE = re.compile(
    r"(?i)(error|failed|failure|exception|traceback|fatal|panic|assertion|"
    r"not found|cannot |can't |conflict|denied|fatal:|FAILED|ERROR\b|"
    r"^\+{3}|^-{3}|^@@\s|^\?\?\s|^[MADRCU!]{1,2}\s)",
)

_DEFAULT_MAX_LINES = 120
_MIN_RETAINED_RATIO = 0.05  # if output shrinks below 5% of input, prefer raw


@dataclass(frozen=True)
class CompactResult:
    text: str
    used_compactor: str
    fell_back_to_raw: bool = False


def is_critical_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return bool(_CRITICAL_RE.search(stripped))


def dedupe_consecutive(lines: list[str]) -> list[str]:
    if not lines:
        return []
    out: list[str] = []
    prev = lines[0]
    count = 1
    for line in lines[1:]:
        if line == prev:
            count += 1
            continue
        if count > 1:
            out.append(f"{prev}  (×{count})")
        else:
            out.append(prev)
        prev = line
        count = 1
    if count > 1:
        out.append(f"{prev}  (×{count})")
    else:
        out.append(prev)
    return out


def truncate_preserving_critical(
    lines: list[str],
    *,
    max_lines: int = _DEFAULT_MAX_LINES,
) -> tuple[list[str], int]:
    """Keep critical lines and a head/tail window; return (lines, omitted_count)."""
    if len(lines) <= max_lines:
        return lines, 0

    critical_idx = [i for i, line in enumerate(lines) if is_critical_line(line)]
    keep: set[int] = set()
    head = max_lines // 3
    tail = max_lines // 3
    for i in range(min(head, len(lines))):
        keep.add(i)
    for i in range(max(0, len(lines) - tail), len(lines)):
        keep.add(i)
    keep.update(critical_idx)

    if len(keep) > max_lines:
        # Too many critical lines — keep all critical + fill with head/tail budget
        ordered = sorted(keep)
        keep = set(ordered[: max_lines])
    else:
        # Fill remaining budget with lines near critical regions
        for idx in critical_idx:
            for j in range(max(0, idx - 2), min(len(lines), idx + 3)):
                if len(keep) >= max_lines:
                    break
                keep.add(j)

    selected = [lines[i] for i in sorted(keep)]
    omitted = len(lines) - len(selected)
    return selected, omitted


def safe_compact(
    raw: str,
    compactor_name: str,
    compacted: str,
) -> CompactResult:
    """Return compacted text unless it lost too much signal vs raw."""
    raw_stripped = raw.strip()
    compact_stripped = compacted.strip()

    if not raw_stripped:
        return CompactResult("", compactor_name, fell_back_to_raw=False)

    if not compact_stripped:
        return CompactResult(raw.rstrip("\n"), compactor_name, fell_back_to_raw=True)

    raw_lines = raw.splitlines()
    compact_lines = compacted.splitlines()
    if len(compact_lines) < max(1, int(len(raw_lines) * _MIN_RETAINED_RATIO)):
        # Extreme shrink — only accept if raw was huge noise (progress bars only)
        if not any(is_critical_line(line) for line in raw_lines):
            return CompactResult(compacted.rstrip("\n"), compactor_name, fell_back_to_raw=False)
        return CompactResult(raw.rstrip("\n"), compactor_name, fell_back_to_raw=True)

    return CompactResult(compacted.rstrip("\n"), compactor_name, fell_back_to_raw=False)
