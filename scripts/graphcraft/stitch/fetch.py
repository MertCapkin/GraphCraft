"""Copy Stitch export directory into project .stitch/."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..constants import STITCH_DIR
from .validate import validate_stitch_dir


def fetch_export(root: Path, export_dir: Path, *, force: bool = False) -> Path:
    root = root.resolve()
    export_dir = export_dir.resolve()
    target = root / STITCH_DIR

    if not export_dir.is_dir():
        raise FileNotFoundError(f"Export directory not found: {export_dir}")

    required = ["metadata.json"]
    for name in required:
        if not (export_dir / name).is_file():
            raise FileNotFoundError(f"Export missing {name} in {export_dir}")

    if target.exists() and not force:
        existing_meta = target / "metadata.json"
        if existing_meta.is_file():
            raise FileExistsError(
                f"{STITCH_DIR}/ already exists — use --force to overwrite"
            )

    if target.exists() and force:
        shutil.rmtree(target)

    shutil.copytree(export_dir, target)
    return target


def run_fetch(root: Path, export_dir: Path, *, force: bool = False) -> int:
    try:
        target = fetch_export(root, export_dir, force=force)
    except (FileNotFoundError, FileExistsError) as exc:
        print(f"Fetch failed: {exc}")
        return 1

    issues = validate_stitch_dir(root)
    print(f"Fetched export -> {target}")
    if issues:
        for i in issues:
            print(f"  WARN: {i}")
        return 1
    print("Stitch fetch: validation PASS")
    return 0
