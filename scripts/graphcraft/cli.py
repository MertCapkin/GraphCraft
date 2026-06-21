"""GraphCraft CLI dispatcher."""

from __future__ import annotations

import argparse
import subprocess
import sys

from . import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graphcraft",
        description="GraphCraft — mobile design layer on GraphStack.",
    )
    parser.add_argument("--version", action="version", version=f"graphcraft {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install", help="Install GraphCraft overlay into a project", add_help=False)
    sub.add_parser("init", help="GraphStack init + GraphCraft overlay", add_help=False)
    sub.add_parser("doctor", help="GraphCraft + GraphStack health check", add_help=False)
    sub.add_parser("design", help="Design graph commands", add_help=False)
    sub.add_parser("stitch", help="Stitch import commands", add_help=False)
    return parser


def _delegate_graphstack(rest: list[str]) -> int:
    cmd = [sys.executable, "-m", "graphstack", *rest]
    return subprocess.run(cmd, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        _build_parser().print_help()
        return 0
    if args[0] == "--version":
        print(f"graphcraft {__version__}")
        return 0

    cmd, rest = args[0], args[1:]

    if cmd == "install":
        from .installer import run as install_run
        return install_run(rest)
    if cmd == "init":
        from .init_cmd import run as init_run
        return init_run(rest)
    if cmd == "doctor":
        from .doctor import run as doctor_run
        return doctor_run(rest)
    if cmd == "design":
        from .design_graph.cli import run as design_run
        return design_run(rest)
    if cmd == "stitch":
        from .stitch.cli import run as stitch_run
        return stitch_run(rest)

    return _delegate_graphstack([cmd, *rest])


if __name__ == "__main__":
    raise SystemExit(main())
