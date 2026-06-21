"""Stitch import CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..constants import STITCH_DIR, STITCH_REPORT
from ..design_graph.builder import update_design_graph
from .fetch import run_fetch
from .mcp import doctor_mcp, format_mcp_json, install_mcp_config, project_id_from_config
from .pull import doctor_stitch, run_pull
from .validate import stitch_summary, validate_stitch_dir


def run_import(root: Path) -> int:
    meta = root / STITCH_DIR / "metadata.json"
    if not meta.is_file():
        print(f"No {STITCH_DIR}/metadata.json — copy metadata.template.json and fill in screen data.")
        return 1
    issues = validate_stitch_dir(root)
    if issues:
        for i in issues:
            print(f"  WARN: {i}")
    graph = update_design_graph(root)
    screens = [n for n in graph.get("nodes", []) if n.get("type") == "screen" and n.get("_origin") == "stitch"]
    print(f"Stitch import: {len(screens)} screen(s) ingested into design graph.")
    return 0 if not issues else 1


def run_report(root: Path) -> int:
    meta = root / STITCH_DIR / "metadata.json"
    design_md = root / STITCH_DIR / "DESIGN.md"
    summary = stitch_summary(root)
    lines = ["# Stitch Import Report", ""]
    lines.append(f"- valid: {summary.get('valid')}")
    lines.append(f"- project_id: {summary.get('project_id', 'unknown')}")
    lines.append(f"- screens in metadata: {summary.get('screens', 0)}")
    lines.append(f"- reference PNGs: {summary.get('png_count', 0)}")
    lines.append(f"- DESIGN.md: {'present' if design_md.is_file() else 'missing'}")
    if summary.get("issues"):
        lines.append("")
        lines.append("## Issues")
        for i in summary["issues"]:
            lines.append(f"- {i}")
    out = root / STITCH_REPORT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report -> {out}")
    return 0 if summary.get("valid") else 1


def run_mcp(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: graphcraft stitch mcp <print|install|doctor> [root]")
        return 0
    action = argv[0]
    rest = argv[1:]
    p = argparse.ArgumentParser(prog=f"graphcraft stitch mcp {action}")
    p.add_argument("root", nargs="?", default=".")
    p.add_argument("--project-id", default=None, help="override stitch.project_id from config")
    args = p.parse_args(rest)
    root = Path(args.root).resolve()
    pid = args.project_id or project_id_from_config(root)

    if action == "print":
        print(format_mcp_json(pid))
        return 0
    if action == "install":
        path = install_mcp_config(root, project_id=pid)
        print(f"Merged Stitch MCP config -> {path}")
        if not pid:
            print("  WARN: stitch.project_id empty in graphcraft.config.yaml — set GOOGLE_CLOUD_PROJECT manually")
        return 0
    if action == "doctor":
        issues = doctor_mcp(root)
        if issues:
            for i in issues:
                print(f"  ISSUE: {i}")
            return 1
        print("Stitch MCP doctor: PASS")
        return 0
    print(f"Unknown mcp action: {action}")
    return 1


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(
            "Usage: graphcraft stitch "
            "<import|report|validate|fetch|pull|doctor|mcp> ..."
        )
        return 0
    cmd = argv[0]
    rest = argv[1:]

    if cmd == "mcp":
        return run_mcp(rest)

    p = argparse.ArgumentParser(prog=f"graphcraft stitch {cmd}")
    p.add_argument("root", nargs="?", default=".")
    if cmd == "fetch":
        p.add_argument("--export-dir", required=True)
        p.add_argument("--force", action="store_true")
    elif cmd == "pull":
        p.add_argument("--project-id", default=None, help="Stitch project id (overrides config)")
        p.add_argument("--force", action="store_true", help="overwrite existing .stitch/")
        p.add_argument("--html", action="store_true", help="download screen HTML exports")
        p.add_argument("--no-import", action="store_true", help="skip design graph import")
        p.add_argument("--skip-doctor", action="store_true", help="skip preflight checks")
    args = p.parse_args(rest)
    root = Path(args.root).resolve()

    if cmd == "import":
        return run_import(root)
    if cmd == "report":
        return run_report(root)
    if cmd == "validate":
        issues = validate_stitch_dir(root)
        if issues:
            for i in issues:
                print(f"  ISSUE: {i}")
            return 1
        print("Stitch validation: PASS")
        return 0
    if cmd == "fetch":
        return run_fetch(root, Path(args.export_dir), force=args.force)
    if cmd == "pull":
        return run_pull(
            root,
            project_id=args.project_id,
            force=args.force,
            skip_import=args.no_import,
            include_html=args.html,
            skip_doctor=args.skip_doctor,
        )
    if cmd == "doctor":
        issues = doctor_stitch(root)
        if issues:
            for i in issues:
                print(f"  ISSUE: {i}")
            return 1
        print("Stitch doctor: PASS (pull + MCP)")
        return 0

    print(f"Unknown stitch subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
