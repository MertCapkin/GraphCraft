"""Shared pytest fixtures for the graphstack package."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide an isolated, writable directory and chdir into it.

    All board operations are resolved relative to ``cwd`` so each test gets a
    pristine handoff/board layout without touching the real repository.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "handoff" / "board" / "todo").mkdir(parents=True)
    (tmp_path / "handoff" / "board" / "doing").mkdir(parents=True)
    (tmp_path / "handoff" / "board" / "done").mkdir(parents=True)
    return tmp_path


@pytest.fixture(autouse=True)
def _disable_git_in_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent any board command from creating real git commits during tests."""
    from graphstack import board

    monkeypatch.setattr(board, "_git_commit_board", lambda _msg: None)
