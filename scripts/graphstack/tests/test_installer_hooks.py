"""Installer hook merge behaviour."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphstack.installer import merge_claude_settings, merge_cursor_hooks


def test_merge_cursor_hooks_appends_without_duplicates() -> None:
    existing = {
        "version": 1,
        "hooks": {
            "preToolUse": [{"command": "echo custom", "matcher": "Shell"}],
        },
    }
    payload = {
        "version": 1,
        "hooks": {
            "preToolUse": [
                {"command": "bash scripts/gate-hook.sh cursor", "matcher": "Write|Edit"},
            ],
            "stop": [{"command": "bash scripts/gate-hook.sh cursor"}],
        },
    }
    merged = merge_cursor_hooks(existing, payload)
    pretool = merged["hooks"]["preToolUse"]
    assert len(pretool) == 2
    assert any("gate-hook" in e["command"] for e in pretool)
    assert any("echo custom" in e["command"] for e in pretool)
    assert len(merged["hooks"]["stop"]) == 1


def test_install_merges_existing_hooks_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from graphstack import installer

    target = tmp_path / "proj"
    target.mkdir()
    hooks = target / ".cursor" / "hooks.json"
    hooks.parent.mkdir(parents=True)
    hooks.write_text(
        json.dumps({"version": 1, "hooks": {"stop": [{"command": "echo hi"}]}}),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    installer.install(target, non_interactive=True)

    data = json.loads(hooks.read_text(encoding="utf-8"))
    assert "gate-hook" in json.dumps(data)
    assert any("echo hi" in e.get("command", "") for e in data["hooks"]["stop"])


def test_merge_claude_settings_preserves_existing() -> None:
    existing = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo x"}]}]}}
    payload = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Edit",
                    "hooks": [{"type": "command", "command": "bash scripts/gate-hook.sh claude"}],
                }
            ]
        }
    }
    merged = merge_claude_settings(existing, payload)
    assert "PreToolUse" in merged["hooks"]
    assert "Stop" in merged["hooks"]
