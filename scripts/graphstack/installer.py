"""GraphStack installer — pure Python port of ``install.sh``.

Improvements over the bash original:
- Works natively on Windows PowerShell (no Git Bash needed)
- No ``realpath`` dependency (uses ``pathlib.Path.resolve()``)
- ``--non-interactive`` / ``-y`` flag for CI use
- ``.gitkeep`` files in empty board directories so git tracks them
- Re-entrant: re-running over an existing install only refreshes managed files
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .platform_utils import echo, graphify_available

PACKAGE_ROOT = Path(__file__).resolve().parent


def install_source_root() -> Path:
    """Workflow files: dev repo checkout, or bundled assets in PyPI wheel."""
    repo = PACKAGE_ROOT.parent.parent
    if (repo / "orchestrator" / "ORCHESTRATOR.md").is_file():
        return repo
    bundled = PACKAGE_ROOT / "assets"
    if (bundled / "orchestrator" / "ORCHESTRATOR.md").is_file():
        return bundled
    raise FileNotFoundError(
        "GraphStack workflow files not found. "
        "Reinstall with: pip install --upgrade MertCapkin_GraphStack"
    )


# Back-compat alias used throughout this module.
def _source_root() -> Path:
    return install_source_root()

DIRS_TO_CREATE = (
    ".cursor/rules",
    ".cursor/skills/architect",
    ".cursor/skills/builder",
    ".cursor/skills/reviewer",
    ".cursor/skills/qa",
    ".cursor/skills/ship",
    ".cursor/skills/bootstrapper",
    ".cursor/commands",
    ".claude",
    "orchestrator",
    "handoff/board/todo",
    "handoff/board/doing",
    "handoff/board/done",
    "graphify-out",
    "scripts",
    "scripts/graphstack",
    "docs",
)

# (source path inside repo, dest path inside target)
FILE_COPIES = (
    (".cursor/rules/graphstack.mdc", ".cursor/rules/graphstack.mdc"),
    (".cursor/commands/graphstack.md", ".cursor/commands/graphstack.md"),
    ("orchestrator/ORCHESTRATOR.md", "orchestrator/ORCHESTRATOR.md"),
    ("orchestrator/TOKEN_OPTIMIZER.md", "orchestrator/TOKEN_OPTIMIZER.md"),
    (".cursor/skills/architect/ARCHITECT.md", ".cursor/skills/architect/ARCHITECT.md"),
    (".cursor/skills/builder/BUILDER.md", ".cursor/skills/builder/BUILDER.md"),
    (".cursor/skills/reviewer/REVIEWER.md", ".cursor/skills/reviewer/REVIEWER.md"),
    (".cursor/skills/qa/QA.md", ".cursor/skills/qa/QA.md"),
    (".cursor/skills/ship/SHIP.md", ".cursor/skills/ship/SHIP.md"),
    (".cursor/skills/bootstrapper/BOOTSTRAPPER.md", ".cursor/skills/bootstrapper/BOOTSTRAPPER.md"),
    ("handoff/board/README.md", "handoff/board/README.md"),
    ("docs/CURSOR_PROMPTS.md", "docs/CURSOR_PROMPTS.md"),
    ("scripts/board.sh", "scripts/board.sh"),
    ("scripts/board.ps1", "scripts/board.ps1"),
    ("scripts/post-commit", "scripts/post-commit"),
    ("scripts/post-commit.ps1", "scripts/post-commit.ps1"),
    ("scripts/gate-hook.sh", "scripts/gate-hook.sh"),
    ("scripts/gate-hook.ps1", "scripts/gate-hook.ps1"),
)

# Handoff files that must NOT overwrite an existing copy in the target.
HANDOFF_TEMPLATES = (
    ("handoff/BRIEF.md", "handoff/BRIEF.md"),
    ("handoff/REVIEW.md", "handoff/REVIEW.md"),
    ("handoff/BOOTSTRAP.md", "handoff/BOOTSTRAP.md"),
)

PYTHON_PACKAGE_FILES = (
    "__init__.py",
    "__main__.py",
    "cli.py",
    "board.py",
    "installer.py",
    "hook.py",
    "validate.py",
    "platform_utils.py",
    "constants.py",
    "run.py",
    "gate.py",
    "state.py",
    "graph.py",
    "init_cmd.py",
    "bootstrap.py",
    "brief_utils.py",
    "cycle.py",
)

COMPACT_PACKAGE_FILES = (
    "__init__.py",
    "base.py",
    "git.py",
    "generic.py",
    "registry.py",
)

GITKEEP_DIRS = ("handoff/board/todo", "handoff/board/doing", "handoff/board/done")

STATE_TEMPLATE = """# GraphStack Session State

