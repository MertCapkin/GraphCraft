"""Sync repo-root GraphCraft assets into scripts/graphcraft/assets for PyPI wheels."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "scripts" / "graphcraft" / "assets"

COPY_DIRS = (
    ".cursor/rules",
    ".cursor/commands",
    ".cursor/skills/designer",
    ".cursor/skills/design-strategist",
    ".cursor/skills/stitch-import",
    ".cursor/skills/visual-review",
    ".cursor/skills/mobile-app",
    ".cursor/skills/mobile-game",
    "orchestrator",
    "packs/mobile-app",
    "packs/mobile-game",
    "packs/stitch",
    "packs/styles/minimal-dark",
    "packages/ui-core",
    "packages/assets",
    "design-system",
    "design/screens",
    "handoff",
    ".stitch",
)

COPY_FILES = (
    "graphcraft.config.yaml",
)


def sync() -> int:
    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    ASSETS.mkdir(parents=True)

    for rel in COPY_DIRS:
        src = ROOT / rel
        dst = ASSETS / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    for rel in COPY_FILES:
        src = ROOT / rel
        if src.is_file():
            dst = ASSETS / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    (ASSETS / ".graphcraft-assets-version").write_text("0.1.0\n", encoding="utf-8")
    print(f"Synced GraphCraft assets -> {ASSETS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(sync())
