"""GraphCraft health check."""

from __future__ import annotations

import argparse
from pathlib import Path

from .bootstrap import graphstack_available
from .constants import (
    CONFIG_FILE,
    DESIGN_GRAPH_JSON,
    DESIGN_SYSTEM_DIR,
    GRAPHCRAFT_OUT,
    HANDOFF_AESTHETIC,
    HANDOFF_DESIGN,
)


def _ok(msg: str) -> None:
    print(f"  OK  {msg}")


def _warn(msg: str) -> None:
    print(f"  WARN  {msg}")


def _fail(msg: str) -> None:
    print(f"  FAIL  {msg}")


def run_doctor(argv: list[str]) -> int:
    _ = argv
    root = Path.cwd()
    issues = 0

    print("")
    print("GraphCraft doctor")
    print("=================")
    print(f"Root: {root}")
    print("")

    if (root / ".graphcraft-framework").is_file():
        _ok(".graphcraft-framework marker")
    else:
        _warn("Not a GraphCraft project — run: graphcraft init .")
        issues += 1

    if graphstack_available():
        _ok("GraphStack Python package available")
    else:
        _warn("GraphStack not installed — pip install MertCapkin_GraphStack[graphify]")
        issues += 1

    if (root / ".cursor" / "rules" / "graphcraft.mdc").is_file():
        _ok(".cursor/rules/graphcraft.mdc")
    else:
        _fail("graphcraft.mdc missing")
        issues += 1

    if (root / ".cursor" / "rules" / "graphstack.mdc").is_file():
        _ok(".cursor/rules/graphstack.mdc (GraphStack layer)")
    else:
        _warn("graphstack.mdc missing — run graphstack init or graphcraft init")

    if CONFIG_FILE.is_file():
        _ok("graphcraft.config.yaml")
    else:
        _warn("graphcraft.config.yaml missing — template not installed")

    if DESIGN_SYSTEM_DIR.is_dir():
        _ok("design-system/")
    else:
        _warn("design-system/ missing")

    if DESIGN_GRAPH_JSON.is_file():
        _ok(f"{DESIGN_GRAPH_JSON}")
    else:
        _warn("design graph not built — run: graphcraft design update .")

    if HANDOFF_AESTHETIC.is_file():
        _ok("handoff/AESTHETIC_BRIEF.md template")
    if HANDOFF_DESIGN.is_file():
        _ok("handoff/DESIGN_BRIEF.md template")

    if GRAPHCRAFT_OUT.is_dir():
        _ok("graphcraft-out/")
    print("")
    if issues:
        print(f"Doctor finished with {issues} issue(s).")
        return 0
    print("Doctor: all core checks passed.")
    return 0


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="graphcraft doctor")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    return run_doctor(argv)


if __name__ == "__main__":
    import sys
    raise SystemExit(run(sys.argv[1:]))
