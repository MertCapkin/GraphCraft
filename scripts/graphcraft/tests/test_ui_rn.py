"""Tests for GraphCraft UI RN tooling."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphcraft.ui.tokens_emit import emit_rn_tokens
from graphcraft.ui.validate import validate_rn


@pytest.fixture
def ui_root(tmp_path: Path) -> Path:
    ds = tmp_path / "design-system" / "components"
    ds.mkdir(parents=True)
    (tmp_path / "design-system" / "tokens.json").write_text(
        json.dumps(
            {
                "color": {
                    "action": {"primary": {"$value": "#111111", "$type": "color"}},
                },
                "spacing": {"button": {"padding": {"$value": "12px", "$type": "dimension"}}},
            }
        ),
        encoding="utf-8",
    )
    (ds / "btn.yaml").write_text("id: component:button-primary\n", encoding="utf-8")
    screens = tmp_path / "design" / "screens"
    screens.mkdir(parents=True)
    (screens / "login.yaml").write_text("id: screen:login\n", encoding="utf-8")

    rn = tmp_path / "packages" / "ui-core" / "rn" / "src" / "components"
    rn.mkdir(parents=True)
    (rn / "ButtonPrimary.tsx").write_text(
        "/** @graphcraft component:button-primary */\n"
        "export const x = { minHeight: TOUCH_TARGET_MIN };\n",
        encoding="utf-8",
    )
    scr = tmp_path / "packages" / "ui-core" / "rn" / "src" / "screens"
    scr.mkdir(parents=True)
    (scr / "LoginScreen.tsx").write_text(
        "/** @graphcraft implements screen:login */\n"
        "export function LoginScreen() { return SafeAreaView; }\n",
        encoding="utf-8",
    )
    (tmp_path / "packages" / "ui-core" / "rn" / "package.json").write_text("{}", encoding="utf-8")
    return tmp_path


def test_emit_rn_tokens(ui_root: Path) -> None:
    out = emit_rn_tokens(ui_root)
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "#111111" in text
    assert "TOUCH_TARGET_MIN" in text


def test_validate_rn_passes(ui_root: Path) -> None:
    assert validate_rn(ui_root) == []


def test_validate_rn_missing_marker(ui_root: Path) -> None:
    (ui_root / "packages" / "ui-core" / "rn" / "src" / "components" / "ButtonPrimary.tsx").write_text(
        "export function ButtonPrimary() {}",
        encoding="utf-8",
    )
    issues = validate_rn(ui_root)
    assert any("button-primary" in i for i in issues)