> Auto-managed by Orchestrator. Append-only — never delete history.

---

<!-- Sessions appended below, newest first -->
"""


def _copy_if_exists(src: Path, dst: Path) -> bool:
    root = _source_root()
    if not src.is_file():
        try:
            rel = src.relative_to(root)
        except ValueError:
            rel = src
        echo(f"⚠️  Missing source file: {rel}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _ask_yes_no(prompt: str, *, default_no: bool = True, non_interactive: bool = False) -> bool:
    if non_interactive:
        return False
    suffix = " (y/N): " if default_no else " (Y/n): "
    try:
        answer = input(prompt + suffix).strip().lower()
    except EOFError:
        return False
    if not answer:
        return not default_no
    return answer in ("y", "yes")


def _install_git_hook(target: Path, non_interactive: bool) -> None:
    git_dir = target / ".git"
    if not git_dir.is_dir():
        return
    if not _ask_yes_no(
        "🔗 Install git post-commit hook for auto graph updates?",
        non_interactive=non_interactive,
    ):
        return
    src = _source_root() / "scripts" / "post-commit"
    dst = git_dir / "hooks" / "post-commit"
    if _copy_if_exists(src, dst):
        try:
            dst.chmod(0o755)
        except OSError:
            pass  # Windows: chmod is largely symbolic, hook still runs via Git Bash
        echo("✅ Git hook installed.")


def _gate_hook_command(platform: str) -> str:
    """Shell command for hook adapters — OS-aware python launcher."""
    if sys.platform == "win32":
        return (
            f"powershell -NoProfile -ExecutionPolicy Bypass "
            f"-File scripts/gate-hook.ps1 {platform}"
        )
    return f"bash scripts/gate-hook.sh {platform}"


def _cursor_hooks_payload() -> dict:
    cmd = _gate_hook_command("cursor")
    hook_entry = {"command": cmd}
    return {
        "version": 1,
        "hooks": {
            "preToolUse": [{**hook_entry, "matcher": "Write|Shell|Delete|Edit"}],
            "beforeShellExecution": [hook_entry],
            "afterFileEdit": [hook_entry],
            "stop": [hook_entry],
        },
    }


def _claude_settings_payload() -> dict:
    cmd = _gate_hook_command("claude")
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash",
                    "hooks": [
                        {"type": "command", "command": cmd, "timeout": 30}
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {"type": "command", "command": cmd, "timeout": 30}
                    ]
                }
            ],
        }
    }


def _json_has_gate_hook(data: object) -> bool:
    return "gate-hook" in json.dumps(data)


def _hook_command_key(entry: object) -> str:
    if isinstance(entry, dict):
        return str(entry.get("command", ""))
    return ""


def _merge_hook_entry_lists(existing: object, new_entries: list) -> list:
    merged = list(existing) if isinstance(existing, list) else []
    known = {_hook_command_key(e) for e in merged if isinstance(e, dict)}
    for entry in new_entries:
        if not isinstance(entry, dict):
            continue
        key = _hook_command_key(entry)
        if key and key not in known:
            merged.append(entry)
            known.add(key)
    return merged


def merge_cursor_hooks(existing: dict | None, payload: dict) -> dict:
    """Merge GraphStack gate entries into an existing Cursor hooks.json."""
    if not existing:
        return payload
    result = dict(existing)
    if "version" not in result:
        result["version"] = payload.get("version", 1)
    hooks = dict(result.get("hooks") or {})
    for name, new_list in (payload.get("hooks") or {}).items():
        hooks[name] = _merge_hook_entry_lists(hooks.get(name, []), new_list)
    result["hooks"] = hooks
    return result


def merge_claude_settings(existing: dict | None, payload: dict) -> dict:
    """Append GraphStack gate hooks to Claude settings when missing."""
    if not existing:
        return payload
    if _json_has_gate_hook(existing):
        return existing
    result = dict(existing)
    hooks = dict(result.get("hooks") or {})
    for event, blocks in (payload.get("hooks") or {}).items():
        hooks[event] = _merge_hook_entry_lists(hooks.get(event, []), blocks)
    result["hooks"] = hooks
    return result


def _install_hook_adapters(target: Path) -> None:
    """Write or merge Cursor / Claude Code hook adapters."""
    adapters = (
        (target / ".cursor" / "hooks.json", _cursor_hooks_payload(), merge_cursor_hooks),
        (target / ".claude" / "settings.json", _claude_settings_payload(), merge_claude_settings),
    )
    for dst, payload, merge_fn in adapters:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            try:
                existing = json.loads(dst.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                echo(f"⚠️  {dst.relative_to(target)} unreadable — overwriting")
                existing = None
            else:
                if _json_has_gate_hook(existing):
                    echo(f"⏭️  {dst.relative_to(target)} already has gate hooks")
                    continue
                payload = merge_fn(existing, payload)
                echo(f"🔀 Merged gate hooks into {dst.relative_to(target)}")
        dst.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    echo("🛡️  Process-gate hooks installed (.cursor/hooks.json, .claude/settings.json)")


def _ensure_state_md(target: Path) -> None:
    state = target / "handoff" / "STATE.md"
    if state.exists():
        return
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(STATE_TEMPLATE, encoding="utf-8")


def _install_python_package(target: Path) -> int:
    """Copy ``scripts/graphstack/*.py`` into the target so the shims work."""
    src_pkg = PACKAGE_ROOT
    dst_pkg = target / "scripts" / "graphstack"
    dst_pkg.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in PYTHON_PACKAGE_FILES:
        src = src_pkg / name
        if not src.is_file():
            echo(f"⚠️  Missing package file: scripts/graphstack/{name}")
            continue
        shutil.copy2(src, dst_pkg / name)
        copied += 1

    compact_src = src_pkg / "compact"
    compact_dst = dst_pkg / "compact"
    if compact_src.is_dir():
        compact_dst.mkdir(parents=True, exist_ok=True)
        for name in COMPACT_PACKAGE_FILES:
            src = compact_src / name
            if src.is_file():
                shutil.copy2(src, compact_dst / name)
                copied += 1
    return copied


def install(target: Path, *, non_interactive: bool = False) -> int:
    target = target.resolve()
    root = _source_root()

    echo("")
    echo("🧠 GraphStack Installer")
    echo("=====================")
    echo(f"Target: {target}")
    echo("")

    echo("📁 Creating directories...")
    for rel in DIRS_TO_CREATE:
        (target / rel).mkdir(parents=True, exist_ok=True)

    echo("📋 Installing Cursor rules, orchestrator and role skills...")
    for src_rel, dst_rel in FILE_COPIES:
        _copy_if_exists(root / src_rel, target / dst_rel)

    echo("🐍 Installing Python helper package...")
    package_count = _install_python_package(target)
    echo(f"   {package_count} package files copied to scripts/graphstack/")

    # Make the unix shims executable; on Windows this is a no-op symbolic chmod.
    for rel in ("scripts/board.sh", "scripts/post-commit", "scripts/gate-hook.sh"):
        path = target / rel
        if path.is_file():
            try:
                path.chmod(0o755)
            except OSError:
                pass

    if not (target / "handoff" / "BRIEF.md").exists():
        echo("📝 Creating handoff templates...")
        for src_rel, dst_rel in HANDOFF_TEMPLATES:
            _copy_if_exists(root / src_rel, target / dst_rel)
    else:
        echo("⏭️  Handoff files already exist — skipping (not overwriting)")

    _ensure_state_md(target)
    _install_hook_adapters(target)

    for rel in GITKEEP_DIRS:
        keep = target / rel / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    _install_git_hook(target, non_interactive)

    echo("")
    if graphify_available():
        echo("✅ graphify is installed.")
    else:
        echo("⚠️  graphify not found. Install it with:")
        echo("   pip install \"graphifyy>=0.7,<0.9\"")

    echo("")
    echo("🎉 GraphStack v4.6.1 installed!")
    echo("")
    echo("Next steps:")
    echo("  1. Build graph:   open Cursor in your project → type: /graphify .")
    echo("  2. Start working: paste the prompt from docs/CURSOR_PROMPTS.md")
    echo("")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graphstack install",
        description="Install GraphStack into a target project directory.",
    )
    p.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project root (defaults to current directory).",
    )
    p.add_argument(
        "-y", "--non-interactive",
        action="store_true",
        help="Skip all interactive prompts (CI-friendly). Implies 'no' to optional features.",
    )
    return p


def run(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    target = Path(args.target)
    return install(target, non_interactive=args.non_interactive)


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
