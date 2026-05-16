"""Smart graph-update logic — pure Python port of ``scripts/post-commit``.

Triggers on:
- new/deleted files (structural change)
- ``Ship`` commits (``board: complete``, ``[ship]``, ``ship:`` prefixes)
- staleness > 24 hours

Skips on:
- pure content edits to existing files

Improvements over bash original:
- Handles the *first* commit gracefully (no ``HEAD~1`` to diff against)
- Cross-platform mtime check (``date -r`` / ``stat -c`` portability solved)
- Uses Python regex instead of grep -E
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

from .constants import GRAPH_HTML, GRAPH_JSON, GRAPH_REPORT, GRAPHIFY_OUT, STALE_GRAPH_HOURS
from .platform_utils import echo, file_mtime_seconds, graphify_available, run_git

SHIP_COMMIT_PATTERN = re.compile(r"^(?:board: complete|\[ship\]|ship:)", re.IGNORECASE)
EXCLUDE_PREFIXES = ("graphify-out/", "handoff/")


def _has_previous_commit() -> bool:
    """``HEAD~1`` exists only after at least 2 commits — guard for first commit."""
    return run_git("rev-parse", "--verify", "HEAD~1").returncode == 0


def _structural_changes_count() -> int:
    """Number of added/deleted files in the latest commit (excluding generated dirs)."""
    if not _has_previous_commit():
        return 0
    result = run_git("diff", "HEAD~1", "--name-status")
    if result.returncode != 0:
        return 0
    count = 0
    for line in result.stdout.splitlines():
        if not line:
            continue
        status, _, path = line.partition("\t")
        if status[:1] not in ("A", "D"):
            continue
        if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        count += 1
    return count


def _modified_count() -> int:
    """Number of files modified in the latest commit (any status, excludes generated)."""
    if not _has_previous_commit():
        return 0
    result = run_git("diff", "HEAD~1", "--name-only")
    if result.returncode != 0:
        return 0
    return sum(
        1 for p in result.stdout.splitlines()
        if p and not any(p.startswith(pre) for pre in EXCLUDE_PREFIXES)
    )


def _last_commit_message() -> str:
    result = run_git("log", "-1", "--pretty=%s")
    return result.stdout.strip() if result.returncode == 0 else ""


def _do_update(reason: str) -> int:
    if not graphify_available():
        echo("⚠️  GraphStack: graphify not found. Install: pip install graphifyy")
        return 0
    echo(f"🧠 GraphStack: updating graph ({reason})...")
    try:
        proc = subprocess.run(
            ["graphify", ".", "--update", "--quiet"],
            check=False,
        )
    except OSError as exc:
        echo(f"⚠️  GraphStack: graphify failed to launch ({exc}).")
        return 0

    if proc.returncode != 0:
        echo("⚠️  GraphStack: graphify update failed. Run /graphify --update manually.")
        return 0

    for artifact in (GRAPH_REPORT, GRAPH_JSON, GRAPH_HTML):
        if artifact.is_file():
            run_git("add", str(artifact))
    echo(f"✅ GraphStack: Graph updated ({reason}) and staged.")
    return 0


def run_hook() -> int:
    if not GRAPH_REPORT.is_file():
        echo("🧠 GraphStack: No graph yet. Run /graphify . manually after first build.")
        return 0

    structural = _structural_changes_count()
    if structural > 0:
        echo(f"🧠 GraphStack: {structural} file(s) added/deleted — updating graph...")
        return _do_update(f"structural ({structural} files)")

    msg = _last_commit_message()
    if SHIP_COMMIT_PATTERN.search(msg):
        echo("🧠 GraphStack: Ship commit detected — updating graph...")
        return _do_update("ship commit")

    age_seconds = file_mtime_seconds(GRAPH_REPORT)
    if age_seconds is not None:
        age_hours = (int(time.time()) - age_seconds) // 3600
        if age_hours > STALE_GRAPH_HOURS:
            echo(f"🧠 GraphStack: Graph is {age_hours}h old — updating...")
            return _do_update(f"stale ({age_hours}h)")

    changed = _modified_count()
    echo(
        f"🧠 GraphStack: {changed} file(s) modified (content only, graph current) "
        f"— no update needed. ✓"
    )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="graphstack hook",
        description="Run the GraphStack post-commit hook logic.",
    )


def run(argv: list[str]) -> int:
    _build_parser().parse_args(argv)
    return run_hook()


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
