"""PyPI wheel must ship ``.cursor`` workflow files inside ``graphstack/assets``."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
WHEEL_GLOB = "mertcapkin_graphstack-*.whl"

REQUIRED_ASSET_PATHS = (
    "graphstack/assets/.cursor/rules/graphstack.mdc",
    "graphstack/assets/.cursor/commands/graphstack.md",
    "graphstack/assets/.cursor/skills/architect/ARCHITECT.md",
    "graphstack/assets/.cursor/skills/builder/BUILDER.md",
)


def _latest_wheel(dist_dir: Path) -> Path | None:
    wheels = sorted(dist_dir.glob(WHEEL_GLOB), key=lambda p: p.stat().st_mtime)
    return wheels[-1] if wheels else None


@pytest.mark.parametrize("member", REQUIRED_ASSET_PATHS)
def test_wheel_includes_cursor_assets(member: str) -> None:
    for dist_name in ("dist", "dist_test"):
        dist_dir = REPO_ROOT / dist_name
        wheel = _latest_wheel(dist_dir)
        if wheel is None:
            continue
        with zipfile.ZipFile(wheel) as archive:
            names = set(archive.namelist())
        assert member in names, (
            f"{member} missing from {wheel.name}; "
            "dot-directories under assets/ need explicit package-data"
        )
        return
    pytest.skip("no built wheel in dist/ or dist_test/ — run python -m build first")
