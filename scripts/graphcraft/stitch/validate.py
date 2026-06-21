"""Validate .stitch/ directory structure."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..constants import STITCH_DIR


def validate_stitch_export(export_dir: Path) -> list[str]:
    """Validate a Stitch export directory (pre-copy layout)."""
    return _validate_stitch_tree(export_dir.resolve())


def validate_stitch_dir(root: Path) -> list[str]:
    root = root.resolve()
    stitch = root / STITCH_DIR
    if not stitch.is_dir():
        return [f"Missing {STITCH_DIR}/ directory"]
    return _validate_stitch_tree(stitch)


def _validate_stitch_tree(stitch: Path) -> list[str]:
    issues: list[str] = []

    meta_path = stitch / "metadata.json"
    if not meta_path.is_file():
        issues.append(f"Missing {STITCH_DIR}/metadata.json")
        return issues

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"metadata.json invalid JSON: {exc}")
        return issues

    if not isinstance(meta, dict):
        issues.append("metadata.json root must be an object")
        return issues

    project_id = meta.get("project_id")
    if not project_id:
        issues.append("metadata.json missing project_id")

    screens = meta.get("screens")
    if not screens:
        issues.append("metadata.json missing screens")
        return issues

    designs = stitch / "designs"
    if not designs.is_dir():
        issues.append(f"Missing {STITCH_DIR}/designs/")
        return issues

    if isinstance(screens, dict):
        items = list(screens.items())
    elif isinstance(screens, list):
        items = [(s.get("id", f"screen-{i}"), s) for i, s in enumerate(screens)]
    else:
        issues.append("screens must be object or array")
        return issues

    for key, spec in items:
        png_name = _png_name(key, spec)
        png_path = designs / png_name
        if not png_path.is_file():
            issues.append(f"Missing reference PNG: {STITCH_DIR}/designs/{png_name}")

    if not (stitch / "DESIGN.md").is_file():
        issues.append(f"Missing {STITCH_DIR}/DESIGN.md (recommended for design system import)")

    return issues


def _png_name(key: str, spec: Any) -> str:
    if isinstance(spec, dict):
        return str(spec.get("png") or f"{key}.png")
    return f"{key}.png"


def stitch_summary(root: Path) -> dict[str, Any]:
    stitch = root / STITCH_DIR
    meta_path = stitch / "metadata.json"
    out: dict[str, Any] = {"valid": False, "screens": 0, "png_count": 0}
    issues = validate_stitch_dir(root)
    out["issues"] = issues
    out["valid"] = not issues

    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            screens = meta.get("screens") or {}
            out["project_id"] = meta.get("project_id")
            if isinstance(screens, dict):
                out["screens"] = len(screens)
            elif isinstance(screens, list):
                out["screens"] = len(screens)
        except json.JSONDecodeError:
            pass

    designs = stitch / "designs"
    if designs.is_dir():
        out["png_count"] = len(list(designs.glob("*.png")))
    return out
