"""GNAP board manager — pure Python port of ``scripts/board.sh``.

JSON schema is preserved verbatim so existing ``handoff/board/*.json`` files
created under v3.0.0 continue to work without migration.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .constants import BOARD_DIR, DOING_DIR, DONE_DIR, TODO_DIR
from .platform_utils import echo, run_git, utc_now_iso

VALID_ROLES = ("architect", "builder", "reviewer", "qa", "ship", "bootstrapper")


def _load_task(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _save_task(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _get(data: dict, key: str) -> str:
    value = data.get(key)
    if value in (None, ""):
        return "-"
    return str(value)


def _print_task(path: Path) -> None:
    try:
        data = _load_task(path)
    except (OSError, json.JSONDecodeError):
        echo(f"  ! could not read {path.name}")
        return
    echo(
        f"  {_get(data, 'id'):<32} {_get(data, 'status'):<10} "
        f"{_get(data, 'assigned_to'):<12} {_get(data, 'title')}"
    )


def _iter_tasks(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.json"))


def _git_commit_board(message: str) -> None:
    """Stage the board directory and commit silently — never fails the command."""
    run_git("add", str(BOARD_DIR))
    run_git("commit", "-m", message)


def cmd_status(_args: argparse.Namespace) -> int:
    echo("")
    echo("📋 GraphStack GNAP Board")
    echo("=" * 56)
    echo(f"  {'TASK ID':<32} {'STATUS':<10} {'ASSIGNED':<12} TITLE")
    echo("  " + "-" * 54)

    todo = _iter_tasks(TODO_DIR)
    doing = _iter_tasks(DOING_DIR)
    done = _iter_tasks(DONE_DIR)

    for f in todo + doing + done:
        _print_task(f)

    if not (todo or doing or done):
        echo("  (no tasks yet)")

    echo("")
    echo(f"  Todo: {len(todo)}  |  In Progress: {len(doing)}  |  Done: {len(done)}")
    echo("")
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    task_id: str = args.task_id
    title = " ".join(args.title) if args.title else "New task"

    TODO_DIR.mkdir(parents=True, exist_ok=True)
    dst = TODO_DIR / f"{task_id}.json"
    if dst.exists():
        echo(f"❌ Task '{task_id}' already exists in todo/")
        return 1

    task = {
        "id": task_id,
        "title": title,
        "created_at": utc_now_iso(),
        "created_by": "architect",
        "brief": "handoff/BRIEF.md",
        "graph_nodes": [],
        "criteria_count": 0,
        "priority": "normal",
        "status": "todo",
        "assigned_to": None,
        "started_at": None,
        "completed_at": None,
        "notes": "",
    }
    _save_task(dst, task)
    _git_commit_board(f"board: new task {task_id} — {title}")

    echo(f"✅ Task '{task_id}' created in todo/")
    echo(f"   Title: {title}")
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    task_id: str = args.task_id
    role: str = args.role.lower()

    if role not in VALID_ROLES:
        echo(f"⚠️  Unknown role '{role}'. Continuing anyway "
             f"(expected one of: {', '.join(VALID_ROLES)})")

    src = TODO_DIR / f"{task_id}.json"
    dst = DOING_DIR / f"{task_id}.json"

    if not src.exists():
        existing = DOING_DIR / f"{task_id}.json"
        if existing.exists():
            current_role = _load_task(existing).get("assigned_to") or "?"
            echo(f"⚠️  Task '{task_id}' is already in doing/ "
                 f"(claimed by {current_role})")
            return 0
        if (DONE_DIR / f"{task_id}.json").exists():
            echo(f"⚠️  Task '{task_id}' is already done.")
            return 0
        echo(f"❌ Task '{task_id}' not found in todo/")
        echo("   Run: python -m graphstack board status")
        return 1

    data = _load_task(src)
    data["status"] = "doing"
    data["assigned_to"] = role
    data["started_at"] = utc_now_iso()
    _save_task(src, data)

    DOING_DIR.mkdir(parents=True, exist_ok=True)
    src.replace(dst)

    _git_commit_board(f"board: {role} claims {task_id}")
    echo(f"✅ Task '{task_id}' claimed by {role}")
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    task_id: str = args.task_id

    src = DOING_DIR / f"{task_id}.json"
    dst = DONE_DIR / f"{task_id}.json"

    if not src.exists():
        if (DONE_DIR / f"{task_id}.json").exists():
            echo(f"⚠️  Task '{task_id}' is already done.")
            return 0
        echo(f"❌ Task '{task_id}' not found in doing/")
        echo("   Run: python -m graphstack board status")
        return 1

    data = _load_task(src)
    data["status"] = "done"
    data["completed_at"] = utc_now_iso()
    _save_task(src, data)

    DONE_DIR.mkdir(parents=True, exist_ok=True)
    src.replace(dst)

    _git_commit_board(f"board: complete {task_id}")
    echo(f"✅ Task '{task_id}' marked complete")
    return 0


def cmd_list_done(args: argparse.Namespace) -> int:
    limit = args.limit
    done = _iter_tasks(DONE_DIR)
    if not done:
        echo("")
        echo("📋 Done tasks: (none)")
        echo("")
        return 0

    if limit is not None and limit > 0:
        done = done[-limit:]

    echo("")
    echo("📋 Done tasks")
    echo("=" * 56)
    echo(f"  {'TASK ID':<32} {'COMPLETED':<22} TITLE")
    echo("  " + "-" * 54)
    for path in done:
        try:
            data = _load_task(path)
        except (OSError, json.JSONDecodeError):
            echo(f"  ! could not read {path.name}")
            continue
        completed = _get(data, "completed_at")
        echo(f"  {_get(data, 'id'):<32} {completed:<22} {_get(data, 'title')}")
    echo("")
    echo(f"  Showing {len(done)} task(s)")
    echo("")
    return 0


def cmd_reopen(args: argparse.Namespace) -> int:
    task_id: str = args.task_id
    dest = args.to.lower()

    if dest not in ("todo", "doing"):
        echo(f"❌ Invalid destination '{dest}'. Use: todo or doing")
        return 1

    src_done = DONE_DIR / f"{task_id}.json"
    src_doing = DOING_DIR / f"{task_id}.json"
    src_todo = TODO_DIR / f"{task_id}.json"

    if src_todo.exists():
        echo(f"⚠️  Task '{task_id}' is already in todo/")
        return 0

    if src_doing.exists() and dest == "doing":
        echo(f"⚠️  Task '{task_id}' is already in doing/")
        return 0

    src: Path | None = None
    if src_done.exists():
        src = src_done
    elif src_doing.exists() and dest == "todo":
        src = src_doing
    else:
        echo(f"❌ Task '{task_id}' not found in done/ (or doing/ for todo reopen)")
        echo("   Run: python -m graphstack board list-done")
        return 1

    data = _load_task(src)
    data["status"] = dest
    data["completed_at"] = None
    if dest == "todo":
        data["assigned_to"] = None
        data["started_at"] = None
    elif data.get("started_at") is None:
        data["started_at"] = utc_now_iso()

    dst_dir = TODO_DIR if dest == "todo" else DOING_DIR
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{task_id}.json"
    _save_task(dst, data)
    src.unlink()

    _git_commit_board(f"board: reopen {task_id} -> {dest}")
    echo(f"✅ Task '{task_id}' reopened to {dest}/")
    return 0


def cmd_log(_args: argparse.Namespace) -> int:
    echo("")
    echo("📜 Board History")
    result = run_git("log", "--oneline", "--", str(BOARD_DIR))
    if result.returncode == 0 and result.stdout.strip():
        echo(result.stdout.rstrip())
    else:
        echo("(no git history yet — initialize with: git init)")
    echo("")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graphstack board",
        description="GNAP board: todo → doing → done lifecycle.",
    )
    sub = p.add_subparsers(dest="action", required=True)

    sub.add_parser("status", help="show full board status")

    p_new = sub.add_parser("new", help="create a new task in todo/")
    p_new.add_argument("task_id")
    p_new.add_argument("title", nargs="*", help="task title (no quotes needed)")

    p_claim = sub.add_parser("claim", help="move task from todo → doing")
    p_claim.add_argument("task_id")
    p_claim.add_argument("role")

    p_complete = sub.add_parser("complete", help="move task from doing → done")
    p_complete.add_argument("task_id")

    p_reopen = sub.add_parser("reopen", help="move task from done/ back to todo/ or doing/")
    p_reopen.add_argument("task_id")
    p_reopen.add_argument(
        "--to",
        default="todo",
        choices=("todo", "doing"),
        help="destination column (default: todo)",
    )

    p_list_done = sub.add_parser("list-done", help="list completed tasks only")
    p_list_done.add_argument(
        "--limit",
        type=int,
        default=None,
        help="show only the last N completed tasks",
    )

    sub.add_parser("log", help="show git history of board changes")

    return p


def _print_help() -> None:
    echo("")
    echo("GraphStack Board — Commands:")
    echo("  status                             show full board")
    echo("  new <id> <title words...>          create task (no quotes needed)")
    echo("  claim <id> <role>                  claim task (builder/reviewer/qa)")
    echo("  complete <id>                      mark done")
    echo("  reopen <id> [--to todo|doing]      move done task back to todo/doing")
    echo("  list-done [--limit N]              list completed tasks only")
    echo("  log                                git history of board")
    echo("")
    echo("Examples:")
    echo("  python -m graphstack board new add-rate-limit Add rate limiting to login")
    echo("  python -m graphstack board claim add-rate-limit builder")
    echo("  python -m graphstack board complete add-rate-limit")
    echo("")


_DISPATCH = {
    "status": cmd_status,
    "new": cmd_new,
    "claim": cmd_claim,
    "complete": cmd_complete,
    "reopen": cmd_reopen,
    "list-done": cmd_list_done,
    "log": cmd_log,
}


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("help", "-h", "--help"):
        _print_help()
        return 0
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2
    return _DISPATCH[args.action](args)


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
