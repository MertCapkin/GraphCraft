"""Tests for the machine-readable session state (handoff/STATE.json)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphstack import state


def test_set_then_get_round_trips(project_root: Path,
                                  capsys: pytest.CaptureFixture[str]) -> None:
    assert state.run(["set", "--role", "builder", "--task", "t1",
                      "--note", "cycle 1"]) == 0
    path = project_root / "handoff" / "STATE.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["role"] == "builder"
    assert data["task_id"] == "t1"
    assert data["note"] == "cycle 1"
    assert data["updated_at"]

    capsys.readouterr()
    assert state.run(["get", "--json"]) == 0
    out = capsys.readouterr().out
    assert json.loads(out)["role"] == "builder"


def test_get_without_state_returns_error(project_root: Path,
                                         capsys: pytest.CaptureFixture[str]) -> None:
    assert state.run(["get"]) == 1
    assert "no STATE.json" in capsys.readouterr().out


def test_clear_is_idempotent(project_root: Path) -> None:
    state.run(["set", "--role", "qa"])
    assert state.run(["clear"]) == 0
    assert not (project_root / "handoff" / "STATE.json").exists()
    assert state.run(["clear"]) == 0


def test_unknown_role_still_writes_with_warning(
    project_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert state.run(["set", "--role", "wizard"]) == 0
    out = capsys.readouterr().out
    assert "Unknown role" in out
    assert (project_root / "handoff" / "STATE.json").is_file()


def test_load_state_handles_corrupt_json(project_root: Path) -> None:
    path = project_root / "handoff" / "STATE.json"
    path.write_text("{not json", encoding="utf-8")
    assert state.load_state() is None
