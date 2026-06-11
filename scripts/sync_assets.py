#!/usr/bin/env python3
"""Sync workflow files into scripts/graphstack/assets for PyPI wheels.

Run before release:  python scripts/sync_assets.py
CI publish job runs this automatically.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_ROOT = REPO_ROOT / "scripts" / "graphstack" / "assets"

# Mirrors installer.FILE_COPIES + HANDOFF_TEMPLATES + handoff STATE template paths
WORKFLOW_PATHS = (
    ".cursor/rules/graphstack.mdc",
    ".cursor/commands/graphstack.md",
    "orchestrator/ORCHESTRATOR.md",
    "orchestrator/TOKEN_OPTIMIZER.md",
    ".cursor/skills/architect/ARCHITECT.md",
    ".cursor/skills/builder/BUILDER.md",
    ".cursor/skills/reviewer/REVIEWER.md",
    ".cursor/skills/qa/QA.md",
    ".cursor/skills/ship/SHIP.md",
    ".cursor/skills/bootstrapper/BOOTSTRAPPER.md",
    "handoff/BRIEF.md",
    "handoff/REVIEW.md",
    "handoff/BOOTSTRAP.md",
    "handoff/board/README.md",
    "docs/CURSOR_PROMPTS.md",
    "scripts/board.sh",
    "scripts/board.ps1",
    "scripts/post-commit",
    "scripts/post-commit.ps1",
    "scripts/gate-hook.sh",
    "scripts/gate-hook.ps1",
)


def sync() -> int:
    if ASSETS_ROOT.exists():
        shutil.rmtree(ASSETS_ROOT)
    ASSETS_ROOT.mkdir(parents=True)

    copied = 0
    missing: list[str] = []
    for rel in WORKFLOW_PATHS:
        src = REPO_ROOT / rel
        dst = ASSETS_ROOT / rel
        if not src.is_file():
            missing.append(rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

    marker = ASSETS_ROOT / ".graphstack-assets-version"
    marker.write_text("synced-from-repo\n", encoding="utf-8")

    print(f"sync_assets: copied {copied} files -> {ASSETS_ROOT.relative_to(REPO_ROOT)}")
    if missing:
        print(f"sync_assets: WARNING missing {len(missing)}:", ", ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(sync())
