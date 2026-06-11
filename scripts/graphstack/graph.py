"""Graphify query wrapper — graph-first reads without raw file grepping.

Delegates to the ``graphify`` CLI (``graphify query``, ``path``, ``explain``,
``update``). Prefer this over reading ``graph.json`` manually or loading the
full ``GRAPH_REPORT.md`` for targeted questions.

Usage::

    python -m graphstack graph query "who calls login"
    python -m graphstack graph path src/auth/login.ts src/utils/crypto.ts
    python -m graphstack graph explain "login()"
    python -m graphstack graph update .
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .constants import GRAPH_JSON, GRAPHIFY_OUT
from .platform_utils import echo, find_python, graphify_available


def graphify_argv(*args: str) -> list[str]:
    """Return argv prefix to invoke graphify (PATH binary or ``python -m graphify``)."""
    if graphify_available():
        return ["graphify", *args]
    return [*find_python(), "-m", "graphify", *args]


def _default_graph() -> str:
    return str(GRAPH_JSON)


def _run_graphify(sub_args: list[str]) -> int:
    if not graphify_available() and not shutil.which(find_python()[0]):
        echo("graphify not found. Install with: pip install \"graphifyy>=0.7,<0.9\"")
        return 1
    proc = subprocess.run(
        graphify_argv(*sub_args),
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode


def _add_graph_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--graph",
        default=_default_graph(),
        help=f"path to graph.json (default: {GRAPH_JSON})",
    )


def run_query(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="graphstack graph query")
    parser.add_argument("question", help="natural-language graph question")
    _add_graph_arg(parser)
    parser.add_argument("--budget", type=int, default=None, help="token budget cap")
    parser.add_argument("--dfs", action="store_true", help="depth-first instead of BFS")
    args = parser.parse_args(argv)

    sub = ["query", args.question, "--graph", args.graph]
    if args.budget is not None:
        sub.extend(["--budget", str(args.budget)])
    if args.dfs:
        sub.append("--dfs")
    return _run_graphify(sub)


def run_path(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="graphstack graph path")
    parser.add_argument("start", help="start node label or file path")
    parser.add_argument("end", help="end node label or file path")
    _add_graph_arg(parser)
    args = parser.parse_args(argv)
    return _run_graphify(["path", args.start, args.end, "--graph", args.graph])


def run_explain(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="graphstack graph explain")
    parser.add_argument("node", help="node label to explain")
    _add_graph_arg(parser)
    args = parser.parse_args(argv)
    return _run_graphify(["explain", args.node, "--graph", args.graph])


def run_update(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="graphstack graph update",
        description="Re-extract code files into the graph (no LLM, local AST only).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="project root to update (default: .)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite graph even if node count drops (refactors)",
    )
    args = parser.parse_args(argv)
    sub = ["update", args.path]
    if args.force:
        sub.append("--force")
    return _run_graphify(sub)


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        echo("GraphStack Graph — graphify wrappers (graph-first reads):")
        echo("  query <question> [--graph PATH] [--budget N] [--dfs]")
        echo("  path <start> <end> [--graph PATH]")
        echo("  explain <node> [--graph PATH]")
        echo("  update [path] [--force]     AST-only graph refresh")
        echo("")
        echo("Requires graphify on PATH or: pip install \"graphifyy>=0.7,<0.9\"")
        if GRAPHIFY_OUT.is_dir():
            echo(f"Graph dir: {GRAPHIFY_OUT}/")
        return 0

    cmd, rest = argv[0], argv[1:]
    if cmd == "query":
        return run_query(rest)
    if cmd == "path":
        return run_path(rest)
    if cmd == "explain":
        return run_explain(rest)
    if cmd == "update":
        return run_update(rest)

    echo(f"Unknown graph command: '{cmd}'")
    return 2


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
