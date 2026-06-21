"""Aesthetic engine CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..constants import DESIGN_GRAPH_JSON
from ..design_graph.query import load_graph
from .evaluate import format_evaluate_summary, run_evaluate, write_aesthetic_report
from .research import init_inspiration, validate_inspiration


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: graphcraft aesthetic <evaluate|research> ...")
        return 0

    cmd, rest = argv[0], argv[1:]

    if cmd == "evaluate":
        p = argparse.ArgumentParser(prog="graphcraft aesthetic evaluate")
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--screen", default=None)
        p.add_argument("--style", default=None)
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        root = Path(args.root).resolve()
        graph_path = Path(args.graph)
        if not graph_path.is_file():
            print(f"Missing {graph_path} — run: graphcraft design update .")
            return 1
        result = run_evaluate(
            root,
            load_graph(graph_path),
            screen_id=args.screen,
            style_id=args.style,
        )
        report_path = write_aesthetic_report(root, result)
        print(format_evaluate_summary(result))
        print(f"  -> {report_path}")
        return 0 if result["overall"] in ("PASS", "WARN") else 1

    if cmd == "research":
        if not rest or rest[0] in ("-h", "--help"):
            print("Usage: graphcraft aesthetic research <init|validate> [root]")
            return 0
        action = rest[0]
        sub_rest = rest[1:]
        p = argparse.ArgumentParser(prog=f"graphcraft aesthetic research {action}")
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--force", action="store_true", help="overwrite INSPIRATION.md (init only)")
        args = p.parse_args(sub_rest)
        root = Path(args.root).resolve()

        if action == "init":
            path = init_inspiration(root, force=args.force)
            print(f"Created {path}")
            return 0

        if action == "validate":
            issues = validate_inspiration(root)
            if issues:
                for i in issues:
                    print(f"  ISSUE: {i}")
                return 1
            print("INSPIRATION validation: PASS")
            return 0

        print(f"Unknown research action: {action}")
        return 1

    print(f"Unknown aesthetic subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
