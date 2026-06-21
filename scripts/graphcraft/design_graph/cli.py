"""Design graph CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..constants import BRIDGE_JSON, DESIGN_GRAPH_JSON
from .bridge import (
    build_bridge,
    format_bridge_report,
    format_bridge_summary,
    load_bridge,
    unified_query,
    write_bridge,
)
from .builder import update_design_graph
from .harmony import run_harmony_check
from .query import blast_radius, explain_node, find_path, load_graph, query, validate


def _graph_path(args_graph: str) -> Path:
    return Path(args_graph)


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(
            "Usage: graphcraft design "
            "<update|query|path|explain|radius|validate|harmony|bridge|unified|evaluate> ..."
        )
        return 0

    cmd, rest = argv[0], argv[1:]

    if cmd == "update":
        p = argparse.ArgumentParser(prog="graphcraft design update")
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--bridge", action="store_true", help="also rebuild bridge.json")
        args = p.parse_args(rest)
        root = Path(args.root).resolve()
        graph = update_design_graph(root)
        print(
            f"Design graph: {len(graph.get('nodes', []))} nodes, "
            f"{len(graph.get('edges', []))} edges"
        )
        print(f"  -> {root / DESIGN_GRAPH_JSON}")
        if args.bridge:
            bridge = build_bridge(root)
            out = write_bridge(root, bridge)
            print(format_bridge_summary(bridge))
            print(f"  -> {out}")
        return 0

    if cmd == "query":
        p = argparse.ArgumentParser(prog="graphcraft design query")
        p.add_argument("question", help="design graph question")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        path = _graph_path(args.graph)
        if not path.is_file():
            print(f"Missing {path} — run: graphcraft design update .")
            return 1
        print(query(load_graph(path), args.question))
        return 0

    if cmd == "path":
        p = argparse.ArgumentParser(prog="graphcraft design path")
        p.add_argument("start", help="start design node id or label")
        p.add_argument("end", help="end design node id or label")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        path = _graph_path(args.graph)
        if not path.is_file():
            print(f"Missing {path} — run: graphcraft design update .")
            return 1
        print(find_path(load_graph(path), args.start, args.end))
        return 0

    if cmd == "explain":
        p = argparse.ArgumentParser(prog="graphcraft design explain")
        p.add_argument("node", help="design node id or label")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        path = _graph_path(args.graph)
        if not path.is_file():
            print(f"Missing {path} — run: graphcraft design update .")
            return 1
        print(explain_node(load_graph(path), args.node))
        return 0

    if cmd == "radius":
        p = argparse.ArgumentParser(prog="graphcraft design radius")
        p.add_argument("node", help="design node id or label")
        p.add_argument("--depth", type=int, default=2)
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        path = _graph_path(args.graph)
        if not path.is_file():
            print(f"Missing {path} — run: graphcraft design update .")
            return 1
        print(blast_radius(load_graph(path), args.node, args.depth))
        return 0

    if cmd == "validate":
        p = argparse.ArgumentParser(prog="graphcraft design validate")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        path = _graph_path(args.graph)
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
        path = _graph_path(args.graph)
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

    if cmd == "bridge":
        p = argparse.ArgumentParser(prog="graphcraft design bridge")
        p.add_argument("action", nargs="?", default="scan", choices=("scan", "report"))
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--no-heuristic", action="store_true")
        args = p.parse_args(rest)
        root = Path(args.root).resolve()
        bridge = build_bridge(root, heuristic=not args.no_heuristic)
        out = write_bridge(root, bridge)
        if args.action == "report":
            report_path = root / "graphcraft-out" / "BRIDGE_REPORT.md"
            report_path.write_text(format_bridge_report(bridge), encoding="utf-8")
            print(format_bridge_report(bridge))
            print(f"  -> {report_path}")
        else:
            print(format_bridge_summary(bridge))
        print(f"  -> {out}")
        return 0

    if cmd == "unified":
        p = argparse.ArgumentParser(prog="graphcraft design unified")
        p.add_argument("question", help="cross-layer question")
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        p.add_argument("--bridge", default=str(BRIDGE_JSON))
        args = p.parse_args(rest)
        graph_path = _graph_path(args.graph)
        if not graph_path.is_file():
            print(f"Missing {graph_path} — run: graphcraft design update .")
            return 1
        bridge_path = _graph_path(args.bridge)
        bridge_data = load_bridge(bridge_path) if bridge_path.is_file() else None
        print(unified_query(load_graph(graph_path), bridge_data, args.question))
        return 0

    if cmd == "evaluate":
        p = argparse.ArgumentParser(prog="graphcraft design evaluate")
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--screen", default=None)
        p.add_argument("--style", default=None)
        p.add_argument("--graph", default=str(DESIGN_GRAPH_JSON))
        args = p.parse_args(rest)
        from ..aesthetic.evaluate import format_evaluate_summary, run_evaluate, write_aesthetic_report

        root = Path(args.root).resolve()
        graph_path = _graph_path(args.graph)
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

    print(f"Unknown design subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
