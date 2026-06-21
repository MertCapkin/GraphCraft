"""GraphCraft design gate — UI implementation path enforcement."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from .constants import DESIGN_GATE_OFF_FILE
from .design_brief_utils import design_brief_is_ready
from .design_state import design_is_ready

UI_IMPLEMENTATION_PREFIXES = (
    "packages/ui-core/",
)

MSG_DESIGN_NOT_READY = (
    "GraphCraft design gate: UI library edits require design phase=ready. "
    "Run: graphcraft cycle enter-design-strategist → enter-designer → "
    "enter-design-audit, then graphcraft cycle enter-builder."
)


def design_gate_enabled(root: Path | None = None) -> bool:
    if os.environ.get("GRAPHCRAFT_DESIGN_GATE", "").lower() in ("off", "0", "false"):
        return False
    root = (root or Path.cwd()).resolve()
    if (root / DESIGN_GATE_OFF_FILE).is_file():
        return False
    if yaml is None:
        return True
    cfg_path = root / "graphcraft.config.yaml"
    if not cfg_path.is_file():
        return True
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return True
    gates = data.get("gates") or {}
    return bool(gates.get("require_design_approval", True))


def is_ui_implementation_path(path: str) -> bool:
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return any(p.startswith(prefix) for prefix in UI_IMPLEMENTATION_PREFIXES)


def evaluate_design_file_edit(file_path: str, root: Path | None = None) -> tuple[bool, str | None]:
    root = (root or Path.cwd()).resolve()
    if not design_gate_enabled(root):
        return True, None
    if not is_ui_implementation_path(file_path):
        return True, None
    if design_is_ready(root) or design_brief_is_ready(root):
        return True, None
    return False, MSG_DESIGN_NOT_READY


def evaluate_design_pretooluse(
    tool_name: str, tool_input: dict, root: Path | None = None
) -> tuple[bool, str | None]:
    write_tools = {"Write", "Edit", "Delete", "TabWrite", "MultiEdit", "NotebookEdit"}
    if tool_name.strip() not in write_tools:
        return True, None
    for key in ("file_path", "path", "target_file"):
        val = tool_input.get(key)
        if val:
            return evaluate_design_file_edit(str(val), root)
    return True, None


def _read_stdin_json() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def _emit(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def _cursor_deny(reason: str) -> None:
    _emit({"permission": "deny", "user_message": reason, "agent_message": reason})


def hook_cursor(root: Path | None = None) -> int:
    """Return 2 on design deny (stop hook chain), 0 on allow (continue to GraphStack gate)."""
    root = (root or Path.cwd()).resolve()
    try:
        data = _read_stdin_json()
        event = data.get("hook_event_name", "")

        if event == "preToolUse":
            allow, reason = evaluate_design_pretooluse(
                str(data.get("tool_name", "")),
                data.get("tool_input") or {},
                root,
            )
            if not allow:
                _cursor_deny(reason or MSG_DESIGN_NOT_READY)
                return 2

        return 0
    except Exception as exc:
        print(f"graphcraft gate: internal error: {exc}", file=sys.stderr)
        return 0


def run_check(root: Path) -> int:
    if not design_gate_enabled(root):
        print("Design gate: disabled")
        return 0
    if design_is_ready(root) or design_brief_is_ready(root):
        print("Design gate: ready")
        return 0
    print(f"  ISSUE: Design not ready for UI implementation edits")
    return 1


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: graphcraft gate <check|hook> [cursor]")
        return 0
    cmd, rest = argv[0], argv[1:]
    root = Path.cwd().resolve()

    if cmd == "check":
        return run_check(root)

    if cmd == "hook":
        platform = rest[0] if rest else "cursor"
        if platform == "cursor":
            return hook_cursor(root)
        print(f"Unknown hook platform: {platform}")
        return 1

    print(f"Unknown gate subcommand: {cmd}")
    return 1
