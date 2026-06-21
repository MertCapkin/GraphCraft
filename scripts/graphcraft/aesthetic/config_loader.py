"""Load GraphCraft project configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from ..constants import CONFIG_FILE, STYLES_DIR


def load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_FILE
    if not path.is_file():
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def active_style_id(config: dict[str, Any]) -> str:
    style = (config.get("design") or {}).get("style", "style:minimal-dark")
    return str(style)


def aesthetic_settings(config: dict[str, Any]) -> dict[str, Any]:
    return dict(config.get("aesthetic") or {})


def design_settings(config: dict[str, Any]) -> dict[str, Any]:
    return dict(config.get("design") or {})


def load_style_pack(root: Path, style_id: str) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    slug = style_id.split(":", 1)[-1] if ":" in style_id else style_id
    path = root / STYLES_DIR / slug / "style.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}
