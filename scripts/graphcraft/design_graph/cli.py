"""Design graph CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..constants import DESIGN_GRAPH_JSON
from .builder import update_design_graph
from .harmony import run_harmony_check
from .query import load_graph, query, validate


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: graphcraft design <update|query|validate|harmony> ...")
        return 0

    cmd, rest = argv[0], argv[1:]

    if cmd == "update":
        p = argparse.ArgumentParser(prog="graphcraft design update")
        p.add_argument("root", nargs="?", default=".")
        args = p.parse_args(rest)
        root = Path(args.root).resolve()
        graph = update_design_graph(root)
        print(f"Design graph: {len(graph.get('nodes', []))} nodes, {len(graph.get('edges', []))} edges")
        print(f"  -> {root / DESIGN_GRAPH_JSON}")
        return 0

    if cmd == "query":
        p = argparse.ArgumentParser(prog="graphcraft design query")
        p.add_argument("question", help="design graph question")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        path = Path(args.graph)
        if not path.is_file():
            print(f"Missing {path} — run: graphcraft design update .")
            return 1
        print(query(load_graph(path), args.question))
        return 0

    if cmd == "validate":
        p = argparse.ArgumentParser(prog="graphcraft design validate")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        path = Path(args.graph)
        if not path.is_file():
            print(f"Missing {path}")
            return 1
        issues = validate(load_graph(path))
        if issues:
            for i in issues:
                print(f"  ISSUE: {i}")
            return 1
        print("Design graph validation: PASS")
        return 0

    if cmd == "harmony":
        p = argparse.ArgumentParser(prog="graphcraft design harmony")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        p.add_argument("--screen", default=None)
        args = p.parse_args(rest)
        path = Path(args.graph)
        if not path.is_file():
            print(f"Missing {path}")
            return 1
        result = run_harmony_check(load_graph(path), args.screen)
        print(f"Harmony: {result['overall']}")
        for w in result["warnings"]:
            print(f"  WARN: {w}")
        for p_msg in result["passed"]:
            print(f"  OK: {p_msg}")
        return 0 if result["overall"] == "PASS" else 1

    print(f"Unknown design subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
