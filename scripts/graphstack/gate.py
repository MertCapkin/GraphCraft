"""Deterministic process gate — enforces GraphStack handoff discipline.

Entry points:

- ``gate check [--json]``     — CI / manual rule evaluation (exit 0 pass, 1 fail)
- ``gate hook cursor``        — Cursor hooks adapter (stdin payload → stdout JSON)
- ``gate hook claude``        — Claude Code hooks adapter (stdin payload → stdout JSON)

Rules:
  R1  ``git commit`` touching code while doing/ is empty → DENY
  R2  Edit/Write on code path while doing/ is empty → DENY
  R3  doing/ + template BRIEF → DENY (commit and code edit)
  R2b Edit/Write on code path while STATE.role != builder → DENY
  R3b Edit/Write on code path while BRIEF status is Draft → DENY
  R4  Stop + stale STATE.json → advisory (DENY when GRAPHSTACK_GATE=strict)
  R5  ``git commit`` on code paths while role != ship → DENY (strict only)
  R6  ``git commit`` on code paths without REVIEW Verdict: Approved → DENY (strict only)

Bypass: ``GRAPHSTACK_GATE=off`` or ``handoff/.gate-off``
Strict: ``GRAPHSTACK_GATE=strict`` — R4–R6 enforced, hook errors deny
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from .brief_utils import brief_is_draft, brief_is_template, review_last_verdict_approved
from .constants import DOING_DIR, GATE_OFF_FILE, HANDOFF_DIR
from .platform_utils import echo, git_available, run_git
from .state import load_state

GIT_COMMIT_RE = re.compile(r"\bgit\b[^|&;]*\bcommit\b")

MSG_NO_TASK = (
    "GraphStack gate: no task in handoff/board/doing/. "
    "Start a cycle: python -m graphstack cycle start <id> \"<title>\" "
    "then Architect writes BRIEF, then: cycle enter-builder <id>. "
    "(Bypass: GRAPHSTACK_GATE=off)"
)
MSG_TEMPLATE_BRIEF = (
    "GraphStack gate: handoff/BRIEF.md is still the template. "
    "Architect must write the brief before code changes. "
    "(Bypass: GRAPHSTACK_GATE=off)"
)
MSG_WRONG_ROLE = (
    "GraphStack gate: code changes require role=builder in handoff/STATE.json "
    "(current: {role}). Run: python -m graphstack cycle enter-builder <task-id> "
    "or: python -m graphstack state set --role builder --task <id>"
)
MSG_BRIEF_DRAFT = (
    "GraphStack gate: BRIEF.md status is Draft. "
    "Architect must set **Status:** Ready for Builder before code edits."
)
MSG_STALE_STATE = (
    "GraphStack gate: task in doing/ but handoff/STATE.json was not updated this cycle. "
    "Run: python -m graphstack state set --role <role> --task <id>"
)
MSG_NOT_SHIP_ROLE = (
    "GraphStack gate (strict): code commits require role=ship "
    "(current: {role}). Complete Reviewer → QA → Ship first."
)
MSG_REVIEW_NOT_APPROVED = (
    "GraphStack gate (strict): handoff/REVIEW.md has no 'Verdict: Approved' "
    "in the latest cycle. Reviewer must approve before shipping code."
)


def gate_disabled() -> bool:
    if os.environ.get("GRAPHSTACK_GATE", "").lower() in ("off", "0", "false"):
        return True
    return GATE_OFF_FILE.exists()


def gate_strict() -> bool:
    """When True, R4–R6 and hook internal errors deny instead of fail-open."""
    return os.environ.get("GRAPHSTACK_GATE", "").lower() in (
        "strict", "fail-closed", "failclosed",
    )


def _extract_file_path(tool_input: dict) -> str:
    for key in ("file_path", "path", "target_file"):
        val = tool_input.get(key)
        if val:
            return str(val)
    return ""


def is_code_path(path: str) -> bool:
    """Anything outside handoff/graph/IDE config and root-level *.md is code."""
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    if not p:
        return False
    from .constants import NON_CODE_PREFIXES

    if any(p.startswith(prefix) for prefix in NON_CODE_PREFIXES):
        return False
    if "/" not in p and p.endswith(".md"):
        return False
    return True


def _doing_tasks() -> list[Path]:
    if not DOING_DIR.is_dir():
        return []
    return sorted(DOING_DIR.glob("*.json"))


def _current_role() -> str | None:
    state = load_state()
    if state is None:
        return None
    role = str(state.get("role") or "").strip().lower()
    return role or None


def _read_brief_text() -> str | None:
    try:
        return (HANDOFF_DIR / "BRIEF.md").read_text(encoding="utf-8")
    except OSError:
        return None


def _brief_is_unwritten() -> bool:
    text = _read_brief_text()
    if text is None:
        return True
    return brief_is_template(text)


def _code_edit_checks() -> tuple[bool, str | None]:
    """Shared R2 / R2b / R3 / R3b checks for code-path mutations."""
    if not _doing_tasks():
        return False, MSG_NO_TASK
    if _brief_is_unwritten():
        return False, MSG_TEMPLATE_BRIEF
    if brief_is_draft():
        return False, MSG_BRIEF_DRAFT
    role = _current_role()
    if role != "builder":
        return False, MSG_WRONG_ROLE.format(role=role or "none")
    return True, None


def _commit_strict_checks() -> tuple[bool, str | None]:
    """R5 + R6 — only when GRAPHSTACK_GATE=strict."""
    if not gate_strict():
        return True, None
    role = _current_role()
    if role != "ship":
        return False, MSG_NOT_SHIP_ROLE.format(role=role or "none")
    if not review_last_verdict_approved():
        return False, MSG_REVIEW_NOT_APPROVED
    return True, None


def _changed_files(*git_args: str) -> list[str]:
    if not git_available():
        return []
    proc = run_git(*git_args)
    if proc.returncode != 0 or not proc.stdout:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _commit_candidate_files(command: str) -> list[str]:
    files = _changed_files("diff", "--cached", "--name-only")
    if re.search(r"\s(-a\b|--all\b|-am\b)", command):
        files += _changed_files("diff", "--name-only")
    for token in re.split(r"[\s'\"]+", command):
        cleaned = token.strip("&|;")
        if not cleaned or cleaned.startswith("-"):
            continue
        try:
            if Path(cleaned).is_file():
                files.append(cleaned)
        except OSError:
            continue
    return sorted(set(files))


# ---------------------------------------------------------------- rule logic

def evaluate_command(command: str) -> tuple[bool, str | None]:
    """R1 + R3 + R5 + R6 for shell commands. Returns (allow, deny_reason)."""
    if gate_disabled():
        return True, None
    if not GIT_COMMIT_RE.search(command):
        return True, None

    candidates = _commit_candidate_files(command)
    touches_code = any(is_code_path(f) for f in candidates)
    if not touches_code:
        return True, None

    doing = _doing_tasks()
    if not doing:
        return False, MSG_NO_TASK
    if _brief_is_unwritten():
        return False, MSG_TEMPLATE_BRIEF

    allow, reason = _commit_strict_checks()
    if not allow:
        return False, reason
    return True, None


def evaluate_file_edit(file_path: str) -> tuple[bool, str | None]:
    """R2 + R2b + R3 + R3b for Edit/Write tool calls."""
    if gate_disabled():
        return True, None
    try:
        rel = os.path.relpath(file_path, Path.cwd())
    except ValueError:
        return True, None
    if rel.startswith(".."):
        return True, None
    if not is_code_path(rel):
        return True, None
    return _code_edit_checks()


def evaluate_pretooluse(tool_name: str, tool_input: dict) -> tuple[bool, str | None]:
    """R1 + R2 for generic PreToolUse / preToolUse events."""
    if gate_disabled():
        return True, None
    tool = tool_name.strip()
    write_tools = {"Write", "Edit", "Delete", "TabWrite", "MultiEdit", "NotebookEdit"}
    if tool in write_tools:
        path = _extract_file_path(tool_input)
        if path:
            return evaluate_file_edit(path)
    if tool in ("Shell", "Bash"):
        return evaluate_command(str(tool_input.get("command", "")))
    return True, None


def evaluate_stop() -> str | None:
    """R4 — advisory by default; deny when strict (handled in hook adapters)."""
    if gate_disabled():
        return None
    doing = _doing_tasks()
    if not doing:
        return None
    state = load_state()
    if state is None:
        return MSG_STALE_STATE
    try:
        task = json.loads(doing[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    started = task.get("started_at") or ""
    updated = state.get("updated_at") or ""
    if started and updated < started:
        return MSG_STALE_STATE
    return None


# ---------------------------------------------------------------- gate check

def run_check(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="graphstack gate check",
        description="Evaluate GraphStack process-gate rules (CI / manual).",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    failures: list[str] = []
    warnings: list[str] = []

    if gate_disabled():
        warnings.append("gate bypassed (GRAPHSTACK_GATE=off or handoff/.gate-off)")
    else:
        doing = _doing_tasks()
        dirty = _changed_files("status", "--porcelain")
        dirty_code = [
            line.split(maxsplit=1)[1] if " " in line else line
            for line in dirty
            if line and is_code_path(line.split(maxsplit=1)[-1])
        ]
        if not doing and dirty_code:
            failures.append(
                f"{len(dirty_code)} uncommitted code change(s) but doing/ is "
                f"empty — run: graphstack cycle start <id> \"<title>\""
            )
        if doing and _brief_is_unwritten():
            failures.append("task in doing/ but handoff/BRIEF.md is still the template")
        role = _current_role()
        if doing and role not in ("builder",):
            failures.append(
                f"task in doing/ but STATE.json role is '{role or 'none'}' "
                f"— run: graphstack cycle enter-builder <task-id>"
            )
        stale = evaluate_stop()
        if stale:
            if gate_strict():
                failures.append(stale)
            else:
                warnings.append(stale)

    if args.json:
        echo(json.dumps({"ok": not failures, "failures": failures,
                         "warnings": warnings}, ensure_ascii=False))
    else:
        for msg in failures:
            echo(f"  [FAIL] {msg}")
        for msg in warnings:
            echo(f"  [WARN] {msg}")
        echo(f"  Gate: {'FAIL' if failures else 'PASS'} "
             f"({len(failures)} failure(s), {len(warnings)} warning(s))")
    return 1 if failures else 0


# ------------------------------------------------------------- hook adapters

def _read_stdin_json() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def _emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def _cursor_deny(reason: str) -> None:
    _emit({
        "continue": False,
        "permission": "deny",
        "user_message": reason,
        "agent_message": reason,
    })


def _cursor_allow() -> None:
    _emit({"continue": True, "permission": "allow"})


def _cursor_pretool_deny(reason: str) -> None:
    _emit({"permission": "deny", "user_message": reason, "agent_message": reason})


def _cursor_pretool_allow() -> None:
    _emit({"permission": "allow"})


def _handle_stop_event(warning: str | None, *, cursor: bool) -> int:
    if not warning:
        if cursor:
            _emit({})
        else:
            _emit({})
        return 0
    if gate_strict():
        if cursor:
            _cursor_deny(warning)
        else:
            _emit({"hookSpecificOutput": {
                "hookEventName": "Stop",
                "permissionDecision": "deny",
                "permissionDecisionReason": warning,
            }})
        return 0
    if cursor:
        _emit({"agent_message": warning})
    else:
        _emit({"systemMessage": warning})
    return 0


def _handle_gate_error(cursor: bool, *, pretool: bool, exc: Exception) -> int:
    print(f"graphstack gate: internal error: {exc}", file=sys.stderr)
    if gate_strict():
        msg = (
            "GraphStack gate (strict): internal error — action denied. "
            "Fix the gate or set GRAPHSTACK_GATE=off temporarily."
        )
        if pretool:
            _cursor_pretool_deny(msg)
        elif cursor:
            _cursor_deny(msg)
        else:
            _emit({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": msg,
            }})
        return 0
    print("graphstack gate: failing open (default). Use GRAPHSTACK_GATE=strict to deny.",
          file=sys.stderr)
    if pretool:
        _cursor_pretool_allow()
    elif cursor:
        _cursor_allow()
    else:
        _emit({})
    return 0


def hook_cursor() -> int:
    """Cursor adapter. Responses use snake_case; only deny is load-bearing."""
    try:
        data = _read_stdin_json()
        event = data.get("hook_event_name", "")

        if event == "beforeShellExecution":
            allow, reason = evaluate_command(str(data.get("command", "")))
            if not allow:
                _cursor_deny(reason or MSG_NO_TASK)
                return 0
            _cursor_allow()
            return 0

        if event == "preToolUse":
            allow, reason = evaluate_pretooluse(
                str(data.get("tool_name", "")),
                data.get("tool_input") or {},
            )
            if not allow:
                _cursor_pretool_deny(reason or MSG_NO_TASK)
                return 0
            _cursor_pretool_allow()
            return 0

        if event == "afterFileEdit":
            edited = str(data.get("file_path", ""))
            if edited and not gate_disabled():
                try:
                    rel = os.path.relpath(edited, Path.cwd())
                except ValueError:
                    rel = edited
                if not rel.startswith("..") and is_code_path(rel):
                    allow, reason = _code_edit_checks()
                    if not allow:
                        _emit({"agent_message": reason or MSG_NO_TASK})
                        return 0
            _emit({})
            return 0

        if event == "stop":
            return _handle_stop_event(evaluate_stop(), cursor=True)

        _cursor_allow()
        return 0
    except Exception as exc:  # noqa: BLE001
        return _handle_gate_error(True, pretool=False, exc=exc)


def hook_claude() -> int:
    """Claude Code adapter. Deny = exit 0 + hookSpecificOutput wrapper."""
    try:
        data = _read_stdin_json()
        event = data.get("hook_event_name", "")
        tool = data.get("tool_name", "")
        tool_input = data.get("tool_input") or {}

        if event == "PreToolUse":
            allow, reason = evaluate_pretooluse(tool, tool_input)
            if not allow:
                _emit({"hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }})
                return 0
            _emit({})
            return 0

        if event == "Stop":
            return _handle_stop_event(evaluate_stop(), cursor=False)

        _emit({})
        return 0
    except Exception as exc:  # noqa: BLE001
        return _handle_gate_error(False, pretool=False, exc=exc)


# ------------------------------------------------------------------ dispatch

def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        echo("GraphStack Gate — commands:")
        echo("  check [--json]      evaluate gate rules (exit 1 on failure)")
        echo("  hook cursor         Cursor hooks adapter (stdin → stdout)")
        echo("  hook claude         Claude Code hooks adapter (stdin → stdout)")
        echo("Bypass: GRAPHSTACK_GATE=off or create handoff/.gate-off")
        echo("Strict:  GRAPHSTACK_GATE=strict (R4–R6 + fail-closed on errors)")
        return 0
    if argv[0] == "check":
        return run_check(argv[1:])
    if argv[0] == "hook":
        platform = argv[1] if len(argv) > 1 else ""
        if platform == "cursor":
            return hook_cursor()
        if platform == "claude":
            return hook_claude()
        echo(f"Unknown hook platform: '{platform}' (expected cursor|claude)")
        return 2
    echo(f"Unknown gate command: '{argv[0]}'")
    return 2


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
