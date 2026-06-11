"""Tests for graphstack graph (graphify wrapper)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from graphstack import graph


def test_graphify_argv_prefers_path_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(graph.shutil, "which", lambda name: "/usr/bin/graphify" if name == "graphify" else None)
    assert graph.graphify_argv("query", "x") == ["graphify", "query", "x"]


def test_graphify_argv_falls_back_to_python_module(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(graph.shutil, "which", lambda _name: None)
    monkeypatch.setattr(graph, "find_python", lambda: ["py", "-3"])
    assert graph.graphify_argv("update", ".") == ["py", "-3", "-m", "graphify", "update", "."]


def test_graph_help_lists_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    assert graph.run(["help"]) == 0
    out = capsys.readouterr().out
    assert "query" in out
    assert "path" in out
    assert "explain" in out
    assert "update" in out


def test_graph_unknown_command() -> None:
    assert graph.run(["nope"]) == 2


def test_graph_query_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(return_value=0)
    monkeypatch.setattr(graph, "_run_graphify", mock)
    rc = graph.run(["query", "who calls main", "--budget", "500"])
    assert rc == 0
    mock.assert_called_once()
    args = mock.call_args[0][0]
    assert args[0] == "query"
    assert args[1] == "who calls main"
    assert "--budget" in args
    assert "500" in args


def test_graph_path_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(return_value=0)
    monkeypatch.setattr(graph, "_run_graphify", mock)
    graph.run(["path", "a.py", "b.py"])
    mock.assert_called_with(["path", "a.py", "b.py", "--graph", graph._default_graph()])


def test_graph_update_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(return_value=0)
    monkeypatch.setattr(graph, "_run_graphify", mock)
    graph.run(["update", ".", "--force"])
    mock.assert_called_with(["update", ".", "--force"])
