"""Deterministic process gate — enforces GraphStack handoff discipline.

Three entry points:

- ``gate check [--json]``     — CI / manual rule evaluation (exit 0 pass, 1 fail)
- ``gate hook cursor``        — Cursor hooks adapter (stdin payload → stdout JSON)
- ``gate hook claude``        — Claude Code hooks adapter (stdin payload → stdout JSON)

Rules:
  R1  ``git commit`` touching code paths while board doing/ is empty → DENY
  R2  Edit/Write on a code path (Claude Code PreToolUse) while doing/ empty → DENY
  R3  doing/ has a task but BRIEF.md is still the template → DENY commit
  R4  (stop events) doing/ task exists but STATE.json is older than the task
      claim → advisory warning, never blocks

Design constraints (do not weaken):
- FAIL OPEN: any internal error → allow + warning on stderr. A crashing gate
  that blocks all work is worse than no gate.
- Cursor honors only ``deny`` reliably → rules are deny-or-silent.
- Claude Code deny requires exit code 0 + ``hookSpecificOutput`` wrapper.
- Bypass: env ``GRAPHSTACK_GATE=off`` or ``handoff/.gate-off`` file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from .constants import DOING_DIR, GATE_OFF_FILE, HANDOFF_DIR, NON_CODE_PREFIXES
from .platform_utils import echo, git_available, run_git
from .state import load_state
from .validate import _brief_is_template

GIT_COMMIT_RE = re.compile(r"\bgit\b[^|&;]*\bcommit\b")

MSG_NO_TASK = (
    "GraphStack gate: no task in handoff/board/doing/. "
    "Process requires: Architect writes handoff/BRIEF.md, then "
    "'python -m graphstack board new <id> <title>' and "
    "'board claim <id> builder' BEFORE changing code. "
    "(Bypass: GRAPHSTACK_GATE=off)"
)
MSG_TEMPLATE_BRIEF = (
    "GraphStack gate: a task is in doing/ but handoff/BRIEF.md is still the "
    "template. Architect must write the brief before code is committed. "
    "(Bypass: GRAPHSTACK_GATE=off)"
)
MSG_STALE_STATE = (
    "GraphStack gate (advisory): task in doing/ but handoff/STATE.json was not "
    "updated this cycle. Run: python -m graphstack state set --role <role> "
    "--task <id>"
)


def gate_disabled() -> bool:
    if os.environ.get("GRAPHSTACK_GATE", "").lower() in ("off", "0", "false"):
        return True
    return GATE_OFF_FILE.exists()


def is_code_path(path: str) -> bool:
    """Anything outside handoff/graph/IDE config and root-level *.md is code."""
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    if not p:
        return False
    if any(p.startswith(prefix) for prefix in NON_CODE_PREFIXES):
        return False
    if "/" not in p and p.endswith(".md"):
        return False
    return True


def _doing_tasks() -> list[Path]:
    if not DOING_DIR.is_dir():
        return []
    return sorted(DOING_DIR.glob("*.json"))


def _brief_is_unwritten() -> bool:
    brief = HANDOFF_DIR / "BRIEF.md"
    try:
        return _brief_is_template(brief.read_text(encoding="utf-8"))
    except OSError:
        return True


def _changed_files(*git_args: str) -> list[str]:
    if not git_available():
        return []
    proc = run_git(*git_args)
    if proc.returncode != 0 or not proc.stdout:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _commit_candidate_files(command: str) -> list[str]:
    """Files a ``git commit`` command would plausibly commit.

    Staged files, plus modified tracked files for ``-a`` commits, plus any
    command token that exists on disk (covers ``git add X && git commit``
    where X is not staged yet when the hook fires).
    """
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
    """R1 + R3 for shell commands. Returns (allow, deny_reason)."""
    if gate_disabled():
        return True, None
    if not GIT_COMMIT_RE.search(command):
        return True, None

    doing = _doing_tasks()
    candidates = _commit_candidate_files(command)
    touches_code = any(is_code_path(f) for f in candidates)

    if not doing and touches_code:
        return False, MSG_NO_TASK  # R1
    if doing and touches_code and _brief_is_unwritten():
        return False, MSG_TEMPLATE_BRIEF  # R3
    return True, None


def evaluate_file_edit(file_path: str) -> tuple[bool, str | None]:
    """R2 for Edit/Write tool calls. Returns (allow, deny_reason)."""
    if gate_disabled():
        return True, None
    try:
        rel = os.path.relpath(file_path, Path.cwd())
    except ValueError:  # different drive on Windows
        return True, None
    if rel.startswith(".."):
        return True, None  # outside this project — not ours to gate
    if is_code_path(rel) and not _doing_tasks():
        return False, MSG_NO_TASK
    return True, None


def evaluate_stop() -> str | None:
    """R4 — advisory only. Returns a warning message or None."""
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
    if started and updated < started:  # ISO-8601 strings compare lexically
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
                f"empty — claim a board task first (e.g. {dirty_code[0]})"
            )
        if doing and _brief_is_unwritten():
            failures.append("task in doing/ but handoff/BRIEF.md is still the template")
        stale = evaluate_stop()
        if stale:
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


def hook_cursor() -> int:
    """Cursor adapter. Responses use snake_case; only deny is load-bearing."""
    try:
        data = _read_stdin_json()
        event = data.get("hook_event_name", "")

        if event == "beforeShellExecution":
            allow, reason = evaluate_command(str(data.get("command", "")))
            if not allow:
                _emit({"continue": False, "permission": "deny",
                       "user_message": reason, "agent_message": reason})
                return 0
            _emit({"continue": True, "permission": "allow"})
            return 0

        if event == "afterFileEdit":
            # Cursor has no before-edit blocking event — advisory only.
            edited = str(data.get("file_path", ""))
            if edited and not gate_disabled() and not _doing_tasks():
                try:
                    rel = os.path.relpath(edited, Path.cwd())
                except ValueError:
                    rel = edited
                if not rel.startswith("..") and is_code_path(rel):
                    _emit({"agent_message": MSG_NO_TASK})
                    return 0
            _emit({})
            return 0

        if event == "stop":
            warning = evaluate_stop()
            _emit({"agent_message": warning} if warning else {})
            return 0

        _emit({"continue": True, "permission": "allow"})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open by design
        print(f"graphstack gate: internal error, failing open: {exc}",
              file=sys.stderr)
        _emit({"continue": True, "permission": "allow"})
        return 0


def hook_claude() -> int:
    """Claude Code adapter. Deny = exit 0 + hookSpecificOutput wrapper."""
    try:
        data = _read_stdin_json()
        event = data.get("hook_event_name", "")
        tool = data.get("tool_name", "")
        tool_input = data.get("tool_input") or {}

        if event == "PreToolUse":
            allow, reason = True, None
            if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                allow, reason = evaluate_file_edit(str(tool_input.get("file_path", "")))
            elif tool == "Bash":
                allow, reason = evaluate_command(str(tool_input.get("command", "")))
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
            warning = evaluate_stop()
            _emit({"systemMessage": warning} if warning else {})
            return 0

        _emit({})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open by design
        print(f"graphstack gate: internal error, failing open: {exc}",
              file=sys.stderr)
        _emit({})
        return 0


# ------------------------------------------------------------------ dispatch

def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        echo("GraphStack Gate — commands:")
        echo("  check [--json]      evaluate gate rules (exit 1 on failure)")
        echo("  hook cursor         Cursor hooks adapter (stdin → stdout)")
        echo("  hook claude         Claude Code hooks adapter (stdin → stdout)")
        echo("Bypass: GRAPHSTACK_GATE=off or create handoff/.gate-off")
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
