"""Git command output compactors — preserve paths, branch, and diff hunks."""

from __future__ import annotations

import re
from .base import (
    _DEFAULT_MAX_LINES,
    dedupe_consecutive,
    is_critical_line,
    truncate_preserving_critical,
)

_BRANCH_RE = re.compile(r"^On branch (.+)$|^HEAD detached at (.+)$", re.MULTILINE)
_AHEAD_BEHIND_RE = re.compile(
    r"Your branch is (ahead of|behind) [^\s]+ by (\d+) commit",
)


def compact_git_status(text: str) -> str:
    porcelain = _try_porcelain_status(text)
    if porcelain is not None:
        return porcelain

    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        if _BRANCH_RE.match(line) or _AHEAD_BEHIND_RE.search(line):
            out.append(line.strip())
        elif line.startswith("nothing to commit"):
            out.append(line.strip())
        elif line.strip().startswith(("modified:", "new file:", "deleted:", "renamed:")):
            out.append(line.strip())
        elif line.strip() and (
            line.startswith("\t") or line.startswith("  ") or ":" in line[:40]
        ):
            out.append(line.strip())

    if not out:
        return text.strip()

    grouped = dedupe_consecutive(out)
    if len(grouped) > _DEFAULT_MAX_LINES:
        grouped, omitted = truncate_preserving_critical(grouped)
        grouped.append(f"... [{omitted} lines omitted — use: graphstack run --raw -- git status]")
    return "\n".join(grouped)


def _try_porcelain_status(text: str) -> str | None:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    if not all(len(ln) >= 3 and ln[2] in (" ", "?") for ln in lines if not ln.startswith("#")):
        # Heuristic: porcelain lines are XY + space + path
        xy_lines = [ln for ln in lines if len(ln) >= 4 and ln[2] == " "]
        if len(xy_lines) < len(lines) * 0.5:
            return None

    branch_lines = [ln[2:].strip() for ln in lines if ln.startswith("## ")]
    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []

    for line in lines:
        if line.startswith("#") or line.startswith("##"):
            continue
        if len(line) < 4:
            continue
        xy, path = line[:2], line[3:].strip()
        if xy == "??":
            untracked.append(path)
        elif xy[0] != " ":
            staged.append(path)
        elif xy[1] != " ":
            unstaged.append(path)

    parts: list[str] = []
    if branch_lines:
        parts.append(branch_lines[0])
    if staged:
        parts.append(f"staged ({len(staged)}): " + ", ".join(_limit_paths(staged)))
    if unstaged:
        parts.append(f"unstaged ({len(unstaged)}): " + ", ".join(_limit_paths(unstaged)))
    if untracked:
        parts.append(f"untracked ({len(untracked)}): " + ", ".join(_limit_paths(untracked)))
    if not parts:
        return None
    return "\n".join(parts)


def _limit_paths(paths: list[str], limit: int = 40) -> list[str]:
    if len(paths) <= limit:
        return paths
    head = paths[:limit]
    head.append(f"... +{len(paths) - limit} more")
    return head


def compact_git_diff(text: str, *, max_lines: int = 150) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text.strip()

    # Always keep file headers and hunk headers; preserve +/- lines in each hunk
    kept: list[str] = []
    hunk_lines: list[str] = []
    omitted = 0

    def flush_hunk() -> None:
        nonlocal omitted
        if not hunk_lines:
            return
        if len(kept) + len(hunk_lines) > max_lines and len(hunk_lines) > 30:
            # Keep hunk header + first/last change lines
            header = [hunk_lines[0]] if hunk_lines[0].startswith("@@") else []
            changes = [
                ln
                for ln in hunk_lines
                if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))
            ]
            body = header + changes[:12] + (["..."] if len(changes) > 12 else []) + changes[-6:]
            kept.extend(body)
            omitted += len(hunk_lines) - len(body)
        else:
            kept.extend(hunk_lines)

    for line in lines:
        if line.startswith("diff --git") or line.startswith("--- ") or line.startswith("+++ "):
            flush_hunk()
            hunk_lines = []
            kept.append(line)
        elif line.startswith("@@"):
            flush_hunk()
            hunk_lines = [line]
        else:
            hunk_lines.append(line)
    flush_hunk()

    if omitted:
        kept.append(
            f"... [{omitted} diff lines omitted — use: graphstack run --raw -- git diff]"
        )
    return "\n".join(kept)


def compact_git_log(text: str, *, max_entries: int = 30) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) <= max_entries:
        return "\n".join(lines)

    compacted: list[str] = []
    for line in lines[:max_entries]:
        if re.match(r"^[0-9a-f]{7,40}\s", line):
            compacted.append(line)
        elif re.match(r"^commit [0-9a-f]{40}", line):
            continue  # skip full commit header blocks when verbose
        elif line.startswith("Author:") or line.startswith("Date:"):
            continue
        elif is_critical_line(line):
            compacted.append(line)
        else:
            compacted.append(line[:120])

    compacted.append(
        f"... [{len(lines) - max_entries} older entries omitted — "
        "use: graphstack run --raw -- git log ...]"
    )
    return "\n".join(compacted)
