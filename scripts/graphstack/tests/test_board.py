"""Round-trip tests for the GNAP board lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphstack import board


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_status_empty_board(project_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = board.run(["status"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Todo: 0" in captured.out
    assert "(no tasks yet)" in captured.out


def test_new_task_creates_file(project_root: Path) -> None:
    rc = board.run(["new", "add-oauth", "Add", "OAuth", "login"])
    assert rc == 0
    task_path = project_root / "handoff" / "board" / "todo" / "add-oauth.json"
    assert task_path.is_file()
    data = _read(task_path)
    assert data["id"] == "add-oauth"
    assert data["title"] == "Add OAuth login"
    assert data["status"] == "todo"
    assert data["assigned_to"] is None


def test_new_task_rejects_duplicates(project_root: Path) -> None:
    assert board.run(["new", "dup", "First"]) == 0
    assert board.run(["new", "dup", "Second"]) == 1


def test_full_lifecycle_todo_to_done(project_root: Path) -> None:
    assert board.run(["new", "rate-limit", "Add", "rate", "limiting"]) == 0

    todo = project_root / "handoff" / "board" / "todo" / "rate-limit.json"
    doing = project_root / "handoff" / "board" / "doing" / "rate-limit.json"
    done = project_root / "handoff" / "board" / "done" / "rate-limit.json"

    assert todo.is_file()

    assert board.run(["claim", "rate-limit", "builder"]) == 0
    assert not todo.exists()
    assert doing.is_file()
    claimed = _read(doing)
    assert claimed["status"] == "doing"
    assert claimed["assigned_to"] == "builder"
    assert claimed["started_at"] is not None

    assert board.run(["complete", "rate-limit"]) == 0
    assert not doing.exists()
    assert done.is_file()
    completed = _read(done)
    assert completed["status"] == "done"
    assert completed["completed_at"] is not None


def test_claim_missing_task_returns_error(project_root: Path) -> None:
    assert board.run(["claim", "ghost", "builder"]) == 1


def test_claim_already_doing_is_idempotent(project_root: Path) -> None:
    board.run(["new", "twice", "Do", "it", "once"])
    board.run(["claim", "twice", "builder"])
    rc = board.run(["claim", "twice", "builder"])
    assert rc == 0  # already-claimed path returns 0 with a warning


def test_complete_already_done_is_idempotent(project_root: Path) -> None:
    board.run(["new", "loop", "Loop", "task"])
    board.run(["claim", "loop", "qa"])
    board.run(["complete", "loop"])
    rc = board.run(["complete", "loop"])
    assert rc == 0


def test_status_lists_tasks_in_each_column(
    project_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    board.run(["new", "a", "Task", "A"])
    board.run(["new", "b", "Task", "B"])
    board.run(["new", "c", "Task", "C"])
    board.run(["claim", "b", "builder"])
    board.run(["claim", "c", "reviewer"])
    board.run(["complete", "c"])

    rc = board.run(["status"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Todo: 1" in out
    assert "In Progress: 1" in out
    assert "Done: 1" in out
    assert "a" in out and "b" in out and "c" in out


def test_help_prints_usage(capsys: pytest.CaptureFixture[str]) -> None:
    rc = board.run([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "GraphStack Board" in out
    assert "status" in out
    assert "claim" in out


def test_reopen_done_to_todo(project_root: Path) -> None:
    board.run(["new", "fix-bug", "Fix", "production", "bug"])
    board.run(["claim", "fix-bug", "builder"])
    board.run(["complete", "fix-bug"])

    done = project_root / "handoff" / "board" / "done" / "fix-bug.json"
    todo = project_root / "handoff" / "board" / "todo" / "fix-bug.json"
    assert done.is_file()

    assert board.run(["reopen", "fix-bug", "--to", "todo"]) == 0
    assert not done.exists()
    assert todo.is_file()
    data = _read(todo)
    assert data["status"] == "todo"
    assert data["assigned_to"] is None
    assert data["completed_at"] is None


def test_reopen_done_to_doing(project_root: Path) -> None:
    board.run(["new", "hotfix", "Hotfix"])
    board.run(["claim", "hotfix", "builder"])
    board.run(["complete", "hotfix"])

    doing = project_root / "handoff" / "board" / "doing" / "hotfix.json"
    assert board.run(["reopen", "hotfix", "--to", "doing"]) == 0
    assert doing.is_file()
    assert _read(doing)["status"] == "doing"


def test_list_done_empty(project_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = board.run(["list-done"])
    assert rc == 0
    assert "(none)" in capsys.readouterr().out


def test_list_done_shows_completed(project_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    board.run(["new", "a", "Task", "A"])
    board.run(["claim", "a", "builder"])
    board.run(["complete", "a"])
    board.run(["new", "b", "Task", "B"])
    board.run(["claim", "b", "qa"])
    board.run(["complete", "b"])

    board.run(["list-done", "--limit", "1"])
    out = capsys.readouterr().out
    assert "b" in out
    assert "Showing 1 task" in out


def test_unicode_title_is_preserved(project_root: Path) -> None:
    board.run(["new", "tr", "Türkçe", "başlık", "ışık"])
    task = _read(project_root / "handoff" / "board" / "todo" / "tr.json")
    assert task["title"] == "Türkçe başlık ışık"
