"""Pull Stitch project via official @google/stitch-sdk (Node helper)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..constants import CONFIG_FILE, STITCH_DIR
from ..design_graph.builder import update_design_graph
from .fetch import fetch_export
from .mcp import doctor_mcp, project_id_from_config
from .validate import validate_stitch_dir, validate_stitch_export

PULL_SCRIPT = Path(__file__).with_name("pull_export.mjs")
STITCH_SDK_PACKAGE = "@google/stitch-sdk"


def _load_stitch_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_FILE
    if not path.is_file():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    stitch = data.get("stitch")
    return stitch if isinstance(stitch, dict) else {}


def pull_auth_env(root: Path) -> tuple[dict[str, str], list[str]]:
    """Build env for Node pull; return (env, issues)."""
    issues: list[str] = []
    env = dict(os.environ)

    api_key = env.get("STITCH_API_KEY", "").strip()
    access_token = env.get("STITCH_ACCESS_TOKEN", "").strip()
    gcp_project = (
        env.get("GOOGLE_CLOUD_PROJECT", "").strip()
        or project_id_from_config(root)
    )

    if not api_key and not (access_token and gcp_project):
        issues.append(
            "Set STITCH_API_KEY (recommended) or STITCH_ACCESS_TOKEN + GOOGLE_CLOUD_PROJECT"
        )

    if access_token and gcp_project and not env.get("GOOGLE_CLOUD_PROJECT"):
        env["GOOGLE_CLOUD_PROJECT"] = gcp_project

    return env, issues


def doctor_pull(root: Path) -> list[str]:
    """Readiness checks for stitch pull (auth + node toolchain)."""
    issues: list[str] = []
    root = root.resolve()

    _, auth_issues = pull_auth_env(root)
    issues.extend(auth_issues)

    pid = project_id_from_config(root)
    if not pid:
        issues.append(
            f"stitch.project_id empty in {CONFIG_FILE} — pass --project-id on pull"
        )

    if shutil.which("npx") is None:
        issues.append("npx not found on PATH (required for @google/stitch-sdk)")

    if not PULL_SCRIPT.is_file():
        issues.append(f"Missing pull helper: {PULL_SCRIPT}")

    return issues


def doctor_stitch(root: Path) -> list[str]:
    """Combined Stitch doctor: pull auth + MCP config."""
    issues = doctor_pull(root)
    mcp_issues = doctor_mcp(root)
    for item in mcp_issues:
        if item not in issues:
            issues.append(f"MCP: {item}")
    return issues


def _resolve_project_id(root: Path, override: str | None) -> str:
    pid = (override or "").strip() or project_id_from_config(root)
    if not pid:
        raise ValueError(
            f"Stitch project id required — set stitch.project_id in {CONFIG_FILE} "
            "or pass --project-id"
        )
    return pid


def run_node_export(
    project_id: str,
    export_dir: Path,
    *,
    env: dict[str, str] | None = None,
    include_html: bool = False,
) -> dict[str, Any]:
    """Invoke pull_export.mjs; return parsed JSON summary from stdout."""
    if not PULL_SCRIPT.is_file():
        raise FileNotFoundError(f"Missing {PULL_SCRIPT}")

    cmd = [
        "npx",
        "-y",
        "-p",
        STITCH_SDK_PACKAGE,
        "node",
        str(PULL_SCRIPT),
        "--project",
        project_id,
        "--out",
        str(export_dir),
    ]
    if include_html:
        cmd.append("--html")

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env or os.environ,
        check=False,
    )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        detail = stderr or stdout or f"exit {proc.returncode}"
        try:
            err_json = json.loads(detail)
            detail = err_json.get("error", detail)
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"Stitch pull export failed: {detail}")

    if not stdout:
        raise RuntimeError("Stitch pull produced no output")

    try:
        summary = json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid pull summary JSON: {stdout[:200]}") from exc

    if not summary.get("ok"):
        raise RuntimeError(summary.get("error", "Stitch pull failed"))

    return summary


def pull_project(
    root: Path,
    project_id: str,
    *,
    force: bool = False,
    include_html: bool = False,
    env: dict[str, str] | None = None,
) -> Path:
    """Pull from Stitch API into a temp export dir; copy to .stitch/."""
    root = root.resolve()
    run_env = env or dict(os.environ)

    with tempfile.TemporaryDirectory(prefix="graphcraft-stitch-") as tmp:
        export_dir = Path(tmp) / "export"
        export_dir.mkdir()
        summary = run_node_export(
            project_id,
            export_dir,
            env=run_env,
            include_html=include_html,
        )
        issues = validate_stitch_export(export_dir)
        if issues:
            raise RuntimeError(
                "Export validation failed: " + "; ".join(issues[:5])
            )
        target = fetch_export(root, export_dir, force=force)

    return target


def run_pull(
    root: Path,
    *,
    project_id: str | None = None,
    force: bool = False,
    skip_import: bool = False,
    include_html: bool = False,
    skip_doctor: bool = False,
) -> int:
    root = root.resolve()

    if not skip_doctor:
        issues = doctor_pull(root)
        if project_id:
            issues = [i for i in issues if "project_id empty" not in i]
        if issues:
            for item in issues:
                print(f"  ISSUE: {item}")
            print("Run: graphcraft stitch doctor .")
            return 1

    try:
        pid = _resolve_project_id(root, project_id)
    except ValueError as exc:
        print(f"Pull failed: {exc}")
        return 1

    env, _ = pull_auth_env(root)
    print(f"Pulling Stitch project {pid} ...")

    try:
        target = pull_project(
            root,
            pid,
            force=force,
            include_html=include_html,
            env=env,
        )
    except (RuntimeError, FileNotFoundError, FileExistsError) as exc:
        print(f"Pull failed: {exc}")
        return 1

    print(f"Pulled -> {target}")

    issues = validate_stitch_dir(root)
    if issues:
        for item in issues:
            print(f"  WARN: {item}")
        return 1

    print("Stitch pull: validation PASS")

    if skip_import:
        print("Skipping design graph import (--no-import)")
        return 0

    graph = update_design_graph(root)
    screens = [
        n
        for n in graph.get("nodes", [])
        if n.get("type") == "screen" and n.get("_origin") == "stitch"
    ]
    print(f"Design graph updated: {len(screens)} stitch screen(s)")

    post_issues = validate_stitch_dir(root)
    if post_issues:
        for item in post_issues:
            print(f"  WARN: {item}")
        return 1
    print("Stitch import: complete")
    return 0
