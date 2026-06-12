"""Atomic GraphStack cycle commands — board + state + brief in one step."""

from __future__ import annotations

import argparse
import sys

from . import board
from .brief_utils import (
    BRIEF_PATH,
    brief_is_draft,
    brief_is_ready_for_builder,
    brief_is_template,
    read_brief_text,
    set_brief_status,
)
from .platform_utils import echo
from .state import save_state


def cmd_start(args: argparse.Namespace) -> int:
    """Create board task, set BRIEF to Draft, enter architect role."""
    title_parts = args.title if args.title else ["New task"]
    rc = board.cmd_new(argparse.Namespace(task_id=args.task_id, title=title_parts))
    title = " ".join(title_parts)
    if rc != 0:
        return rc

    if not BRIEF_PATH.is_file():
        BRIEF_PATH.parent.mkdir(parents=True, exist_ok=True)
        BRIEF_PATH.write_text(
            "# Brief: cycle\n\n**Status:** Draft\n\n## Objective\n\n> TBD\n",
            encoding="utf-8",
        )
    elif not set_brief_status("Draft"):
        echo("⚠️  Could not update handoff/BRIEF.md status — set **Status:** Draft manually")

    save_state("architect", args.task_id, f"cycle start: {title}")
    echo("")
    echo("Cycle started.")
    echo(f"  Task: {args.task_id}")
    echo(f"  Role: architect (STATE.json updated)")
    echo("")
    echo("Next steps:")
    echo("  1. Architect writes handoff/BRIEF.md (set Status: Ready for Builder)")
    echo(f"  2. python -m graphstack cycle enter-builder {args.task_id}")
    return 0


def cmd_enter_builder(args: argparse.Namespace) -> int:
    """Claim task as builder after brief is ready."""
    text = read_brief_text()
    if text is None:
        echo("❌ handoff/BRIEF.md not found")
        return 1
    if brief_is_template(text):
        echo("❌ BRIEF.md is still the template — Architect must write the brief first")
        return 1
    if brief_is_draft():
        echo("❌ BRIEF.md status is Draft — set **Status:** Ready for Builder first")
        return 1
    if not brief_is_ready_for_builder():
        echo("❌ BRIEF.md is not Ready for Builder — Architect must finalize the brief")
        return 1

    rc = board.cmd_claim(
        argparse.Namespace(task_id=args.task_id, role="builder")
    )
    if rc != 0:
        return rc

    save_state("builder", args.task_id, "cycle enter-builder")
    echo("✅ Builder role active — code edits are now allowed by the process gate")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graphstack cycle",
        description="Start or advance a GraphStack development cycle.",
    )
    sub = p.add_subparsers(dest="action", required=True)

    p_start = sub.add_parser(
        "start",
        help="board new + BRIEF Draft + state architect",
    )
    p_start.add_argument("task_id", help="board task id (e.g. email-verify)")
    p_start.add_argument("title", nargs="*", help="task title")

    p_builder = sub.add_parser(
        "enter-builder",
        help="claim task as builder after BRIEF is Ready for Builder",
    )
    p_builder.add_argument("task_id", help="board task id to claim")

    return p


_DISPATCH = {"start": cmd_start, "enter-builder": cmd_enter_builder}


def run(argv: list[str]) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2
    return _DISPATCH[args.action](args)


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
