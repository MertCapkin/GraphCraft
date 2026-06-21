"""UI library CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .tokens_emit import EMITTERS
from .validate import STACKS, validate_all, validate_stack

_STACK_CHOICES = tuple(EMITTERS.keys())


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: graphcraft ui <tokens|validate> ...")
        return 0

    cmd, rest = argv[0], argv[1:]

    if cmd == "tokens":
        if not rest or rest[0] in ("-h", "--help"):
            print(f"Usage: graphcraft ui tokens emit <{'|'.join(_STACK_CHOICES)}> [root]")
            return 0
        if rest[0] != "emit":
            print(f"Usage: graphcraft ui tokens emit <{'|'.join(_STACK_CHOICES)}> [root]")
            return 1
        sub = rest[1:]
        p = argparse.ArgumentParser(prog="graphcraft ui tokens emit")
        p.add_argument("stack", choices=_STACK_CHOICES)
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--touch-min", type=int, default=44)
        args = p.parse_args(sub)
        root = Path(args.root).resolve()
        emitter = EMITTERS[args.stack]
        out = emitter(root, touch_min=args.touch_min)
        print(f"Emitted {args.stack} tokens -> {out}")
        return 0

    if cmd == "validate":
        p = argparse.ArgumentParser(prog="graphcraft ui validate")
        p.add_argument("stack", nargs="?", default="all", choices=(*_STACK_CHOICES, "all"))
        p.add_argument("root", nargs="?", default=".")
        args = p.parse_args(rest)
        root = Path(args.root).resolve()
        if args.stack == "all":
            issues = validate_all(root)
            label = "all stacks"
        else:
            issues = validate_stack(root, args.stack)
            label = args.stack
        if issues:
            for i in issues:
                print(f"  ISSUE: {i}")
            return 1
        print(f"UI validate ({label}): PASS")
        return 0

    print(f"Unknown ui subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
