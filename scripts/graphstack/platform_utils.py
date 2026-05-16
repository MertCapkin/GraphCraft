"""OS-agnostic helpers: python detection, git wrappers, console output.

The package intentionally avoids any third-party dependencies — only the
Python standard library is used so that a fresh ``pip install graphifyy``
already covers all runtime requirements.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"


def _reconfigure_stdout() -> None:
    """Make stdout/stderr tolerant of Unicode on Windows code pages.

    Many Windows shells default to cp1252/cp1254 which cannot represent box
    drawing characters or emoji. Python 3.7+ exposes ``reconfigure`` so we
    can switch to UTF-8 with replacement mode and never crash on output.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            try:
                reconfigure(errors="replace")
            except (OSError, ValueError):
                pass


_reconfigure_stdout()


def find_python() -> list[str]:
    """Return the argv prefix to launch a Python interpreter.

    Order: ``python3`` → ``python`` → ``py -3``. Returns the first one that
    actually exists on PATH. Falls back to ``sys.executable`` if nothing is
    discoverable (we are obviously running under one already).
    """
    for name in ("python3", "python"):
        if shutil.which(name):
            return [name]
    if IS_WINDOWS and shutil.which("py"):
        return ["py", "-3"]
    return [sys.executable]


def run_git(*args: str, capture: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git subcommand without ever raising on non-zero exit.

    Returns the CompletedProcess so callers can decide what to do with
    stdout/stderr. Mirrors the silent-fail behaviour of the original bash
    scripts (``2>/dev/null || true``).
    """
    return subprocess.run(
        ["git", *args],
        capture_output=capture,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )


def git_available() -> bool:
    return shutil.which("git") is not None


def graphify_available() -> bool:
    return shutil.which("graphify") is not None


def utc_now_iso() -> str:
    """ISO 8601 timestamp in UTC, second precision (matches old shell output)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def file_mtime_seconds(path: Path) -> int | None:
    try:
        return int(path.stat().st_mtime)
    except OSError:
        return None


def emoji_safe(text: str) -> str:
    """Return ``text`` unchanged on UTF-8 capable stdouts, ASCII-flatten otherwise.

    Windows ``cmd.exe`` defaults to cp1252 and chokes on emoji. We detect
    the encoding once and downgrade if needed instead of crashing the user.
    """
    encoding = (sys.stdout.encoding or "").lower()
    if "utf" in encoding:
        return text
    replacements = {
        "🧠": "[*]", "📋": "[#]", "📁": "[+]", "🤖": "[~]", "🎭": "[~]",
        "🚀": "[>]", "📝": "[w]", "📚": "[b]", "🔗": "[L]", "🎉": "[!]",
        "✅": "[ok]", "❌": "[x]", "⚠️": "[!]", "⏭️": "[-]", "🟢": "[+]",
        "🔄": "[~]", "📜": "[H]", "✓": "[ok]", "✗": "[x]",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def echo(message: str = "") -> None:
    """``print`` with emoji-safe fallback. Always flushes for shim transparency.

    Defensive against encoding errors: if the runtime locale still cannot
    encode the message (older Pythons or odd ``cmd.exe`` configurations),
    we fall back to an ASCII transliteration via ``encode(errors='replace')``.
    """
    safe = emoji_safe(message)
    try:
        print(safe, flush=True)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        ascii_only = safe.encode(encoding, errors="replace").decode(encoding, errors="replace")
        print(ascii_only, flush=True)
