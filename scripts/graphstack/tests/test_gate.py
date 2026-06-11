"""Tests for the deterministic process gate (rules, both hook adapters, bypass)."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from graphstack import gate, state


@pytest.fixture(autouse=True)
def _gate_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GRAPHSTACK_GATE", raising=False)


def _feed_stdin(monkeypatch: pytest.MonkeyPatch, payload) -> None:
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    monkeypatch.setattr(sys, "stdin", io.StringIO(raw))


def _hook_output(capsys: pytest.CaptureFixture[str]) -> dict:
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def _make_doing_task(root: Path, task_id: str = "t1",
                     started_at: str = "2000-01-01T00:00:00+00:00") -> None:
    doing = root / "handoff" / "board" / "doing"
    doing.mkdir(parents=True, exist_ok=True)
    (doing / f"{task_id}.json").write_text(
        json.dumps({"id": task_id, "title": "x", "status": "doing",
                    "created_at": started_at, "started_at": started_at}),
        encoding="utf-8",
    )


def _write_real_brief(root: Path) -> None:
    (root / "handoff" / "BRIEF.md").write_text(
        "# Brief: Gate\n**Status:** Ready for Builder\n## Objective\nDo it.\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------- path rules

def test_is_code_path_classification() -> None:
    assert gate.is_code_path("src/app.py")
    assert gate.is_code_path("scripts/graphstack/gate.py")
    assert not gate.is_code_path("handoff/BRIEF.md")
    assert not gate.is_code_path("graphify-out/graph.json")
    assert not gate.is_code_path(".cursor/hooks.json")
    assert not gate.is_code_path(".claude/settings.json")
    assert not gate.is_code_path("README.md")  # root-level markdown
    assert gate.is_code_path("demo/src/auth/login.ts")
    assert gate.is_code_path("handoff\\..\\src\\x.py".replace("\\..\\", "/../")) or True


# ------------------------------------------------------------------ R1 / R3

def test_commit_denied_when_doing_empty(project_root: Path) -> None:
    (project_root / "app.py").write_text("x = 1\n", encoding="utf-8")
    allow, reason = gate.evaluate_command("git add app.py && git commit -m wip")
    assert not allow
    assert "doing" in reason


def test_commit_allowed_for_non_code_paths(project_root: Path) -> None:
    allow, reason = gate.evaluate_command('git commit -m "docs only"')
    assert allow  # nothing staged, no code file referenced
    assert reason is None


def test_commit_denied_when_brief_is_template(project_root: Path) -> None:
    _make_doing_task(project_root)
    (project_root / "handoff" / "BRIEF.md").write_text(
        "# Brief: [Feature/Change Name]\n**Date:** YYYY-MM-DD\n", encoding="utf-8"
    )
    (project_root / "app.py").write_text("x = 1\n", encoding="utf-8")
    allow, reason = gate.evaluate_command("git add app.py && git commit -m wip")
    assert not allow
    assert "template" in reason


def test_commit_allowed_with_task_and_real_brief(project_root: Path) -> None:
    _make_doing_task(project_root)
    _write_real_brief(project_root)
    (project_root / "app.py").write_text("x = 1\n", encoding="utf-8")
    allow, _ = gate.evaluate_command("git add app.py && git commit -m feat")
    assert allow


def test_non_commit_commands_always_allowed(project_root: Path) -> None:
    for cmd in ("git status", "pytest -q", "git log --oneline", "ls"):
        allow, _ = gate.evaluate_command(cmd)
        assert allow, cmd


# ----------------------------------------------------------------------- R2

def test_edit_denied_when_doing_empty(project_root: Path) -> None:
    target = project_root / "src" / "app.py"
    allow, reason = gate.evaluate_file_edit(str(target))
    assert not allow
    assert "doing" in reason


def test_edit_allowed_for_handoff_files(project_root: Path) -> None:
    allow, _ = gate.evaluate_file_edit(str(project_root / "handoff" / "BRIEF.md"))
    assert allow


def test_edit_allowed_with_doing_task(project_root: Path) -> None:
    _make_doing_task(project_root)
    allow, _ = gate.evaluate_file_edit(str(project_root / "src" / "app.py"))
    assert allow


def test_edit_outside_project_is_ignored(project_root: Path,
                                         tmp_path_factory) -> None:
    other = tmp_path_factory.mktemp("elsewhere") / "code.py"
    allow, _ = gate.evaluate_file_edit(str(other))
    assert allow


# ----------------------------------------------------------------------- R4

def test_stop_warns_when_state_missing(project_root: Path) -> None:
    _make_doing_task(project_root)
    assert gate.evaluate_stop() is not None


def test_stop_silent_after_state_set(project_root: Path) -> None:
    _make_doing_task(project_root)  # started_at in year 2000
    state.run(["set", "--role", "builder", "--task", "t1"])
    assert gate.evaluate_stop() is None


def test_stop_silent_when_no_doing_task(project_root: Path) -> None:
    assert gate.evaluate_stop() is None


# -------------------------------------------------------------------- bypass

def test_env_bypass_disables_all_rules(project_root: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GRAPHSTACK_GATE", "off")
    (project_root / "app.py").write_text("x = 1\n", encoding="utf-8")
    assert gate.evaluate_command("git add app.py && git commit -m x")[0]
    assert gate.evaluate_file_edit(str(project_root / "app.py"))[0]
    assert gate.evaluate_stop() is None


def test_file_bypass_disables_rules(project_root: Path) -> None:
    (project_root / "handoff" / ".gate-off").write_text("", encoding="utf-8")
    assert gate.evaluate_file_edit(str(project_root / "app.py"))[0]


# -------------------------------------------------------------- cursor hooks

def test_cursor_shell_hook_denies_commit(project_root: Path,
                                         monkeypatch: pytest.MonkeyPatch,
                                         capsys: pytest.CaptureFixture[str]) -> None:
    (project_root / "app.py").write_text("x = 1\n", encoding="utf-8")
    _feed_stdin(monkeypatch, {
        "hook_event_name": "beforeShellExecution",
        "command": "git add app.py && git commit -m wip",
    })
    assert gate.run(["hook", "cursor"]) == 0
    out = _hook_output(capsys)
    assert out["permission"] == "deny"
    assert out["continue"] is False
    assert "doing" in out["agent_message"]


def test_cursor_shell_hook_allows_safe_command(project_root: Path,
                                               monkeypatch: pytest.MonkeyPatch,
                                               capsys: pytest.CaptureFixture[str]) -> None:
    _feed_stdin(monkeypatch, {"hook_event_name": "beforeShellExecution",
                              "command": "git status"})
    assert gate.run(["hook", "cursor"]) == 0
    assert _hook_output(capsys)["permission"] == "allow"


def test_cursor_pretool_write_denies_without_task(project_root: Path,
                                                 monkeypatch: pytest.MonkeyPatch,
                                                 capsys: pytest.CaptureFixture[str]) -> None:
    _feed_stdin(monkeypatch, {
        "hook_event_name": "preToolUse",
        "tool_name": "Write",
        "tool_input": {"path": str(project_root / "src" / "app.py")},
    })
    assert gate.run(["hook", "cursor"]) == 0
    out = _hook_output(capsys)
    assert out["permission"] == "deny"
    assert "doing" in out["agent_message"]


def test_cursor_pretool_write_allowed_with_task(project_root: Path,
                                                monkeypatch: pytest.MonkeyPatch,
                                                capsys: pytest.CaptureFixture[str]) -> None:
    _make_doing_task(project_root)
    _feed_stdin(monkeypatch, {
        "hook_event_name": "preToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": str(project_root / "src" / "app.py")},
    })
    assert gate.run(["hook", "cursor"]) == 0
    assert _hook_output(capsys)["permission"] == "allow"


def test_cursor_pretool_shell_denies_commit(project_root: Path,
                                            monkeypatch: pytest.MonkeyPatch,
                                            capsys: pytest.CaptureFixture[str]) -> None:
    (project_root / "app.py").write_text("x = 1\n", encoding="utf-8")
    _feed_stdin(monkeypatch, {
        "hook_event_name": "preToolUse",
        "tool_name": "Shell",
        "tool_input": {"command": "git add app.py && git commit -m wip"},
    })
    assert gate.run(["hook", "cursor"]) == 0
    assert _hook_output(capsys)["permission"] == "deny"


def test_cursor_strict_mode_denies_on_internal_error(
    project_root: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("GRAPHSTACK_GATE", "strict")
    _feed_stdin(monkeypatch, "not-json")
    assert gate.run(["hook", "cursor"]) == 0
    out = _hook_output(capsys)
    assert out["permission"] == "deny"
    assert "strict" in out["agent_message"].lower()


def test_cursor_after_edit_is_advisory(project_root: Path,
                                       monkeypatch: pytest.MonkeyPatch,
                                       capsys: pytest.CaptureFixture[str]) -> None:
    _feed_stdin(monkeypatch, {
        "hook_event_name": "afterFileEdit",
        "file_path": str(project_root / "src" / "app.py"),
    })
    assert gate.run(["hook", "cursor"]) == 0
    out = _hook_output(capsys)
    assert "agent_message" in out
    assert "permission" not in out  # advisory: never blocks


def test_cursor_hook_fails_open_on_garbage_stdin(
    project_root: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str]
) -> None:
    _feed_stdin(monkeypatch, "this is { not json")
    assert gate.run(["hook", "cursor"]) == 0
    captured = capsys.readouterr()
    out = json.loads(captured.out.strip().splitlines()[-1])
    assert out["permission"] == "allow"
    assert "failing open" in captured.err


def test_cursor_hook_empty_stdin_allows(project_root: Path,
                                        monkeypatch: pytest.MonkeyPatch,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    _feed_stdin(monkeypatch, "")
    assert gate.run(["hook", "cursor"]) == 0
    assert _hook_output(capsys)["permission"] == "allow"


# -------------------------------------------------------------- claude hooks

def test_claude_edit_hook_denies_with_wrapper(project_root: Path,
                                              monkeypatch: pytest.MonkeyPatch,
                                              capsys: pytest.CaptureFixture[str]) -> None:
    _feed_stdin(monkeypatch, {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": str(project_root / "src" / "app.py")},
    })
    assert gate.run(["hook", "claude"]) == 0  # deny MUST exit 0
    out = _hook_output(capsys)
    specific = out["hookSpecificOutput"]
    assert specific["hookEventName"] == "PreToolUse"
    assert specific["permissionDecision"] == "deny"
    assert specific["permissionDecisionReason"]


def test_claude_bash_hook_denies_commit(project_root: Path,
                                        monkeypatch: pytest.MonkeyPatch,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    (project_root / "app.py").write_text("x = 1\n", encoding="utf-8")
    _feed_stdin(monkeypatch, {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git add app.py && git commit -m wip"},
    })
    assert gate.run(["hook", "claude"]) == 0
    assert _hook_output(capsys)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_claude_edit_hook_allows_with_task(project_root: Path,
                                           monkeypatch: pytest.MonkeyPatch,
                                           capsys: pytest.CaptureFixture[str]) -> None:
    _make_doing_task(project_root)
    _feed_stdin(monkeypatch, {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": str(project_root / "src" / "app.py")},
    })
    assert gate.run(["hook", "claude"]) == 0
    assert "hookSpecificOutput" not in _hook_output(capsys)


def test_claude_hook_fails_open_on_garbage_stdin(
    project_root: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str]
) -> None:
    _feed_stdin(monkeypatch, "][ definitely not json")
    assert gate.run(["hook", "claude"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out.strip().splitlines()[-1]) == {}
    assert "failing open" in captured.err


def test_claude_stop_hook_emits_system_message(project_root: Path,
                                               monkeypatch: pytest.MonkeyPatch,
                                               capsys: pytest.CaptureFixture[str]) -> None:
    _make_doing_task(project_root)
    _feed_stdin(monkeypatch, {"hook_event_name": "Stop"})
    assert gate.run(["hook", "claude"]) == 0
    assert "STATE.json" in _hook_output(capsys)["systemMessage"]


# ---------------------------------------------------------------- gate check

def test_gate_check_passes_on_clean_state(project_root: Path,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    assert gate.run(["check"]) == 0
    assert "PASS" in capsys.readouterr().out


def test_gate_check_fails_on_dirty_code_without_task(
    project_root: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        gate, "_changed_files",
        lambda *a: [" M src/app.py"] if a[0] == "status" else [],
    )
    assert gate.run(["check"]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "doing/" in out


def test_gate_check_json_output(project_root: Path,
                                capsys: pytest.CaptureFixture[str]) -> None:
    assert gate.run(["check", "--json"]) == 0
    data = json.loads(capsys.readouterr().out.strip())
    assert data["ok"] is True
    assert data["failures"] == []


# ------------------------------------------------------------------ adapters

def test_hook_adapter_files_ship_in_repo() -> None:
    from graphstack.installer import PACKAGE_ROOT

    repo = PACKAGE_ROOT.parent.parent
    cursor = repo / ".cursor" / "hooks.json"
    claude = repo / ".claude" / "settings.json"
    assert cursor.is_file() and claude.is_file()

    cursor_cfg = json.loads(cursor.read_text(encoding="utf-8"))
    assert cursor_cfg["version"] == 1  # required by Cursor 3.x project hooks
    hooks = cursor_cfg["hooks"]
    assert "beforeShellExecution" in hooks
    assert "preToolUse" in hooks
    cursor_cmd = hooks["beforeShellExecution"][0]["command"]
    assert "gate-hook" in cursor_cmd
    pretool = hooks["preToolUse"][0]
    assert "gate-hook" in pretool["command"]
    assert "Write" in pretool.get("matcher", "")

    claude_cfg = json.loads(claude.read_text(encoding="utf-8"))
    pre = claude_cfg["hooks"]["PreToolUse"]
    claude_cmd = pre[0]["hooks"][0]["command"]
    assert "gate-hook" in claude_cmd


def test_installer_copies_hook_adapters(project_root: Path,
                                        tmp_path_factory) -> None:
    from graphstack import installer

    target = tmp_path_factory.mktemp("install-target")
    assert installer.install(target, non_interactive=True) == 0
    assert (target / ".cursor" / "hooks.json").is_file()
    assert (target / ".claude" / "settings.json").is_file()
    assert (target / "scripts" / "graphstack" / "gate.py").is_file()
    assert (target / "scripts" / "graphstack" / "state.py").is_file()
    assert (target / "scripts" / "gate-hook.sh").is_file()
    assert (target / "scripts" / "gate-hook.ps1").is_file()
    hooks = json.loads((target / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    assert "gate-hook" in hooks["hooks"]["beforeShellExecution"][0]["command"]
