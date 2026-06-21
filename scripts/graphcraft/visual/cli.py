"""Visual review CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .review import format_visual_summary, run_diff, run_visual_review, write_visual_report


def run(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: graphcraft visual <review|diff> ...")
        return 0

    cmd, rest = argv[0], argv[1:]

    if cmd == "review":
        p = argparse.ArgumentParser(prog="graphcraft visual review")
        p.add_argument("root", nargs="?", default=".")
        p.add_argument("--screen", default=None)
        p.add_argument("--candidates", default="screenshots", help="candidate PNG directory")
        p.add_argument("--threshold", type=float, default=0.85)
        args = p.parse_args(rest)
        root = Path(args.root).resolve()
        result = run_visual_review(
            root,
            screen_id=args.screen,
            candidates_dir=root / args.candidates,
            threshold=args.threshold,
        )
        report = write_visual_report(root, result)
        print(format_visual_summary(result))
        print(f"  -> {report}")
        return 0 if result["overall"] in ("PASS", "WARN") else 1

    if cmd == "diff":
        p = argparse.ArgumentParser(prog="graphcraft visual diff")
        p.add_argument("--reference", required=True)
        p.add_argument("--candidate", required=True)
        args = p.parse_args(rest)
        result = run_diff(Path(args.reference), Path(args.candidate))
        print(f"Visual diff: {result.get('overall')}")
        print(f"  method={result.get('method')} similarity={result.get('similarity')}")
        if result.get("error"):
            print(f"  error={result['error']}")
        if result.get("note"):
            print(f"  note={result['note']}")
        return 0 if result.get("overall") in ("PASS", "WARN") else 1

    print(f"Unknown visual subcommand: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
