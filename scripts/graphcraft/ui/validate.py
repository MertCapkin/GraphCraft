"""Validate UI stack implementations against design graph registry."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ..constants import DESIGN_COMPONENTS_DIR, DESIGN_SCREENS_DIR

_COMPONENT_MARKER = re.compile(
    r"@graphcraft\s+component:(?P<id>[\w.-]+)", re.IGNORECASE
)
_SCREEN_MARKER = re.compile(
    r"@graphcraft\s+implements\s+(?P<id>screen:[\w.-]+)", re.IGNORECASE
)


@dataclass(frozen=True)
class StackConfig:
    name: str
    root: Path
    src: Path
    extensions: tuple[str, ...]
    manifest: str
    button_rel: Path
    login_rel: Path
    touch_pattern: re.Pattern[str]
    safe_area_tokens: tuple[str, ...]
    hex_check_button: bool = True


STACKS: dict[str, StackConfig] = {
    "rn": StackConfig(
        name="RN",
        root=Path("packages") / "ui-core" / "rn",
        src=Path("packages") / "ui-core" / "rn" / "src",
        extensions=(".tsx",),
        manifest="package.json",
        button_rel=Path("components") / "ButtonPrimary.tsx",
        login_rel=Path("screens") / "LoginScreen.tsx",
        touch_pattern=re.compile(r"minHeight:\s*TOUCH_TARGET_MIN|minHeight:\s*(\d+)"),
        safe_area_tokens=("SafeAreaView",),
    ),
    "flutter": StackConfig(
        name="Flutter",
        root=Path("packages") / "ui-core" / "flutter",
        src=Path("packages") / "ui-core" / "flutter" / "lib",
        extensions=(".dart",),
        manifest="pubspec.yaml",
        button_rel=Path("components") / "button_primary.dart",
        login_rel=Path("screens") / "login_screen.dart",
        touch_pattern=re.compile(
            r"touchTargetMin|minimumSize.*Size\(|BoxConstraints\(minHeight:"
        ),
        safe_area_tokens=("SafeArea",),
        hex_check_button=False,
    ),
    "unity": StackConfig(
        name="Unity",
        root=Path("packages") / "ui-core" / "unity",
        src=Path("packages") / "ui-core" / "unity" / "Runtime",
        extensions=(".cs",),
        manifest="GraphCraft.UI.asmdef",
        button_rel=Path("Components") / "ButtonPrimary.cs",
        login_rel=Path("Screens") / "LoginScreen.cs",
        touch_pattern=re.compile(r"TouchTargetMin|minHeight\s*=\s*44|sizeDelta\.y"),
        safe_area_tokens=("SafeArea", "Screen.safeArea", "padding"),
        hex_check_button=False,
    ),
    "godot": StackConfig(
        name="Godot",
        root=Path("packages") / "ui-core" / "godot",
        src=Path("packages") / "ui-core" / "godot",
        extensions=(".gd",),
        manifest="plugin.cfg",
        button_rel=Path("components") / "button_primary.gd",
        login_rel=Path("screens") / "login_screen.gd",
        touch_pattern=re.compile(r"TOUCH_TARGET_MIN|custom_minimum_size"),
        safe_area_tokens=("MarginContainer", "SafeArea", "safe_area"),
        hex_check_button=False,
    ),
}


def _norm_component_id(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("component:"):
        return raw
    return f"component:{raw}"


def _norm_screen_id(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("screen:"):
        return raw
    return f"screen:{raw}"


def _yaml_ids(root: Path, directory: Path, key: str = "id") -> set[str]:
    ids: set[str] = set()
    if not directory.is_dir():
        return ids
    try:
        import yaml
    except ImportError:
        return ids
    for path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get(key):
            ids.add(str(data[key]))
    return ids


def _scan_markers(
    src_dir: Path, extensions: tuple[str, ...]
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    components: dict[str, list[str]] = {}
    screens: dict[str, list[str]] = {}
    if not src_dir.is_dir():
        return components, screens
    for path in src_dir.rglob("*"):
        if path.suffix.lower() not in extensions:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.as_posix()
        for m in _COMPONENT_MARKER.finditer(text):
            cid = _norm_component_id(m.group("id"))
            components.setdefault(cid, []).append(rel)
        for m in _SCREEN_MARKER.finditer(text):
            sid = _norm_screen_id(m.group("id"))
            screens.setdefault(sid, []).append(rel)
    return components, screens


def validate_stack_impl(root: Path, cfg: StackConfig) -> list[str]:
    root = root.resolve()
    issues: list[str] = []

    manifest = root / cfg.root / cfg.manifest
    if not manifest.is_file():
        issues.append(f"{cfg.name}: missing {cfg.root / cfg.manifest}")
        return issues

    expected_components = _yaml_ids(root, root / DESIGN_COMPONENTS_DIR)
    expected_screens = _yaml_ids(root, root / DESIGN_SCREENS_DIR)
    found_components, found_screens = _scan_markers(root / cfg.src, cfg.extensions)

    for cid in expected_components:
        if cid not in found_components:
            issues.append(f"{cfg.name} missing implementation marker for {cid}")

    for sid in expected_screens:
        if sid not in found_screens:
            issues.append(f"{cfg.name} missing screen marker for {sid}")

    for cid, files in found_components.items():
        if cid not in expected_components:
            issues.append(f"{cfg.name} undeclared component marker {cid} in {files[0]}")

    btn_path = root / cfg.src / cfg.button_rel
    if btn_path.is_file():
        text = btn_path.read_text(encoding="utf-8")
        if not cfg.touch_pattern.search(text):
            issues.append(f"{cfg.name} ButtonPrimary: touch target pattern not found")
        if cfg.hex_check_button and re.search(r"#[0-9a-fA-F]{3,8}", text):
            issues.append(f"{cfg.name} ButtonPrimary: hardcoded hex — use tokens")

    login_path = root / cfg.src / cfg.login_rel
    if login_path.is_file():
        text = login_path.read_text(encoding="utf-8")
        if not any(tok in text for tok in cfg.safe_area_tokens):
            issues.append(f"{cfg.name} LoginScreen: safe area handling not detected")

    return issues


def validate_rn(root: Path) -> list[str]:
    return validate_stack_impl(root, STACKS["rn"])


def validate_flutter(root: Path) -> list[str]:
    return validate_stack_impl(root, STACKS["flutter"])


def validate_unity(root: Path) -> list[str]:
    return validate_stack_impl(root, STACKS["unity"])


def validate_godot(root: Path) -> list[str]:
    return validate_stack_impl(root, STACKS["godot"])


def validate_stack(root: Path, stack: str) -> list[str]:
    validators = {
        "rn": validate_rn,
        "flutter": validate_flutter,
        "unity": validate_unity,
        "godot": validate_godot,
    }
    fn = validators.get(stack)
    if fn is None:
        return [f"Unknown stack: {stack} (supported: {', '.join(validators)}))"]
    return fn(root)


def validate_all(root: Path) -> list[str]:
    issues: list[str] = []
    for stack in STACKS:
        issues.extend(validate_stack(root, stack))
    return issues
