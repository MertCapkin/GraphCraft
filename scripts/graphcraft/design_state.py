"""Machine-readable design cycle state — handoff/DESIGN_STATE.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import DESIGN_STATE_JSON

DESIGN_PHASES = (
    "idle",
    "design-strategist",
    "designer",
    "design-audit",
    "ready",
    "visual-review",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_design_state(root: Path | None = None) -> dict[str, Any] | None:
    path = DESIGN_STATE_JSON if root is None else root / DESIGN_STATE_JSON
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def save_design_state(
    phase: str,
    task_id: str | None,
    *,
    root: Path | None = None,
    design_ready: bool | None = None,
    note: str = "",
    checks: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = DESIGN_STATE_JSON if root is None else root / DESIGN_STATE_JSON
    state: dict[str, Any] = {
        "phase": phase,
        "task_id": task_id,
        "updated_at": _utc_now(),
        "note": note,
    }
    if design_ready is not None:
        state["design_ready"] = design_ready
    if checks is not None:
        state["checks"] = checks
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return state


def design_is_ready(root: Path | None = None) -> bool:
    state = load_design_state(root)
    if state is None:
        return False
    if state.get("design_ready") is True:
        return True
    return str(state.get("phase")) == "ready"
