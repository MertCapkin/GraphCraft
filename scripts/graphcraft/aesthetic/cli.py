"""Aesthetic engine CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..constants import DESIGN_GRAPH_JSON, RESEARCH_INSPIRATION
from ..design_graph.query import load_graph
from .evaluate import format_evaluate_summary, run_evaluate, write_aesthetic_report
from .distill import format_distill_summary, run_distill
from .research import (
    doctor_research,
    init_inspiration,
    run_research,
    validate_inspiration,
)


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
            print(
                "Usage: graphcraft aesthetic research "
                "<init|validate|run|distill|doctor> [root]"
            )
            return 0
        action = rest[0]
        sub_rest = rest[1:]
        p = argparse.ArgumentParser(prog=f"graphcraft aesthetic research {action}")
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--force", action="store_true", help="overwrite INSPIRATION.md")
        p.add_argument("--offline", action="store_true", help="use offline fixture results")
        p.add_argument("--max-queries", type=int, default=5)
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

        if action == "doctor":
            issues = doctor_research(root, offline=args.offline)
            if issues:
                for i in issues:
                    print(f"  ISSUE: {i}")
                return 1
            print("Aesthetic research doctor: PASS")
            return 0

        if action == "run":
            try:
                path, warnings = run_research(
                    root,
                    force=args.force,
                    offline=args.offline,
                    max_queries=args.max_queries,
                )
            except (RuntimeError, FileExistsError) as exc:
                print(f"Research failed: {exc}")
                return 1
            print(f"Research complete -> {path}")
            for w in warnings:
                print(f"  WARN: {w}")
            issues = validate_inspiration(root)
            if issues:
                for i in issues:
                    print(f"  ISSUE: {i}")
                return 1
            print("INSPIRATION validation: PASS")
            print("Next: graphcraft aesthetic research distill .")
            return 0

        if action == "distill":
            try:
                result = run_distill(root, write=True)
            except FileNotFoundError as exc:
                print(f"Distill failed: {exc}")
                return 1
            print(format_distill_summary(result))
            print(f"  -> {root / RESEARCH_INSPIRATION}")
            print(f"  -> {root / 'graphcraft-out' / 'DISTILL_REPORT.md'}")
            return 0 if result["overall"] != "FAIL" else 1

        print(f"Unknown research action: {action}")
        return 1

    print(f"Unknown aesthetic subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
