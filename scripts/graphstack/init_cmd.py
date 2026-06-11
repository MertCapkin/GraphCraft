"""One-shot project bootstrap: install GraphStack + refresh graph + health check.

Replaces the manual four-step onboarding (install → graphify → doctor → hooks)
with a single command for new or existing target projects.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .bootstrap import ensure_graphify, run_graphify_cursor_install
from .graph import run_update as graph_update
from .installer import install
from .platform_utils import echo, graphify_available
from .validate import run_doctor


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="graphstack init",
        description="Install GraphStack into a project, refresh the code graph, run doctor.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project root (default: current directory).",
    )
    parser.add_argument(
        "-y", "--non-interactive",
        action="store_true",
        help="Skip interactive install prompts (CI-friendly).",
    )
    parser.add_argument(
        "--skip-graph",
        action="store_true",
        help="Skip graphify update even when graphify is installed.",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="pip install graphifyy if missing; run graphify cursor install.",
    )
    args = parser.parse_args(argv)
    target = Path(args.target).resolve()

    echo("")
    echo("GraphStack init")
    echo("===============")
    echo(f"Target: {target}")
    echo("")

    if args.install_deps:
        if not ensure_graphify(install=True):
            echo("Warning: could not install graphify — continue without graph refresh.")

    rc = install(target, non_interactive=args.non_interactive)
    if rc != 0:
        return rc

    if args.install_deps and graphify_available():
        echo("")
        echo("Registering Graphify in Cursor (.cursor/rules)...")
        cursor_rc = run_graphify_cursor_install()
        if cursor_rc != 0:
            echo("Warning: graphify cursor install failed — run manually: graphify cursor install")

    if not args.skip_graph and graphify_available():
        echo("")
        echo("Refreshing code graph (AST-only, no API cost)...")
        prev = Path.cwd()
        try:
            os.chdir(target)
            graph_rc = graph_update(["."])
        finally:
            os.chdir(prev)
        if graph_rc != 0:
            echo("Warning: graph update failed — run manually: graphify update .")
    elif not args.skip_graph:
        echo("")
        echo("Skipping graph update (graphify not on PATH).")
        if not args.install_deps:
            echo("  Tip: re-run with --install-deps or: pip install \"graphifyy>=0.7,<0.9\"")

    echo("")
    echo("Health check:")
    prev = Path.cwd()
    try:
        os.chdir(target)
        doctor_rc = run_doctor([])
    finally:
        os.chdir(prev)

    graph_report = target / "graphify-out" / "GRAPH_REPORT.md"
    echo("")
    if graph_report.is_file():
        echo("Ready. Describe your task in Cursor — GraphStack rules load automatically.")
        echo("  graph query:  python -m graphstack graph query \"your question\"")
    else:
        echo("Next: build the full knowledge graph in Cursor chat → /graphify .")
        echo("  (code-only graph: graphstack graph update .)")
    echo("  process gate:  python -m graphstack gate check")
    echo("")

    return doctor_rc


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
