"""GraphCraft overlay installer — copies assets without overwriting GraphStack."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent


def install_source_root() -> Path:
    repo = PACKAGE_ROOT.parent.parent
    if (repo / "orchestrator" / "GRAPHCRAFT.md").is_file():
        return repo
    bundled = PACKAGE_ROOT / "assets"
    if (bundled / "orchestrator" / "GRAPHCRAFT.md").is_file():
        return bundled
    raise FileNotFoundError(
        "GraphCraft workflow files not found. Reinstall: pip install MertCapkin_GraphCraft"
    )


def _source_root() -> Path:
    return install_source_root()


DIRS_TO_CREATE = (
    ".cursor/skills/designer",
    ".cursor/skills/design-strategist",
    ".cursor/skills/stitch-import",
    ".cursor/skills/visual-review",
    ".cursor/skills/mobile-app",
    ".cursor/skills/mobile-game",
    "orchestrator",
    "design-system/components",
    "design/screens",
    "design/flows",
    "design/collections",
    "packs/styles",
    "packs/mobile-app",
    "packs/mobile-game",
    "packs/stitch",
    "packages/ui-core",
    "packages/assets",
    "graphcraft-out",
    "research",
    "scripts/graphcraft",
    ".stitch/designs",
)

FILE_COPIES = (
    (".cursor/rules/graphcraft.mdc", ".cursor/rules/graphcraft.mdc"),
    (".cursor/commands/graphcraft.md", ".cursor/commands/graphcraft.md"),
    (".cursor/skills/designer/DESIGNER.md", ".cursor/skills/designer/DESIGNER.md"),
    (
        ".cursor/skills/design-strategist/DESIGN_STRATEGIST.md",
        ".cursor/skills/design-strategist/DESIGN_STRATEGIST.md",
    ),
    (
        ".cursor/skills/stitch-import/STITCH_IMPORT.md",
        ".cursor/skills/stitch-import/STITCH_IMPORT.md",
    ),
    (
        ".cursor/skills/visual-review/VISUAL_REVIEW.md",
        ".cursor/skills/visual-review/VISUAL_REVIEW.md",
    ),
    (".cursor/skills/mobile-app/MOBILE_APP.md", ".cursor/skills/mobile-app/MOBILE_APP.md"),
    (".cursor/skills/mobile-game/MOBILE_GAME.md", ".cursor/skills/mobile-game/MOBILE_GAME.md"),
    ("orchestrator/GRAPHCRAFT.md", "orchestrator/GRAPHCRAFT.md"),
    ("packs/mobile-app/STACKS.md", "packs/mobile-app/STACKS.md"),
    ("packs/mobile-game/STACKS.md", "packs/mobile-game/STACKS.md"),
    ("packs/stitch/README.md", "packs/stitch/README.md"),
    ("packages/ui-core/README.md", "packages/ui-core/README.md"),
    ("packages/assets/README.md", "packages/assets/README.md"),
)

TEMPLATE_COPIES = (
    ("graphcraft.config.yaml", "graphcraft.config.yaml"),
    ("design-system/tokens.base.json", "design-system/tokens.base.json"),
    ("design-system/tokens.json", "design-system/tokens.json"),
    ("design-system/components/button.example.yaml", "design-system/components/button.example.yaml"),
    ("design/screens/login.example.yaml", "design/screens/login.example.yaml"),
    ("packs/styles/minimal-dark/style.yaml", "packs/styles/minimal-dark/style.yaml"),
    ("handoff/AESTHETIC_BRIEF.md", "handoff/AESTHETIC_BRIEF.md"),
    ("handoff/DESIGN_BRIEF.md", "handoff/DESIGN_BRIEF.md"),
    (".stitch/metadata.template.json", ".stitch/metadata.template.json"),
)

PYTHON_PACKAGE_FILES = (
    "__init__.py",
    "__main__.py",
    "cli.py",
    "constants.py",
    "bootstrap.py",
    "installer.py",
    "init_cmd.py",
    "doctor.py",
)

DESIGN_GRAPH_FILES = (
    "__init__.py",
    "builder.py",
    "query.py",
    "harmony.py",
    "stitch_adapter.py",
    "report.py",
    "cli.py",
    "schema.py",
)

STITCH_FILES = ("__init__.py", "cli.py", "import_cmd.py")


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _install_python_package(target: Path) -> int:
    src_pkg = PACKAGE_ROOT
    dst_pkg = target / "scripts" / "graphcraft"
    dst_pkg.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in PYTHON_PACKAGE_FILES:
        src = src_pkg / name
        if src.is_file():
            shutil.copy2(src, dst_pkg / name)
            copied += 1
    dg_src = src_pkg / "design_graph"
    dg_dst = dst_pkg / "design_graph"
    if dg_src.is_dir():
        dg_dst.mkdir(parents=True, exist_ok=True)
        for name in DESIGN_GRAPH_FILES:
            src = dg_src / name
            if src.is_file():
                shutil.copy2(src, dg_dst / name)
                copied += 1
    st_src = src_pkg / "stitch"
    st_dst = dst_pkg / "stitch"
    if st_src.is_dir():
        st_dst.mkdir(parents=True, exist_ok=True)
        for name in STITCH_FILES:
            src = st_src / name
            if src.is_file():
                shutil.copy2(src, st_dst / name)
                copied += 1
    return copied


def install(target: Path, *, non_interactive: bool = False) -> int:
    _ = non_interactive
    target = target.resolve()
    root = _source_root()

    print("")
    print("GraphCraft Installer")
    print("====================")
    print(f"Target: {target}")
    print("")

    for rel in DIRS_TO_CREATE:
        (target / rel).mkdir(parents=True, exist_ok=True)

    for src_rel, dst_rel in FILE_COPIES:
        _copy_if_exists(root / src_rel, target / dst_rel)

    for src_rel, dst_rel in TEMPLATE_COPIES:
        dst = target / dst_rel
        if not dst.exists():
            _copy_if_exists(root / src_rel, dst)

    marker = target / ".graphcraft-framework"
    if not marker.exists():
        marker.write_text(
            "# GraphCraft framework overlay installed.\n"
            "# GraphStack provides orchestration; GraphCraft adds design layer.\n",
            encoding="utf-8",
        )

    count = _install_python_package(target)
    print(f"Python package: {count} files → scripts/graphcraft/")
    print("")
    print("GraphCraft overlay installed.")
    print("  graphcraft design update .")
    print("  graphcraft doctor .")
    print("")
    return 0


def run(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="graphcraft install")
    p.add_argument("target", nargs="?", default=".")
    p.add_argument("-y", "--non-interactive", action="store_true")
    args = p.parse_args(argv)
    return install(Path(args.target), non_interactive=args.non_interactive)


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
