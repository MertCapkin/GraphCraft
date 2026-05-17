"""Route argv to the right compactor."""

from __future__ import annotations

from .base import CompactResult, safe_compact
from .generic import compact_generic, compact_pytest
from .git import compact_git_diff, compact_git_log, compact_git_status


def _normalize_argv(argv: list[str]) -> list[str]:
    return [a for a in argv if a]


def compact_command_output(argv: list[str], raw_stdout: str, raw_stderr: str = "") -> CompactResult:
    """Compact *raw_stdout* for the given command argv. stderr is appended verbatim."""
    argv = _normalize_argv(argv)
    combined_for_match = " ".join(argv).lower()
    stdout = raw_stdout or ""

    if not argv:
        return CompactResult(stdout.rstrip("\n"), "passthrough", fell_back_to_raw=True)

    name = argv[0].lower()
    sub = argv[1].lower() if len(argv) > 1 else ""

    if name in ("git", "git.exe") and sub == "status":
        compacted = compact_git_status(stdout)
        result = safe_compact(stdout, "git-status", compacted)
    elif name in ("git", "git.exe") and sub == "diff":
        compacted = compact_git_diff(stdout)
        result = safe_compact(stdout, "git-diff", compacted)
    elif name in ("git", "git.exe") and sub in ("log", "reflog"):
        compacted = compact_git_log(stdout)
        result = safe_compact(stdout, "git-log", compacted)
    elif name in ("pytest", "pytest.exe") or "pytest" in combined_for_match:
        compacted = compact_pytest(stdout)
        result = safe_compact(stdout, "pytest", compacted)
    else:
        compacted = compact_generic(stdout)
        result = safe_compact(stdout, "generic", compacted)

    if raw_stderr.strip():
        suffix = raw_stderr.rstrip("\n")
        text = result.text + ("\n" if result.text else "") + suffix
        return CompactResult(text, result.used_compactor, result.fell_back_to_raw)

    return result
