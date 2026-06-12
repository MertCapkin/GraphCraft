"""Doctor/validate cycle_unclosed warnings."""

from __future__ import annotations

import json
from pathlib import Path

from graphstack import state
from graphstack.validate import run_checks


def _make_doing(project_root: Path, task_id: str = "t1") -> None:
    doing = project_root / "handoff" / "board" / "doing"
    doing.mkdir(parents=True, exist_ok=True)
    (doing / f"{task_id}.json").write_text(
        json.dumps({"id": task_id, "title": "x", "status": "doing",
                    "created_at": "2000-01-01T00:00:00+00:00",
                    "started_at": "2000-01-01T00:00:00+00:00"}),
        encoding="utf-8",
    )


def test_doctor_warns_cycle_unclosed(project_root: Path) -> None:
    _make_doing(project_root)
    state.run(["set", "--role", "builder", "--task", "t1"])
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: X\n**Status:** Ready for Builder\n", encoding="utf-8"
    )
    report = run_checks()
    codes = [f.code for f in report.findings if f.level == "warn"]
    assert "cycle_unclosed" in codes
