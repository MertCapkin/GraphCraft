"""Machine-readable session state — ``handoff/STATE.json``.

Complements the human-readable ``handoff/STATE.md`` log (which stays
append-only and unchanged). The JSON file holds only the *current* state so
hooks and the process gate can verify it deterministically.

Schema: ``{"role": str, "task_id": str | None, "updated_at": str, "note": str}``
"""

from __future__ import annotations

import argparse
import json
import sys

from .constants import STATE_JSON
from .platform_utils import echo, utc_now_iso

VALID_ROLES = (
    "idle", "architect", "builder", "reviewer", "qa", "ship", "bootstrapper",
)


def load_state() -> dict | None:
    """Return the current state dict, or None if missing/unreadable."""
    try:
        return json.loads(STATE_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def save_state(role: str, task_id: str | None = None, note: str = "") -> dict:
    state = {
        "role": role,
        "task_id": task_id,
        "updated_at": utc_now_iso(),
        "note": note,
    }
    STATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return state


def cmd_set(args: argparse.Namespace) -> int:
    role = args.role.lower()
    if role not in VALID_ROLES:
        echo(f"⚠️  Unknown role '{role}' (expected one of: {', '.join(VALID_ROLES)})")
    state = save_state(role, args.task, args.note or "")
    echo(f"✅ STATE.json: role={state['role']} task={state['task_id'] or '-'}")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    state = load_state()
    if state is None:
        if args.json:
            echo("null")
        else:
            echo("(no STATE.json — run: python -m graphstack state set --role <role>)")
        return 1
    if args.json:
        echo(json.dumps(state, ensure_ascii=False))
    else:
        echo(f"role={state.get('role', '-')} task={state.get('task_id') or '-'} "
             f"updated={state.get('updated_at', '-')}")
        if state.get("note"):
            echo(f"note: {state['note']}")
    return 0


def cmd_clear(_args: argparse.Namespace) -> int:
    try:
        STATE_JSON.unlink()
        echo("✅ STATE.json cleared")
    except FileNotFoundError:
        echo("(STATE.json already absent)")
    except OSError as exc:
        echo(f"❌ Could not remove STATE.json: {exc}")
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graphstack state",
        description="Manage the machine-readable session state (handoff/STATE.json).",
    )
    sub = p.add_subparsers(dest="action", required=True)

    p_set = sub.add_parser("set", help="write current role/task state")
    p_set.add_argument("--role", required=True)
    p_set.add_argument("--task", default=None, help="board task id")
    p_set.add_argument("--note", default="", help="free-text note")

    p_get = sub.add_parser("get", help="print current state")
    p_get.add_argument("--json", action="store_true")

    sub.add_parser("clear", help="remove STATE.json")
    return p


_DISPATCH = {"set": cmd_set, "get": cmd_get, "clear": cmd_clear}


def run(argv: list[str]) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2
    return _DISPATCH[args.action](args)


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
