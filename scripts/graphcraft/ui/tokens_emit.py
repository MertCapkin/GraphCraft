"""Emit stack-specific token files from design-system/tokens.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from ..constants import DESIGN_SYSTEM_DIR

RN_TOKENS_PATH = Path("packages") / "ui-core" / "rn" / "src" / "tokens.ts"
FLUTTER_TOKENS_PATH = Path("packages") / "ui-core" / "flutter" / "lib" / "tokens.dart"
UNITY_TOKENS_PATH = Path("packages") / "ui-core" / "unity" / "Runtime" / "Tokens" / "DesignTokens.cs"
GODOT_TOKENS_PATH = Path("packages") / "ui-core" / "godot" / "tokens.gd"


def _flatten_tokens(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not isinstance(obj, dict):
        return out
    if "$value" in obj or "value" in obj:
        raw = obj.get("$value") or obj.get("value")
        out[prefix] = _normalize_value(raw, obj.get("$type"))
        return out
    for key, child in obj.items():
        if key.startswith("$"):
            continue
        child_prefix = f"{prefix}.{key}" if prefix else key
        out.update(_flatten_tokens(child, child_prefix))
    return out


def _normalize_value(raw: Any, token_type: str | None) -> Any:
    if token_type == "dimension" and isinstance(raw, str):
        match = re.match(r"^([\d.]+)", raw.strip())
        if match:
            return float(match.group(1)) if "." in match.group(1) else int(match.group(1))
    return raw


def _nested_from_flat(flat: dict[str, Any]) -> dict[str, Any]:
    root: dict[str, Any] = {}
    for path, value in flat.items():
        parts = path.split(".")
        cursor = root
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = value
    return root


def load_token_tree(root: Path) -> dict[str, Any]:
    root = root.resolve()
    tokens_path = root / DESIGN_SYSTEM_DIR / "tokens.json"
    if not tokens_path.is_file():
        tokens_path = root / DESIGN_SYSTEM_DIR / "tokens.base.json"
    if not tokens_path.is_file():
        raise FileNotFoundError("design-system/tokens.json not found")
    data = json.loads(tokens_path.read_text(encoding="utf-8"))
    return _nested_from_flat(_flatten_tokens(data))


def _ts_value(value: Any, indent: int) -> str:
    pad = "  " * indent
    if isinstance(value, dict):
        lines = ["{"]
        for k, v in value.items():
            lines.append(f"{pad}  {k}: {_ts_value(v, indent + 1)},")
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, float):
        return str(value)
    return str(value)


def _dart_const_name(path: str) -> str:
    parts = path.split(".")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _emit_dart_consts(nested: dict[str, Any], prefix: str = "") -> list[str]:
    lines: list[str] = []
    for key, value in nested.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            lines.extend(_emit_dart_consts(value, path))
        elif isinstance(value, str) and value.startswith("#"):
            hex_part = value[1:]
            arg = f"0xFF{hex_part.upper()}" if len(hex_part) == 6 else f"0x{hex_part.upper()}"
            lines.append(f"  static const Color {_dart_const_name(path)} = Color({arg});")
        elif isinstance(value, float):
            lines.append(f"  static const double {_dart_const_name(path)} = {value};")
        else:
            lines.append(f"  static const double {_dart_const_name(path)} = {value};")
    return lines


def _csharp_const_name(path: str) -> str:
    return "".join(part.capitalize() for part in path.replace(".", "_").split("_"))


def _emit_csharp_consts(nested: dict[str, Any], prefix: str = "") -> list[str]:
    lines: list[str] = []
    for key, value in nested.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            lines.extend(_emit_csharp_consts(value, path))
        elif isinstance(value, str):
            lines.append(f'        public const string {_csharp_const_name(path)} = "{value}";')
        elif isinstance(value, float):
            lines.append(f"        public const float {_csharp_const_name(path)} = {value}f;")
        else:
            lines.append(f"        public const int {_csharp_const_name(path)} = {value};")
    return lines


def _gd_flat_lines(nested: dict[str, Any], prefix: str = "") -> list[str]:
    lines: list[str] = []
    for key, value in nested.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            lines.extend(_gd_flat_lines(value, path))
        else:
            const_name = path.upper().replace(".", "_")
            if isinstance(value, str) and value.startswith("#"):
                lines.append(f'const {const_name} := Color("{value}")')
            elif isinstance(value, str):
                lines.append(f'const {const_name} := "{value}"')
            elif isinstance(value, float):
                lines.append(f"const {const_name} := {value}")
            else:
                lines.append(f"const {const_name} := {value}")
    return lines


def emit_rn_tokens(root: Path, *, touch_min: int = 44) -> Path:
    nested = load_token_tree(root)
    out_path = root.resolve() / RN_TOKENS_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "/**\n * Semantic design tokens — design-system/tokens.json\n"
        " * Regenerate: graphcraft ui tokens emit rn\n */\n"
    )
    body = _ts_value(nested, 0)
    content = (
        f"{header}export const tokens = {body} as const;\n\n"
        f"export type DesignTokens = typeof tokens;\n\n"
        f"export const TOUCH_TARGET_MIN = {touch_min};\n"
    )
    out_path.write_text(content, encoding="utf-8")
    return out_path


def emit_flutter_tokens(root: Path, *, touch_min: int = 44) -> Path:
    nested = load_token_tree(root)
    out_path = root.resolve() / FLUTTER_TOKENS_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "/// Semantic design tokens — design-system/tokens.json\n"
        "/// Regenerate: graphcraft ui tokens emit flutter\n"
        "import 'package:flutter/material.dart';\n\n"
        "class DesignTokens {\n"
        "  DesignTokens._();\n\n"
        + "\n".join(_emit_dart_consts(nested))
        + f"\n\n  static const double touchTargetMin = {touch_min};\n"
        "}\n"
    )
    out_path.write_text(content, encoding="utf-8")
    return out_path


def emit_unity_tokens(root: Path, *, touch_min: int = 44) -> Path:
    nested = load_token_tree(root)
    out_path = root.resolve() / UNITY_TOKENS_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "// Semantic design tokens — design-system/tokens.json\n"
        "// Regenerate: graphcraft ui tokens emit unity\n"
        "namespace GraphCraft.UI\n"
        "{\n"
        "    public static class DesignTokens\n"
        "    {\n"
        + "\n".join(_emit_csharp_consts(nested))
        + f"\n        public const float TouchTargetMin = {touch_min}f;\n"
        "    }\n"
        "}\n"
    )
    out_path.write_text(content, encoding="utf-8")
    return out_path


def emit_godot_tokens(root: Path, *, touch_min: int = 44) -> Path:
    nested = load_token_tree(root)
    out_path = root.resolve() / GODOT_TOKENS_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "## Semantic design tokens — design-system/tokens.json\n"
        "## Regenerate: graphcraft ui tokens emit godot\n"
        "class_name DesignTokens\n"
        "extends RefCounted\n\n"
        + "\n".join(_gd_flat_lines(nested))
        + f"\n\nconst TOUCH_TARGET_MIN := {touch_min}\n"
    )
    out_path.write_text(content, encoding="utf-8")
    return out_path


EMITTERS: dict[str, Callable[..., Path]] = {
    "rn": emit_rn_tokens,
    "flutter": emit_flutter_tokens,
    "unity": emit_unity_tokens,
    "godot": emit_godot_tokens,
}
