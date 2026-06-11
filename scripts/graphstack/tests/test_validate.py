"""Tests for graphstack validate / doctor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphstack.validate import run_checks


def _minimal_layout(root: Path) -> None:
    paths = (
        ".cursor/rules/graphstack.mdc",
        "orchestrator/ORCHESTRATOR.md",
        "orchestrator/TOKEN_OPTIMIZER.md",
        ".cursor/skills/architect/ARCHITECT.md",
        ".cursor/skills/builder/BUILDER.md",
        "handoff/BRIEF.md",
        "handoff/STATE.md",
        "handoff/board/README.md",
        "handoff/board/todo",
        "handoff/board/doing",
        "handoff/board/done",
    )
    for rel in paths:
        p = root / rel
        if rel.endswith(("todo", "doing", "done")):
            p.mkdir(parents=True, exist_ok=True)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# stub\n", encoding="utf-8")


def test_validate_reports_template_brief_as_warning(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _minimal_layout(project_root)
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: [Feature/Change Name]\n**Status:** Draft\n",
        encoding="utf-8",
    )
    report = run_checks()
    assert any(f.code == "brief_template" and f.level == "warn" for f in report.findings)


def test_validate_strict_template_brief_is_error(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _minimal_layout(project_root)
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: [Feature/Change Name]\n",
        encoding="utf-8",
    )
    report = run_checks(strict=True)
    assert any(f.code == "brief_template" and f.level == "error" for f in report.findings)


def test_validate_invalid_board_json_is_error(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _minimal_layout(project_root)
    bad = project_root / "handoff" / "board" / "todo" / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    report = run_checks()
    assert any(f.code == "task_invalid_json" for f in report.errors)


def test_validate_task_missing_keys(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _minimal_layout(project_root)
    task = project_root / "handoff" / "board" / "doing" / "t1.json"
    task.write_text(json.dumps({"id": "t1"}), encoding="utf-8")
    report = run_checks()
    assert any(f.code == "task_missing_keys" for f in report.errors)


def test_graph_stale_when_commit_mismatch(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    from graphstack import validate as validate_mod

    _minimal_layout(project_root)
    graph_dir = project_root / "graphify-out"
    graph_dir.mkdir()
    (graph_dir / "GRAPH_REPORT.md").write_text(
        "Built from commit: `deadbeef00000000000000000000000000000000`\n",
        encoding="utf-8",
    )

    def fake_git(*args: str, capture: bool = True) -> subprocess.CompletedProcess[str]:
        if args == ("rev-parse", "HEAD"):
            return subprocess.CompletedProcess(
                args, 0, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n", ""
            )
        return subprocess.CompletedProcess(args, 1, "", "")

    monkeypatch.setattr(validate_mod, "run_git", fake_git)
    monkeypatch.setattr(validate_mod, "git_available", lambda: True)
    report = run_checks(fail_stale=True)
    assert any(f.code == "graph_stale" for f in report.errors)


def test_graph_fresh_when_built_commit_is_ancestor_of_head(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    from graphstack import validate as validate_mod

    _minimal_layout(project_root)
    graph_dir = project_root / "graphify-out"
    graph_dir.mkdir()
    old = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    head = "cccccccccccccccccccccccccccccccccccccccc"
    (graph_dir / "GRAPH_REPORT.md").write_text(
        f"Built from commit: `{old}`\n",
        encoding="utf-8",
    )

    def fake_git(*args: str, capture: bool = True) -> subprocess.CompletedProcess[str]:
        if args == ("rev-parse", "HEAD"):
            return subprocess.CompletedProcess(args, 0, f"{head}\n", "")
        if args == ("rev-parse", "HEAD~1"):
            return subprocess.CompletedProcess(args, 1, "", "unknown")
        if args[:2] == ("merge-base", "--is-ancestor"):
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:2] == ("rev-list", "--max-count"):
            return subprocess.CompletedProcess(args, 0, f"{head}\n", "")
        if args[:3] == ("log", "-1", "--format=%H"):
            return subprocess.CompletedProcess(args, 0, f"{head}\n", "")
        return subprocess.CompletedProcess(args, 1, "", "")

    monkeypatch.setattr(validate_mod, "run_git", fake_git)
    monkeypatch.setattr(validate_mod, "git_available", lambda: True)
    report = run_checks(fail_stale=True)
    assert any(f.code == "graph_fresh" for f in report.findings)
    assert not report.errors


def test_graph_fresh_when_built_from_parent_commit(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    from graphstack import validate as validate_mod

    _minimal_layout(project_root)
    graph_dir = project_root / "graphify-out"
    graph_dir.mkdir()
    parent = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    (graph_dir / "GRAPH_REPORT.md").write_text(
        f"Built from commit: `{parent}`\n",
        encoding="utf-8",
    )

    def fake_git(*args: str, capture: bool = True) -> subprocess.CompletedProcess[str]:
        if args == ("rev-parse", "HEAD"):
            return subprocess.CompletedProcess(
                args, 0, "cccccccccccccccccccccccccccccccccccccccc\n", ""
            )
        if args == ("rev-parse", "HEAD~1"):
            return subprocess.CompletedProcess(args, 0, f"{parent}\n", "")
        return subprocess.CompletedProcess(args, 1, "", "")

    monkeypatch.setattr(validate_mod, "run_git", fake_git)
    monkeypatch.setattr(validate_mod, "git_available", lambda: True)
    report = run_checks(fail_stale=True)
    assert any(f.code == "graph_fresh" for f in report.findings)
    assert not report.errors


def test_validate_framework_warns_on_dirty_handoff(project_root: Path) -> None:
    _minimal_layout(project_root)
    (project_root / ".graphstack-framework").write_text("framework\n", encoding="utf-8")
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: Real Feature\n**Status:** Ready for Builder\n",
        encoding="utf-8",
    )
    done = project_root / "handoff" / "board" / "done"
    (done / "stale-task.json").write_text(
        json.dumps({"id": "stale-task", "title": "x", "status": "done",
                    "created_at": "2026-01-01T00:00:00+00:00"}),
        encoding="utf-8",
    )
    report = run_checks()
    codes = {f.code for f in report.findings if f.level == "warn"}
    assert "framework_brief_dirty" in codes
    assert "framework_board_dirty" in codes


def test_validate_framework_clean_handoff_no_warnings(project_root: Path) -> None:
    _minimal_layout(project_root)
    (project_root / ".graphstack-framework").write_text("framework\n", encoding="utf-8")
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: [Feature/Change Name]\n**Date:** YYYY-MM-DD\n",
        encoding="utf-8",
    )
    report = run_checks()
    assert not any(f.code.startswith("framework_") for f in report.findings)
