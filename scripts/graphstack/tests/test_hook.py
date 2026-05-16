"""Tests for the post-commit graph-update logic."""

from __future__ import annotations

from pathlib import Path

import pytest

from graphstack import hook


def test_no_graph_returns_zero_and_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    rc = hook.run_hook()
    assert rc == 0
    assert "No graph yet" in capsys.readouterr().out


def test_ship_commit_pattern_matches_real_messages() -> None:
    pat = hook.SHIP_COMMIT_PATTERN
    assert pat.search("board: complete add-rate-limit")
    assert pat.search("[ship] release v1.2.0")
    assert pat.search("ship: stable build")
    assert pat.search("SHIP: yelling counts too")
    assert not pat.search("feat: add new login flow")
    assert not pat.search("fix: typo in board readme")


def test_no_previous_commit_skips_structural_diff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When ``HEAD~1`` cannot be resolved, structural count must be 0."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(hook, "_has_previous_commit", lambda: False)
    assert hook._structural_changes_count() == 0
    assert hook._modified_count() == 0


def test_excludes_generated_paths_from_structural_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Files inside graphify-out/ or handoff/ never trigger an update by themselves."""

    class _Result:
        returncode = 0
        stdout = (
            "A\tsrc/new_module.py\n"
            "A\tgraphify-out/graph.json\n"
            "D\thandoff/STATE.md\n"
            "M\tsrc/existing.py\n"
        )

    monkeypatch.setattr(hook, "_has_previous_commit", lambda: True)
    monkeypatch.setattr(hook, "run_git", lambda *a, **kw: _Result())
    assert hook._structural_changes_count() == 1  # only src/new_module.py counts
