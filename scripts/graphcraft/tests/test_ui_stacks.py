"""Tests for GraphCraft UI stacks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphcraft.ui.tokens_emit import EMITTERS
from graphcraft.ui.validate import validate_stack


@pytest.fixture
def ui_root(tmp_path: Path) -> Path:
    ds = tmp_path / "design-system" / "components"
    ds.mkdir(parents=True)
    (tmp_path / "design-system" / "tokens.json").write_text(
        json.dumps(
            {
                "color": {
                    "action": {"primary": {"$value": "#6366F1", "$type": "color"}},
                    "text": {"primary": {"$value": "#FFFFFF", "$type": "color"}},
                    "bg": {"default": {"$value": "#0F172A", "$type": "color"}},
                },
                "spacing": {
                    "button": {"padding": {"$value": "12px", "$type": "dimension"}},
                    "screen": {"padding": {"$value": "16px", "$type": "dimension"}},
                },
                "radius": {"default": {"$value": "8px", "$type": "dimension"}},
            }
        ),
        encoding="utf-8",
    )
    (ds / "btn.yaml").write_text("id: component:button-primary\n", encoding="utf-8")
    screens = tmp_path / "design" / "screens"
    screens.mkdir(parents=True)
    (screens / "login.yaml").write_text("id: screen:login\n", encoding="utf-8")
    return tmp_path


def _write_minimal_stack(root: Path, stack: str) -> None:
    marker_comp = "/** @graphcraft component:button-primary */"
    marker_screen = "/** @graphcraft implements screen:login */"

    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    if stack == "rn":
        base = root / "packages" / "ui-core" / "rn" / "src"
        _write(
            base / "components" / "ButtonPrimary.tsx",
            f"{marker_comp}\nexport const x = {{ minHeight: TOUCH_TARGET_MIN }};\n",
        )
        _write(
            base / "screens" / "LoginScreen.tsx",
            f"{marker_screen}\nexport function LoginScreen() {{ return SafeAreaView; }}\n",
        )
        _write(root / "packages" / "ui-core" / "rn" / "package.json", "{}")

    elif stack == "flutter":
        base = root / "packages" / "ui-core" / "flutter" / "lib"
        _write(
            base / "components" / "button_primary.dart",
            f"// {marker_comp}\nclass B {{ void x() {{ DesignTokens.touchTargetMin; minimumSize: Size(0, 44); }} }}\n",
        )
        _write(
            base / "screens" / "login_screen.dart",
            f"// {marker_screen}\nclass L {{ void x() {{ SafeArea(child: null); }} }}\n",
        )
        _write(root / "packages" / "ui-core" / "flutter" / "pubspec.yaml", "name: x\n")

    elif stack == "unity":
        base = root / "packages" / "ui-core" / "unity" / "Runtime"
        _write(
            base / "Components" / "ButtonPrimary.cs",
            f"{marker_comp}\npublic class B {{ float h = DesignTokens.TouchTargetMin; }}\n",
        )
        _write(
            base / "Screens" / "LoginScreen.cs",
            f"{marker_screen}\npublic class L {{ void M() {{ var p = Screen.safeArea; }} }}\n",
        )
        _write(root / "packages" / "ui-core" / "unity" / "GraphCraft.UI.asmdef", "{}")

    elif stack == "godot":
        base = root / "packages" / "ui-core" / "godot"
        _write(
            base / "components" / "button_primary.gd",
            f"## {marker_comp}\nextends Button\nfunc _r(): custom_minimum_size.y = DesignTokens.TOUCH_TARGET_MIN\n",
        )
        _write(
            base / "screens" / "login_screen.gd",
            f"## {marker_screen}\nextends MarginContainer\nfunc _r(): pass\n",
        )
        _write(base / "plugin.cfg", "[plugin]\n")


@pytest.mark.parametrize("stack", ["rn", "flutter", "unity", "godot"])
def test_emit_tokens(ui_root: Path, stack: str) -> None:
    out = EMITTERS[stack](ui_root)
    assert out.is_file()
    assert out.stat().st_size > 20


@pytest.mark.parametrize("stack", ["rn", "flutter", "unity", "godot"])
def test_validate_stack_passes(ui_root: Path, stack: str) -> None:
    _write_minimal_stack(ui_root, stack)
    assert validate_stack(ui_root, stack) == []
