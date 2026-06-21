"""GraphCraft design cycle — extends GraphStack with design phases."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from ..constants import DOING_DIR, STATE_JSON
from ..design_audit import run_design_audit
from ..design_brief_utils import design_brief_is_ready, set_design_brief_status
from ..design_state import design_is_ready, save_design_state

_GRAPHSTACK = [sys.executable, "-m", "graphstack", "cycle"]


def _require_doing(root: Path, task_id: str) -> bool:
    if not (root / DOING_DIR / f"{task_id}.json").is_file():
        print(f"Task '{task_id}' not in doing/ — run: graphstack cycle start {task_id} \"title\"")
        return False
    return True


def _delegate(action: str, task_id: str) -> int:
    return subprocess.run([*_GRAPHSTACK, action, task_id], check=False).returncode


def _enter_design_phase(root: Path, task_id: str, phase: str, note: str) -> int:
    if not _require_doing(root, task_id):
        return 1
    save_design_state(phase, task_id, root=root, note=note)
    print(f"Design phase: {phase} (task={task_id})")
    return 0


def cmd_enter_design_strategist(root: Path, task_id: str) -> int:
    return _enter_design_phase(
        root,
        task_id,
        "design-strategist",
        "Write handoff/AESTHETIC_BRIEF.md + research/INSPIRATION.md",
    )


def cmd_enter_designer(root: Path, task_id: str) -> int:
    return _enter_design_phase(
        root,
        task_id,
        "designer",
        "Update design/, design-system/; run graphcraft design update .",
    )


def cmd_enter_design_audit(root: Path, task_id: str) -> int:
    if not _require_doing(root, task_id):
        return 1
    result = run_design_audit(root)
    print(f"Design audit: {result['overall']}")
    for name, status in (result.get("checks") or {}).items():
        print(f"  {name}: {status}")
    for issue in result.get("issues") or []:
        print(f"  ISSUE: {issue}")

    ready = result["overall"] in ("PASS", "WARN")
    if ready:
        set_design_brief_status("Ready for Builder", root)
        save_design_state(
            "ready",
            task_id,
            root=root,
            design_ready=True,
            note="Design audit complete",
            checks=result.get("checks"),
        )
        print("DESIGN_BRIEF -> Ready for Builder")
        print(f"Next: graphcraft cycle enter-builder {task_id}")
    else:
        save_design_state(
            "design-audit",
            task_id,
            root=root,
            design_ready=False,
            note="Design audit failed",
            checks=result.get("checks"),
        )
    return 0 if ready else 1


def cmd_enter_visual_review(root: Path, task_id: str) -> int:
    if not _require_doing(root, task_id):
        return 1
    save_design_state(
        "visual-review",
        task_id,
        root=root,
        note="Run graphcraft visual review .",
    )
    proc = subprocess.run(
        [sys.executable, "-m", "graphcraft", "visual", "review", str(root)],
        check=False,
    )
    print(f"Design phase: visual-review (exit={proc.returncode})")
    return proc.returncode


def cmd_enter_builder(root: Path, task_id: str) -> int:
    from ..gate_cmd import design_gate_enabled, MSG_DESIGN_NOT_READY

    if design_gate_enabled(root) and not design_is_ready(root) and not design_brief_is_ready(root):
        print(MSG_DESIGN_NOT_READY)
        print(f"Run: graphcraft cycle enter-design-audit {task_id}")
        return 1
    return _delegate("enter-builder", task_id)


def cmd_status(root: Path) -> int:
    from ..design_state import load_design_state

    gs_state = None
    if (root / STATE_JSON).is_file():
        try:
            gs_state = json.loads((root / STATE_JSON).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            gs_state = None

    ds = load_design_state(root)
    print("GraphCraft cycle status")
    if gs_state:
        print(f"  graphstack role={gs_state.get('role')} task={gs_state.get('task_id')}")
    else:
        print("  graphstack: (no STATE.json)")
    if ds:
        print(
            f"  design phase={ds.get('phase')} ready={ds.get('design_ready')} "
            f"task={ds.get('task_id')}"
        )
    else:
        print("  design: (no DESIGN_STATE.json)")
    return 0


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(
            "Usage: graphcraft cycle "
            "<start|enter-design-strategist|enter-designer|enter-design-audit|"
            "enter-visual-review|enter-builder|enter-reviewer|enter-qa|enter-ship|close|status> ..."
        )
        return 0

    action = argv[0]
    rest = argv[1:]
    p = argparse.ArgumentParser(prog=f"graphcraft cycle {action}")
    p.add_argument("task_id", nargs="?", default=None)
    p.add_argument("title", nargs="*", help="for cycle start only")
    p.add_argument("--force", action="store_true", help="passed to graphstack cycle close")
    args = p.parse_args(rest)
    root = Path.cwd()

    if action == "status":
        return cmd_status(root)

    if action == "start":
        if not args.task_id:
            print("Usage: graphcraft cycle start <task-id> <title...>")
            return 1
        title = " ".join(args.title) if args.title else "New task"
        rc = subprocess.run(
            [*_GRAPHSTACK, "start", args.task_id, *args.title],
            check=False,
        ).returncode
        if rc == 0:
            save_design_state("idle", args.task_id, root=root, design_ready=False, note="cycle start")
        return rc

    if not args.task_id:
        print(f"Usage: graphcraft cycle {action} <task-id>")
        return 1

    handlers = {
        "enter-design-strategist": cmd_enter_design_strategist,
        "enter-designer": cmd_enter_designer,
        "enter-design-audit": cmd_enter_design_audit,
        "enter-visual-review": cmd_enter_visual_review,
        "enter-builder": cmd_enter_builder,
    }
    if action in handlers:
        return handlers[action](root, args.task_id)

    if action in ("enter-reviewer", "enter-qa", "enter-ship"):
        return _delegate(action, args.task_id)

    if action == "close":
        cmd = [*_GRAPHSTACK, "close", args.task_id]
        if args.force:
            cmd.append("--force")
        rc = subprocess.run(cmd, check=False).returncode
        if rc == 0:
            save_design_state("idle", None, root=root, design_ready=False, note="cycle closed")
        return rc

    print(f"Unknown cycle action: {action}")
    return 1
