"""Sync repo-root GraphCraft overlay assets into scripts/graphcraft/assets for PyPI wheels.

IMPORTANT: GraphStack files are NOT copied. GraphStack comes from the
MertCapkin_GraphStack dependency via graphstack init.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "scripts" / "graphcraft" / "assets"

# GraphCraft-only directories (no graphstack skills, no full handoff state)
COPY_DIRS = (
    ".cursor/skills/designer",
    ".cursor/skills/design-strategist",
    ".cursor/skills/stitch-import",
    ".cursor/skills/visual-review",
    ".cursor/skills/mobile-app",
    ".cursor/skills/mobile-game",
    "design-system/components",
    "design/screens",
    "packs/styles/minimal-dark",
    "packs/styles/warm-light",
    "packs/mobile-app",
    "packs/mobile-game",
    "packs/stitch",
    "packages/ui-core",
    "packages/assets",
    ".stitch",
)

COPY_FILES = (
    (".cursor/rules/graphcraft.mdc", ".cursor/rules/graphcraft.mdc"),
    (".cursor/commands/graphcraft.md", ".cursor/commands/graphcraft.md"),
    ("orchestrator/GRAPHCRAFT.md", "orchestrator/GRAPHCRAFT.md"),
    ("graphcraft.config.yaml", "graphcraft.config.yaml"),
    ("design-system/tokens.base.json", "design-system/tokens.base.json"),
    ("design-system/tokens.json", "design-system/tokens.json"),
    ("design-system/components/button.example.yaml", "design-system/components/button.example.yaml"),
    ("design/screens/login.example.yaml", "design/screens/login.example.yaml"),
    ("handoff/AESTHETIC_BRIEF.md", "handoff/AESTHETIC_BRIEF.md"),
    ("handoff/DESIGN_BRIEF.md", "handoff/DESIGN_BRIEF.md"),
    ("handoff/BRIEF.md", "handoff/BRIEF.md"),
    ("handoff/REVIEW.md", "handoff/REVIEW.md"),
    ("handoff/STATE.json", "handoff/STATE.json"),
    ("handoff/DESIGN_STATE.json", "handoff/DESIGN_STATE.json"),
    ("handoff/board/README.md", "handoff/board/README.md"),
    ("research/INSPIRATION.template.md", "research/INSPIRATION.template.md"),
    (".stitch/metadata.template.json", ".stitch/metadata.template.json"),
    ("packs/mobile-app/STACKS.md", "packs/mobile-app/STACKS.md"),
    ("packs/mobile-game/STACKS.md", "packs/mobile-game/STACKS.md"),
    ("packs/stitch/README.md", "packs/stitch/README.md"),
    ("packs/styles/minimal-dark/style.yaml", "packs/styles/minimal-dark/style.yaml"),
    ("packages/ui-core/README.md", "packages/ui-core/README.md"),
    ("packages/assets/README.md", "packages/assets/README.md"),
    ("graphcraft-out/.gitkeep", "graphcraft-out/.gitkeep"),
)

BOARD_GITKEEP = (
    "handoff/board/todo/.gitkeep",
    "handoff/board/doing/.gitkeep",
    "handoff/board/done/.gitkeep",
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

    for src_rel, dst_rel in COPY_FILES:
        src = ROOT / src_rel
        dst = ASSETS / dst_rel
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    for rel in BOARD_GITKEEP:
        src = ROOT / rel
        dst = ASSETS / rel
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    (ASSETS / ".graphcraft-assets-version").write_text("2.4.0\n", encoding="utf-8")
    print(f"Synced GraphCraft overlay assets -> {ASSETS}")
    print("  (GraphStack files excluded - installed via dependency)")
    return 0


if __name__ == "__main__":
    raise SystemExit(sync())
