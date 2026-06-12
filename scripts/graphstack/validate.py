"""GraphStack project health checks (LLM-free).

Validates handoff layout, board task JSON, brief readiness, and graph freshness.
Use ``graphstack doctor`` for a human-friendly report of the same checks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .brief_utils import (
    BRIEF_READY_STATUSES,
    brief_is_template,
    brief_status,
    review_last_has_verdict,
)
from .constants import (
    BOARD_DIR,
    DOING_DIR,
    DONE_DIR,
    GRAPH_REPORT,
    HANDOFF_DIR,
    STATE_JSON,
    TASK_REQUIRED_KEYS,
    TODO_DIR,
)

FRAMEWORK_MARKER = Path(".graphstack-framework")
from .platform_utils import echo, git_available, graphify_available, run_git

GRAPH_COMMIT_RE = re.compile(r"Built from commit:\s*`([0-9a-f]+)`", re.IGNORECASE)

REQUIRED_PATHS = (
    ".cursor/rules/graphstack.mdc",
    "orchestrator/ORCHESTRATOR.md",
    "orchestrator/TOKEN_OPTIMIZER.md",
    ".cursor/skills/architect/ARCHITECT.md",
    ".cursor/skills/builder/BUILDER.md",
    "handoff/BRIEF.md",
    "handoff/STATE.md",
    "handoff/board/README.md",
)


@dataclass
class Finding:
    level: str  # error | warn | ok
    code: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, level: str, code: str, message: str) -> None:
        self.findings.append(Finding(level, code, message))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "warn"]


def _root() -> Path:
    return Path.cwd()


def _iter_board_tasks() -> list[Path]:
    paths: list[Path] = []
    for directory in (TODO_DIR, DOING_DIR, DONE_DIR):
        if not directory.is_dir():
            continue
        paths.extend(sorted(directory.glob("*.json")))
    return paths


def check_layout(report: Report, root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if path.is_file():
            report.add("ok", "layout_ok", f"Found {rel}")
        else:
            report.add("error", "layout_missing", f"Missing required file: {rel}")

    for rel in ("handoff/board/todo", "handoff/board/doing", "handoff/board/done"):
        path = root / rel
        if path.is_dir():
            report.add("ok", "board_dir_ok", f"Found {rel}/")
        else:
            report.add("error", "board_dir_missing", f"Missing directory: {rel}/")


def check_brief(report: Report, root: Path, *, strict: bool) -> None:
    brief_path = root / "handoff" / "BRIEF.md"
    if not brief_path.is_file():
        return

    text = brief_path.read_text(encoding="utf-8")
    if brief_is_template(text):
        level = "error" if strict else "warn"
        report.add(
            level,
            "brief_template",
            "handoff/BRIEF.md still contains template placeholders",
        )
        return

    status = brief_status(text)
    if status and status.startswith("Draft"):
        report.add("warn", "brief_draft", f"BRIEF.md status is '{status}' (not ready for Builder)")
    elif status and any(s in status for s in BRIEF_READY_STATUSES):
        report.add("ok", "brief_ready", f"BRIEF.md status: {status}")
    elif status:
        report.add("ok", "brief_status", f"BRIEF.md status: {status}")


def check_board_tasks(report: Report) -> None:
    for path in _iter_board_tasks():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            report.add("error", "task_invalid_json", f"{path}: {exc}")
            continue

        missing = [k for k in TASK_REQUIRED_KEYS if k not in data]
        if missing:
            report.add(
                "error",
                "task_missing_keys",
                f"{path.name}: missing keys {missing}",
            )
            continue

        task_id = data.get("id")
        if task_id and path.stem != str(task_id):
            report.add(
                "warn",
                "task_id_mismatch",
                f"{path.name}: filename does not match id '{task_id}'",
            )

        folder = path.parent.name
        status = str(data.get("status", ""))
        if folder == "todo" and status != "todo":
            report.add(
                "warn",
                "task_status_folder",
                f"{path.name}: in todo/ but status is '{status}'",
            )
        elif folder == "doing" and status != "doing":
            report.add(
                "warn",
                "task_status_folder",
                f"{path.name}: in doing/ but status is '{status}'",
            )
        elif folder == "done" and status != "done":
            report.add(
                "warn",
                "task_status_folder",
                f"{path.name}: in done/ but status is '{status}'",
            )
        else:
            report.add("ok", "task_ok", f"{path.name} ({folder}, {status})")


def _commit_matches_graph(graph_commit: str, ref: str) -> bool:
    ref = ref.strip().lower()
    graph_commit = graph_commit.lower()
    return ref.startswith(graph_commit) or graph_commit.startswith(ref[: len(graph_commit)])


def _refs_for_staleness_check() -> list[str]:
    """HEAD, HEAD~1, and last commit that touched the graph report.

    Graph is often built on HEAD~1 then committed on HEAD (release workflow).
    GitHub Actions uses fetch-depth: 1 by default — without HEAD~1, fall back to
    the commit that last modified GRAPH_REPORT.md (needs at least that commit).
    """
    refs: list[str] = []
    seen: set[str] = set()
    for arg in ("HEAD", "HEAD~1"):
        proc = run_git("rev-parse", arg)
        if proc.returncode == 0 and proc.stdout:
            ref = proc.stdout.strip().lower()
            if ref not in seen:
                seen.add(ref)
                refs.append(ref)
    proc = run_git("log", "-1", "--format=%H", "--", str(GRAPH_REPORT))
    if proc.returncode == 0 and proc.stdout:
        ref = proc.stdout.strip().lower()
        if ref not in seen:
            seen.add(ref)
            refs.append(ref)
    return refs


def _state_has_active_sessions(text: str) -> bool:
    """True when STATE.md contains real session entries (not only the template comment)."""
    without_comments = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return bool(re.search(r"^## \[\d{4}-", without_comments, re.MULTILINE))


def check_framework_handoff(report: Report, root: Path) -> None:
    """Warn when the framework source repo ships consumer session state in handoff/."""
    if not (root / FRAMEWORK_MARKER).is_file():
        return

    brief_path = root / "handoff" / "BRIEF.md"
    if brief_path.is_file():
        try:
            if not brief_is_template(brief_path.read_text(encoding="utf-8")):
                report.add(
                    "warn",
                    "framework_brief_dirty",
                    "Framework repo: handoff/BRIEF.md is not the template — "
                    "reset before release (see CONTRIBUTING.md)",
                )
        except OSError:
            pass

    done_tasks = list(DONE_DIR.glob("*.json")) if DONE_DIR.is_dir() else []
    if done_tasks:
        report.add(
            "warn",
            "framework_board_dirty",
            f"Framework repo: handoff/board/done/ has {len(done_tasks)} task(s) — "
            "reset before release",
        )

    state_path = root / "handoff" / "STATE.md"
    if state_path.is_file():
        try:
            if _state_has_active_sessions(state_path.read_text(encoding="utf-8")):
                report.add(
                    "warn",
                    "framework_state_dirty",
                    "Framework repo: handoff/STATE.md has active session entries — "
                    "reset before release",
                )
        except OSError:
            pass


def check_state(report: Report, root: Path) -> None:
    state_path = root / "handoff" / "STATE.md"
    if not state_path.is_file():
        report.add("error", "state_missing", "handoff/STATE.md is missing")
        return
    if state_path.stat().st_size == 0:
        report.add("warn", "state_empty", "handoff/STATE.md is empty")
    else:
        report.add("ok", "state_ok", "handoff/STATE.md present")


def check_handoff_sync(report: Report, root: Path, *, strict: bool) -> None:
    """Warn when BRIEF, board, and STATE.json are out of sync."""
    brief_path = root / "handoff" / "BRIEF.md"
    doing = sorted((root / "handoff" / "board" / "doing").glob("*.json")) if (
        root / "handoff" / "board" / "doing"
    ).is_dir() else []

    if brief_path.is_file():
        try:
            text = brief_path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        if not brief_is_template(text):
            status = brief_status(text) or ""
            if any(s in status for s in BRIEF_READY_STATUSES) and not doing:
                report.add(
                    "warn",
                    "brief_ready_no_doing",
                    "BRIEF.md is Ready for Builder but doing/ is empty — "
                    "run: python -m graphstack cycle enter-builder <task-id>",
                )

    if doing:
        state_path = root / STATE_JSON
        role = "none"
        if state_path.is_file():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                state = None
            if state:
                role = str(state.get("role") or "none")
        if role not in ("builder", "reviewer", "qa", "ship"):
            level = "error" if strict else "warn"
            report.add(
                level,
                "doing_role_mismatch",
                f"doing/ has {len(doing)} task(s) but STATE.json role is '{role}' — "
                f"run: python -m graphstack cycle enter-builder <task-id>",
            )
        elif role == "builder" and not review_last_has_verdict():
            report.add(
                "warn",
                "cycle_unclosed",
                f"doing/ has task(s) with role=builder but no REVIEW Verdict — "
                f"if implementation is done, run Reviewer→QA→Ship then "
                f"'python -m graphstack cycle close <task-id>'",
            )
        elif role in ("reviewer", "qa") and not review_last_has_verdict():
            report.add(
                "warn",
                "cycle_unclosed",
                f"doing/ has task(s) with role={role} but no REVIEW Verdict yet — "
                f"finish the cycle through Ship",
            )
    elif strict and (root / STATE_JSON).is_file():
        try:
            state = json.loads((root / STATE_JSON).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = None
        if state and str(state.get("role") or "") == "builder":
            report.add(
                "warn",
                "builder_role_no_doing",
                "STATE.json role is builder but doing/ is empty",
            )


def check_gate_hooks(report: Report, root: Path, *, strict: bool) -> None:
    """Verify Cursor process-gate hooks are installed."""
    hooks_path = root / ".cursor" / "hooks.json"
    if not hooks_path.is_file():
        level = "error" if strict else "warn"
        report.add(
            level,
            "hooks_missing",
            ".cursor/hooks.json not found — process gate inactive in Cursor "
            "(reinstall GraphStack or merge hooks)",
        )
        return

    try:
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.add("error", "hooks_invalid", f".cursor/hooks.json unreadable: {exc}")
        return

    hooks = data.get("hooks", {})
    pretool = hooks.get("preToolUse", [])
    has_gate = any(
        "gate-hook" in str(entry.get("command", ""))
        for entry in pretool
        if isinstance(entry, dict)
    )
    if has_gate:
        report.add("ok", "hooks_ok", "Cursor process-gate hooks configured")
    else:
        level = "error" if strict else "warn"
        report.add(
            level,
            "hooks_no_gate",
            "hooks.json exists but no graphstack gate-hook entry — "
            "reinstall or run graphstack install to merge hooks",
        )


def check_graph(report: Report, root: Path, *, fail_stale: bool) -> None:
    report_path = root / GRAPH_REPORT
    if not report_path.is_file():
        report.add("warn", "graph_missing", "graphify-out/GRAPH_REPORT.md not found — run /graphify .")
        return

    text = report_path.read_text(encoding="utf-8", errors="replace")
    match = GRAPH_COMMIT_RE.search(text)
    if not match:
        report.add("warn", "graph_no_commit", "GRAPH_REPORT.md has no 'Built from commit' line")
        return

    graph_commit = match.group(1)
    if not git_available():
        report.add("ok", "graph_commit", f"Graph built from {graph_commit[:12]} (git not checked)")
        return

    refs = _refs_for_staleness_check()
    if not refs:
        report.add("warn", "graph_git_head", "Could not read git HEAD for staleness check")
        return

    head = refs[0]
    for ref in refs:
        if _commit_matches_graph(graph_commit, ref):
            label = "HEAD" if ref == head else "git ref"
            report.add("ok", "graph_fresh", f"Graph matches {label} ({ref[:12]})")
            return

    # Graph built on an older commit that is still in history (full or deep clone).
    ancestor = run_git("merge-base", "--is-ancestor", graph_commit, "HEAD")
    if ancestor.returncode == 0:
        report.add(
            "ok",
            "graph_fresh",
            f"Graph commit {graph_commit[:12]} is an ancestor of HEAD ({head[:12]})",
        )
        return

    # Shallow clone: match any fetched commit on the current branch.
    listed = run_git("rev-list", "--max-count", "100", "HEAD")
    if listed.returncode == 0 and listed.stdout:
        for ref in listed.stdout.splitlines():
            if _commit_matches_graph(graph_commit, ref):
                report.add(
                    "ok",
                    "graph_fresh",
                    f"Graph matches fetched commit {ref[:12]} (shallow history)",
                )
                return

    level = "error" if fail_stale else "warn"
    report.add(
        level,
        "graph_stale",
        f"Graph built from {graph_commit[:12]} but HEAD is {head[:12]} — run graphify update .",
    )


def check_compact_module(report: Report, root: Path) -> None:
    run_py = root / "scripts" / "graphstack" / "run.py"
    registry = root / "scripts" / "graphstack" / "compact" / "registry.py"
    if run_py.is_file() and registry.is_file():
        report.add(
            "ok",
            "compact_ok",
            "Output compact module present (use: python -m graphstack run -- <cmd>)",
        )
    else:
        report.add(
            "warn",
            "compact_missing",
            "Output compact module missing — reinstall GraphStack for shell token savings",
        )


def check_graph_module(report: Report, root: Path) -> None:
    graph_py = root / "scripts" / "graphstack" / "graph.py"
    if graph_py.is_file():
        report.add(
            "ok",
            "graph_ok",
            "Graph query module present (use: python -m graphstack graph query \"…\")",
        )
    else:
        report.add(
            "warn",
            "graph_missing",
            "Graph query module missing — reinstall GraphStack for graph-first queries",
        )


def check_tooling(report: Report, *, doctor: bool) -> None:
    if graphify_available():
        report.add("ok", "graphify_ok", "graphify CLI found on PATH")
    else:
        report.add(
            "warn",
            "graphify_missing",
            "graphify not on PATH — install with: pip install -r requirements.txt",
        )

    if git_available():
        report.add("ok", "git_ok", "git found on PATH")
    else:
        msg = "git not on PATH (board commits and staleness checks need git)"
        if doctor:
            report.add("warn", "git_missing", msg)
        else:
            report.add("warn", "git_missing", msg)


def run_checks(
    *,
    strict: bool = False,
    fail_stale: bool = False,
    doctor: bool = False,
) -> Report:
    root = _root()
    report = Report()
    check_layout(report, root)
    check_brief(report, root, strict=strict)
    check_board_tasks(report)
    check_framework_handoff(report, root)
    check_state(report, root)
    check_handoff_sync(report, root, strict=strict)
    check_gate_hooks(report, root, strict=strict)
    check_graph(report, root, fail_stale=fail_stale)
    check_compact_module(report, root)
    check_graph_module(report, root)
    check_tooling(report, doctor=doctor)
    return report


def _print_report(report: Report, *, doctor: bool) -> None:
    if doctor:
        echo("")
        echo("GraphStack doctor")
        echo("=" * 40)

    errors = report.errors
    warnings = report.warnings
    oks = [f for f in report.findings if f.level == "ok"]

    for finding in report.findings:
        if finding.level == "error":
            prefix = "ERROR"
        elif finding.level == "warn":
            prefix = "WARN "
        else:
            if not doctor:
                continue
            prefix = "OK   "
        echo(f"  [{prefix}] {finding.message}")

    echo("")
    echo(
        f"  Summary: {len(errors)} error(s), {len(warnings)} warning(s), "
        f"{len(oks)} check(s) passed"
    )
    echo("")


def _build_parser(prog: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog, description="Validate GraphStack project layout.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat template BRIEF.md as an error (not only a warning)",
    )
    parser.add_argument(
        "--fail-stale-graph",
        action="store_true",
        help="Exit 1 when GRAPH_REPORT commit does not match git HEAD",
    )
    return parser


def run_validate(argv: list[str]) -> int:
    parser = _build_parser("graphstack validate")
    args = parser.parse_args(argv)
    report = run_checks(strict=args.strict, fail_stale=args.fail_stale_graph)
    _print_report(report, doctor=False)
    return 1 if report.errors else 0


def run_doctor(argv: list[str]) -> int:
    parser = _build_parser("graphstack doctor")
    args = parser.parse_args(argv)
    report = run_checks(strict=False, fail_stale=False, doctor=True)
    _print_report(report, doctor=True)
    return 1 if report.errors else 0


def run(argv: list[str] | None = None) -> int:
    """Default entry when invoked as ``validate`` sub-command."""
    args = sys.argv[2:] if argv is None else argv
    return run_validate(args)
