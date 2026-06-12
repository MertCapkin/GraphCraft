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
    review_last_qa_shippable,
    review_last_verdict_approved,
    set_brief_status,
)
from .constants import DOING_DIR
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


def _require_doing(task_id: str) -> int | None:
    if not (DOING_DIR / f"{task_id}.json").is_file():
        echo(f"❌ Task '{task_id}' not found in doing/")
        echo("   Run: python -m graphstack board status")
        return 1
    return None


def cmd_enter_reviewer(args: argparse.Namespace) -> int:
    """Hand off Builder → Reviewer after implementation."""
    if (err := _require_doing(args.task_id)) is not None:
        return err
    rc = board.cmd_claim(argparse.Namespace(task_id=args.task_id, role="reviewer"))
    if rc != 0:
        return rc
    set_brief_status("In Review")
    save_state("reviewer", args.task_id, "cycle enter-reviewer")
    echo("✅ Reviewer role active — append handoff/REVIEW.md with Verdict")
    echo(f"   Next: python -m graphstack cycle enter-qa {args.task_id}")
    return 0


def cmd_enter_qa(args: argparse.Namespace) -> int:
    """Hand off Reviewer → QA after Verdict: Approved."""
    if (err := _require_doing(args.task_id)) is not None:
        return err
    if not review_last_verdict_approved():
        echo("❌ handoff/REVIEW.md has no 'Verdict: Approved' in the latest cycle")
        echo("   Complete Reviewer first")
        return 1
    rc = board.cmd_claim(argparse.Namespace(task_id=args.task_id, role="qa"))
    if rc != 0:
        return rc
    save_state("qa", args.task_id, "cycle enter-qa")
    echo("✅ QA role active — trace call paths and append QA Report to REVIEW.md")
    echo(f"   Next: python -m graphstack cycle enter-ship {args.task_id}")
    return 0


def cmd_enter_ship(args: argparse.Namespace) -> int:
    """Hand off QA → Ship after QA PASS/PARTIAL."""
    if (err := _require_doing(args.task_id)) is not None:
        return err
    if not review_last_verdict_approved():
        echo("❌ Reviewer must approve before Ship")
        return 1
    if not review_last_qa_shippable():
        echo("❌ handoff/REVIEW.md has no shippable QA Report (Overall: PASS or PARTIAL)")
        echo("   Complete QA first")
        return 1
    rc = board.cmd_claim(argparse.Namespace(task_id=args.task_id, role="ship"))
    if rc != 0:
        return rc
    save_state("ship", args.task_id, "cycle enter-ship")
    echo("✅ Ship role active — run checklist, then: cycle close <task-id>")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    """Complete board task and reset state after Reviewer/QA/Ship."""
    task_id: str = args.task_id
    doing_file = DOING_DIR / f"{task_id}.json"
    if not doing_file.is_file():
        echo(f"❌ Task '{task_id}' not found in doing/")
        echo("   Run: python -m graphstack board status")
        return 1

    if not args.force and not review_last_verdict_approved():
        echo("❌ handoff/REVIEW.md has no 'Verdict: Approved' in the latest cycle")
        echo("   Complete Reviewer → QA → Ship first, or use --force to close anyway")
        return 1
    if not args.force and not review_last_qa_shippable():
        echo("❌ handoff/REVIEW.md has no shippable QA Report (Overall: PASS or PARTIAL)")
        echo("   Complete QA → Ship first, or use --force to close anyway")
        return 1

    rc = board.cmd_complete(argparse.Namespace(task_id=task_id))
    if rc != 0:
        return rc

    set_brief_status("Complete")
    save_state("idle", None, f"cycle close: {task_id}")
    echo("✅ Cycle closed — task moved to done/, role=idle")
    echo("   If structural files changed, run: python -m graphstack graph update .")
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

    p_reviewer = sub.add_parser(
        "enter-reviewer",
        help="hand off Builder → Reviewer after implementation",
    )
    p_reviewer.add_argument("task_id", help="board task id in doing/")

    p_qa = sub.add_parser(
        "enter-qa",
        help="hand off Reviewer → QA after Verdict: Approved",
    )
    p_qa.add_argument("task_id", help="board task id in doing/")

    p_ship = sub.add_parser(
        "enter-ship",
        help="hand off QA → Ship after QA PASS/PARTIAL",
    )
    p_ship.add_argument("task_id", help="board task id in doing/")

    p_close = sub.add_parser(
        "close",
        help="board complete + BRIEF Complete + state idle (after Ship)",
    )
    p_close.add_argument("task_id", help="board task id in doing/")
    p_close.add_argument(
        "--force",
        action="store_true",
        help="close even without Verdict: Approved in REVIEW.md",
    )

    return p


_DISPATCH = {
    "start": cmd_start,
    "enter-builder": cmd_enter_builder,
    "enter-reviewer": cmd_enter_reviewer,
    "enter-qa": cmd_enter_qa,
    "enter-ship": cmd_enter_ship,
    "close": cmd_close,
}


def run(argv: list[str]) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2
    return _DISPATCH[args.action](args)


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
