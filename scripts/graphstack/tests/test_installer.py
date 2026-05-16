"""Smoke test for the installer — confirms a clean install creates expected paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from graphstack import installer


def test_install_creates_full_layout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "myproj"
    target.mkdir()

    monkeypatch.chdir(tmp_path)
    rc = installer.install(target, non_interactive=True)
    assert rc == 0

    expected_dirs = (
        ".cursor/rules",
        ".cursor/skills/architect",
        ".cursor/skills/bootstrapper",
        ".cursor/commands",
        "orchestrator",
        "handoff/board/todo",
        "handoff/board/doing",
        "handoff/board/done",
        "graphify-out",
        "scripts/graphstack",
    )
    for rel in expected_dirs:
        assert (target / rel).is_dir(), f"missing dir: {rel}"

    expected_files = (
        ".cursor/rules/graphstack.mdc",
        ".cursor/commands/graphstack.md",
        "orchestrator/ORCHESTRATOR.md",
        "orchestrator/TOKEN_OPTIMIZER.md",
        ".cursor/skills/builder/BUILDER.md",
        "handoff/board/README.md",
        "handoff/board/todo/example-task.json",
        "handoff/STATE.md",
        "scripts/board.sh",
        "scripts/board.ps1",
        "scripts/post-commit",
        "scripts/post-commit.ps1",
        "scripts/graphstack/__init__.py",
        "scripts/graphstack/board.py",
        "scripts/graphstack/installer.py",
        "scripts/graphstack/hook.py",
        "scripts/graphstack/cli.py",
        "scripts/graphstack/__main__.py",
        "handoff/board/doing/.gitkeep",
        "handoff/board/done/.gitkeep",
    )
    for rel in expected_files:
        assert (target / rel).is_file(), f"missing file: {rel}"


def test_install_does_not_overwrite_existing_brief(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    (target / "handoff").mkdir()
    (target / "handoff" / "BRIEF.md").write_text("PRESERVED", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    installer.install(target, non_interactive=True)

    assert (target / "handoff" / "BRIEF.md").read_text(encoding="utf-8") == "PRESERVED"
