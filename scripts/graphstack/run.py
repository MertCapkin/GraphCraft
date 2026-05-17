"""Run shell commands with token-safe output compaction.

Usage:
  graphstack run -- git status
  graphstack run --raw -- git diff
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from .compact.registry import compact_command_output
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graphstack run",
        description="Run a command and print token-safe output (stderr preserved).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Disable compaction; print stdout verbatim (quality/debug).",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command after -- (e.g. git status)",
    )
    return parser


def _strip_leading_dashes(argv: list[str]) -> list[str]:
    if argv and argv[0] == "--":
        return argv[1:]
    return argv


def _quality_git_argv(cmd: list[str], *, raw: bool) -> list[str]:
    """Use porcelain status for reliable path preservation when compacting."""
    if raw or len(cmd) < 2:
        return cmd
    exe = cmd[0].lower().removesuffix(".exe")
    if exe != "git":
        return cmd
    sub = cmd[1].lower()
    joined = " ".join(cmd[2:]).lower()
    if sub == "status" and "--porcelain" not in joined and " -s" not in f" {joined} ":
        return cmd[:2] + ["--porcelain=v1", "-b"] + cmd[2:]
    if sub == "log" and "--oneline" not in joined:
        return cmd[:2] + ["--oneline"] + cmd[2:]
    return cmd


def execute(argv: list[str], *, raw: bool = False) -> int:
    cmd = _quality_git_argv(_strip_leading_dashes(argv), raw=raw)
    if not cmd:
        print(
            "graphstack run: missing command (use: graphstack run -- git status)",
            file=sys.stderr,
        )
        return 2

    executable = cmd[0]
    if shutil.which(executable) is None and not executable.startswith("."):
        print(f"graphstack run: command not found: {executable}", file=sys.stderr)
        return 127

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    if raw:
        if stdout:
            print(stdout, end="" if stdout.endswith("\n") else "\n")
        if stderr:
            print(stderr, end="" if stderr.endswith("\n") else "", file=sys.stderr)
        return proc.returncode

    result = compact_command_output(cmd, stdout, stderr)
    if result.text:
        print(result.text)
    elif proc.returncode == 0:
        print(f"(ok, {result.used_compactor}, no stdout)")

    return proc.returncode


def run(argv: list[str] | None = None) -> int:
    args_list = sys.argv[2:] if argv is None else argv
    parser = _build_parser()
    args = parser.parse_args(args_list)
    cmd = _strip_leading_dashes(args.command)
    return execute(cmd, raw=args.raw)
