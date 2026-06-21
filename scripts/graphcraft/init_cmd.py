"""One-shot bootstrap: GraphStack init + GraphCraft overlay."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .bootstrap import ensure_graphstack, run_graphstack_init
from .installer import install


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="graphcraft init",
        description="Install GraphStack + GraphCraft into a project.",
    )
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("-y", "--non-interactive", action="store_true")
    parser.add_argument("--skip-graphstack", action="store_true")
    parser.add_argument("--install-deps", action="store_true")
    args = parser.parse_args(argv)
    target = Path(args.target).resolve()

    print("")
    print("GraphCraft init")
    print("===============")
    print(f"Target: {target}")
    print("")

    if args.install_deps:
        if not ensure_graphstack(install=True):
            print("Warning: GraphStack not installed — overlay only.")

    if not args.skip_graphstack:
        prev = Path.cwd()
        try:
            os.chdir(target)
            gs_rc = run_graphstack_init(
                str(target),
                non_interactive=args.non_interactive,
                install_deps=args.install_deps,
            )
        finally:
            os.chdir(prev)
        if gs_rc != 0:
            print("Warning: graphstack init returned non-zero — continuing overlay.")

    rc = install(target, non_interactive=args.non_interactive)

    from .doctor import run_doctor
    prev = Path.cwd()
    try:
        os.chdir(target)
        run_doctor([])
    finally:
        os.chdir(prev)

    rule = target / ".cursor" / "rules" / "graphcraft.mdc"
    if not rule.is_file():
        print("Error: graphcraft.mdc missing after install.")
        return 1

    print("")
    print("Ready — GraphCraft project initialized.")
    print("  GraphStack (dependency): cycle, gate, code graph")
    print("  GraphCraft (overlay):    design graph, style packs, mobile profiles")
    print("")
    print("  graphcraft design update .")
    print("  python -m graphstack graph query \"...\"")
    print("  Describe your mobile app/game in Cursor chat.")
    print("")
    return rc


if __name__ == "__main__":
    import sys
    raise SystemExit(run(sys.argv[1:]))
