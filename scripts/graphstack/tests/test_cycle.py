"""Tests for graphstack cycle commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphstack import cycle


def test_cycle_start_creates_task_and_architect_state(project_root: Path) -> None:
    assert cycle.run(["start", "email-verify", "Add", "email", "verification"]) == 0
    todo = project_root / "handoff" / "board" / "todo" / "email-verify.json"
    assert todo.is_file()
    data = json.loads(todo.read_text(encoding="utf-8"))
    assert data["status"] == "todo"
    assert "email verification" in data["title"].lower()

    brief = (project_root / "handoff" / "BRIEF.md").read_text(encoding="utf-8")
    assert "**Status:** Draft" in brief

    st = json.loads((project_root / "handoff" / "STATE.json").read_text(encoding="utf-8"))
    assert st["role"] == "architect"
    assert st["task_id"] == "email-verify"


def test_enter_builder_requires_ready_brief(project_root: Path) -> None:
    cycle.run(["start", "feat-a", "Feature", "A"])
    rc = cycle.run(["enter-builder", "feat-a"])
    assert rc == 1


def test_enter_builder_claims_task(project_root: Path) -> None:
    cycle.run(["start", "feat-b", "Feature", "B"])
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: B\n**Status:** Ready for Builder\n## Objective\nShip it.\n",
        encoding="utf-8",
    )
    assert cycle.run(["enter-builder", "feat-b"]) == 0
    assert (project_root / "handoff" / "board" / "doing" / "feat-b.json").is_file()
    st = json.loads((project_root / "handoff" / "STATE.json").read_text(encoding="utf-8"))
    assert st["role"] == "builder"


def test_cycle_close_requires_review_verdict(project_root: Path) -> None:
    cycle.run(["start", "feat-c", "Feature", "C"])
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: C\n**Status:** Ready for Builder\n", encoding="utf-8"
    )
    cycle.run(["enter-builder", "feat-c"])
    assert cycle.run(["close", "feat-c"]) == 1
    assert (project_root / "handoff" / "board" / "doing" / "feat-c.json").is_file()


def test_enter_reviewer_sets_role(project_root: Path) -> None:
    cycle.run(["start", "feat-r", "Feature", "R"])
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: R\n**Status:** Ready for Builder\n", encoding="utf-8"
    )
    cycle.run(["enter-builder", "feat-r"])
    assert cycle.run(["enter-reviewer", "feat-r"]) == 0
    st = json.loads((project_root / "handoff" / "STATE.json").read_text(encoding="utf-8"))
    assert st["role"] == "reviewer"


def test_enter_qa_requires_approved_review(project_root: Path) -> None:
    cycle.run(["start", "feat-q", "Feature", "Q"])
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: Q\n**Status:** Ready for Builder\n", encoding="utf-8"
    )
    cycle.run(["enter-builder", "feat-q"])
    cycle.run(["enter-reviewer", "feat-q"])
    assert cycle.run(["enter-qa", "feat-q"]) == 1
    (project_root / "handoff" / "REVIEW.md").write_text(
        "## Review: Q\n### Verdict: Approved\n", encoding="utf-8"
    )
    assert cycle.run(["enter-qa", "feat-q"]) == 0
    st = json.loads((project_root / "handoff" / "STATE.json").read_text(encoding="utf-8"))
    assert st["role"] == "qa"


def test_enter_ship_requires_qa_pass(project_root: Path) -> None:
    cycle.run(["start", "feat-s", "Feature", "S"])
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: S\n**Status:** Ready for Builder\n", encoding="utf-8"
    )
    cycle.run(["enter-builder", "feat-s"])
    cycle.run(["enter-reviewer", "feat-s"])
    (project_root / "handoff" / "REVIEW.md").write_text(
        "## Review: S\n### Verdict: Approved\n", encoding="utf-8"
    )
    cycle.run(["enter-qa", "feat-s"])
    assert cycle.run(["enter-ship", "feat-s"]) == 1
    (project_root / "handoff" / "REVIEW.md").write_text(
        "## Review: S\n### Verdict: Approved\n\n"
        "## QA Report: S\n### Overall: PASS\n",
        encoding="utf-8",
    )
    assert cycle.run(["enter-ship", "feat-s"]) == 0
    st = json.loads((project_root / "handoff" / "STATE.json").read_text(encoding="utf-8"))
    assert st["role"] == "ship"


def test_cycle_close_moves_task_to_done(project_root: Path) -> None:
    cycle.run(["start", "feat-d", "Feature", "D"])
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: D\n**Status:** Ready for Builder\n", encoding="utf-8"
    )
    cycle.run(["enter-builder", "feat-d"])
    (project_root / "handoff" / "REVIEW.md").write_text(
        "## Review: D — 2026-06-12\n### Verdict: Approved\n\n"
        "## QA Report: D — 2026-06-12\n### Overall: ✅ PASS\n",
        encoding="utf-8",
    )
    assert cycle.run(["close", "feat-d"]) == 0
    assert (project_root / "handoff" / "board" / "done" / "feat-d.json").is_file()
    st = json.loads((project_root / "handoff" / "STATE.json").read_text(encoding="utf-8"))
    assert st["role"] == "idle"
    assert "**Status:** Complete" in (project_root / "handoff" / "BRIEF.md").read_text(encoding="utf-8")
