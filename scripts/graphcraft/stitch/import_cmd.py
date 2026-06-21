"""Stitch import CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..constants import STITCH_DIR
from ..design_graph.builder import update_design_graph


def run_import(root: Path) -> int:
    meta = root / STITCH_DIR / "metadata.json"
    if not meta.is_file():
        print(f"No {STITCH_DIR}/metadata.json — copy metadata.template.json and fill in screen data.")
        return 1
    graph = update_design_graph(root)
    screens = [n for n in graph.get("nodes", []) if n.get("type") == "screen" and n.get("_origin") == "stitch"]
    print(f"Stitch import: {len(screens)} screen(s) ingested into design graph.")
    return 0


def run_report(root: Path) -> int:
    meta = root / STITCH_DIR / "metadata.json"
    design_md = root / STITCH_DIR / "DESIGN.md"
    lines = ["# Stitch Import Report", ""]
    if meta.is_file():
        data = json.loads(meta.read_text(encoding="utf-8"))
        lines.append(f"- project_id: {data.get('project_id', 'unknown')}")
        screens = data.get("screens") or {}
        lines.append(f"- screens in metadata: {len(screens) if isinstance(screens, (dict, list)) else 0}")
    else:
        lines.append("- metadata.json: missing")
    lines.append(f"- DESIGN.md: {'present' if design_md.is_file() else 'missing'}")
    designs = root / STITCH_DIR / "designs"
    if designs.is_dir():
        pngs = list(designs.glob("*.png"))
        htmls = list(designs.glob("*.html"))
        lines.append(f"- reference assets: {len(pngs)} PNG, {len(htmls)} HTML")
    out = root / "graphcraft-out" / "STITCH_REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report -> {out}")
    return 0


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: graphcraft stitch <import|report> [root]")
        return 0
    cmd = argv[0]
    rest = argv[1:]
    p = argparse.ArgumentParser(prog=f"graphcraft stitch {cmd}")
    p.add_argument("root", nargs="?", default=".")
    args = p.parse_args(rest)
    root = Path(args.root).resolve()
    if cmd == "import":
        return run_import(root)
    if cmd == "report":
        return run_report(root)
    print(f"Unknown stitch subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
