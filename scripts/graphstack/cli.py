"""Top-level CLI dispatcher.

Eight sub-commands:
- ``board``     — GNAP task board manager (replaces ``scripts/board.sh``)
- ``install``   — install GraphStack into a target project (replaces ``install.sh``)
- ``hook``      — post-commit graph-update logic (replaces ``scripts/post-commit``)
- ``validate``  — check handoff layout, brief, board tasks, graph freshness
- ``doctor``    — human-friendly health report (same checks as validate)
- ``run``       — execute shell commands with token-safe output compaction
- ``gate``      — deterministic process gate (check / cursor hook / claude hook)
- ``state``     — machine-readable session state (handoff/STATE.json)

Each sub-command parses its own arguments to keep the dispatcher minimal.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graphstack",
        description="GraphStack cross-platform helper (board / install / hook / validate / doctor / run).",
    )
    parser.add_argument(
        "--version", action="version", version=f"graphstack {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("board", help="GNAP board commands", add_help=False)
    sub.add_parser("install", help="Install GraphStack into a project", add_help=False)
    sub.add_parser("hook", help="Run the post-commit hook logic", add_help=False)
    sub.add_parser("validate", help="Validate handoff and graph layout", add_help=False)
    sub.add_parser("doctor", help="Project health report", add_help=False)
    sub.add_parser("run", help="Run shell command with compact output", add_help=False)
    sub.add_parser("gate", help="Process gate (check / hook adapters)", add_help=False)
    sub.add_parser("state", help="Session state (handoff/STATE.json)", add_help=False)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for both ``python -m graphstack`` and unit tests."""
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        _build_parser().print_help()
        return 0
    if args[0] == "--version":
        print(f"graphstack {__version__}")
        return 0

    cmd, rest = args[0], args[1:]

    if cmd == "board":
        from .board import run as board_run
        return board_run(rest)
    if cmd == "install":
        from .installer import run as install_run
        return install_run(rest)
    if cmd == "hook":
        from .hook import run as hook_run
        return hook_run(rest)
    if cmd == "validate":
        from .validate import run_validate
        return run_validate(rest)
    if cmd == "doctor":
        from .validate import run_doctor
        return run_doctor(rest)
    if cmd == "run":
        from .run import run as run_cmd
        return run_cmd(rest)
    if cmd == "gate":
        from .gate import run as gate_run
        return gate_run(rest)
    if cmd == "state":
        from .state import run as state_run
        return state_run(rest)

    print(f"Unknown command: {cmd}", file=sys.stderr)
    _build_parser().print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
