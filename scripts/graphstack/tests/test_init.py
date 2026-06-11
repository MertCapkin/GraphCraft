"""Tests for graphstack init (install + graph + doctor bootstrap)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from graphstack import init_cmd


def test_init_runs_install_graph_and_doctor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    rule = target / ".cursor" / "rules" / "graphstack.mdc"
    rule.parent.mkdir(parents=True)

    def _install(t: Path, *, non_interactive: bool = False) -> int:
        rule.write_text("rules", encoding="utf-8")
        return 0

    graph_mock = MagicMock(return_value=0)
    doctor_mock = MagicMock(return_value=0)

    monkeypatch.setattr(init_cmd, "install", _install)
    monkeypatch.setattr(init_cmd, "graph_update", graph_mock)
    monkeypatch.setattr(init_cmd, "run_doctor", doctor_mock)
    monkeypatch.setattr(init_cmd, "graphify_available", lambda: True)

    assert init_cmd.run([str(target), "-y"]) == 0
    assert rule.is_file()
    graph_mock.assert_called_once_with(["."])
    doctor_mock.assert_called_once()


def test_init_skips_graph_when_requested(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "proj"
    target.mkdir()

    monkeypatch.setattr(init_cmd, "install", MagicMock(return_value=0))
    graph_mock = MagicMock(return_value=0)
    monkeypatch.setattr(init_cmd, "graph_update", graph_mock)
    monkeypatch.setattr(init_cmd, "run_doctor", MagicMock(return_value=0))
    monkeypatch.setattr(init_cmd, "graphify_available", lambda: True)

    init_cmd.run([str(target), "-y", "--skip-graph"])
    graph_mock.assert_not_called()


def test_init_propagates_install_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    monkeypatch.setattr(init_cmd, "install", MagicMock(return_value=1))
    monkeypatch.setattr(init_cmd, "graph_update", MagicMock())
    monkeypatch.setattr(init_cmd, "run_doctor", MagicMock())
    assert init_cmd.run([str(target), "-y"]) == 1


def test_init_succeeds_when_doctor_fails_but_layout_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    rule = target / ".cursor" / "rules" / "graphstack.mdc"
    rule.parent.mkdir(parents=True)
    rule.write_text("rules", encoding="utf-8")

    monkeypatch.setattr(init_cmd, "install", MagicMock(return_value=0))
    monkeypatch.setattr(init_cmd, "graph_update", MagicMock(return_value=0))
    monkeypatch.setattr(init_cmd, "run_doctor", MagicMock(return_value=1))
    monkeypatch.setattr(init_cmd, "graphify_available", lambda: False)

    assert init_cmd.run([str(target), "-y", "--skip-graph"]) == 0
