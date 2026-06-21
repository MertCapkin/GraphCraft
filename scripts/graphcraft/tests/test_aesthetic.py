"""Tests for GraphCraft aesthetic engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphcraft.aesthetic.contrast import contrast_ratio, passes_contrast
from graphcraft.aesthetic.evaluate import run_evaluate
from graphcraft.aesthetic.research import init_inspiration, validate_inspiration
from graphcraft.design_graph.builder import build_design_graph


@pytest.fixture
def aesthetic_root(tmp_path: Path) -> Path:
    tokens = {
        "color": {
            "text": {"primary": {"$value": "#111111", "$type": "color"}},
            "bg": {"default": {"$value": "#FFFFFF", "$type": "color"}},
        }
    }
    ds = tmp_path / "design-system"
    (ds / "components").mkdir(parents=True)
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    (ds / "components" / "btn.yaml").write_text(
        "id: component:btn\nstyle_compatibility:\n  - style:test\n",
        encoding="utf-8",
    )
    screens = tmp_path / "design" / "screens"
    screens.mkdir(parents=True)
    (screens / "home.yaml").write_text(
        "id: screen:home\ntitle: Home\ncomponents:\n  - component:btn\n"
        "tokens:\n  - color.text.primary\n  - color.bg.default\n"
        "acceptance:\n  touch_target_min: 48\n",
        encoding="utf-8",
    )
    styles = tmp_path / "packs" / "styles" / "test"
    styles.mkdir(parents=True)
    (styles / "style.yaml").write_text(
        "id: style:test\nlabel: Test\ncomponents:\n  preferred:\n    - component:btn\n",
        encoding="utf-8",
    )
    (tmp_path / "graphcraft.config.yaml").write_text(
        "design:\n  style: style:test\n  touch_target_min: 44\n"
        "aesthetic:\n  priority: balanced\n  hard_floors:\n    contrast_min: 4.5\n",
        encoding="utf-8",
    )
    return tmp_path


def test_contrast_ratio_passes() -> None:
    ratio = contrast_ratio("#111111", "#FFFFFF")
    assert ratio is not None
    assert ratio > 4.5
    assert passes_contrast("#111111", "#FFFFFF", 4.5) is True


def test_contrast_ratio_fails_floor() -> None:
    ratio = contrast_ratio("#CCCCCC", "#FFFFFF")
    assert ratio is not None
    assert ratio < 4.5
    assert passes_contrast("#CCCCCC", "#FFFFFF", 4.5) is False


def test_evaluate_pass(aesthetic_root: Path) -> None:
    graph = build_design_graph(aesthetic_root)
    result = run_evaluate(aesthetic_root, graph)
    assert result["overall"] in ("PASS", "WARN")
    assert result["scores"]["contrast"] >= 0.9


def test_evaluate_fail_low_contrast(tmp_path: Path) -> None:
    tokens = {
        "color": {
            "text": {"primary": {"$value": "#CCCCCC", "$type": "color"}},
            "bg": {"default": {"$value": "#FFFFFF", "$type": "color"}},
        }
    }
    ds = tmp_path / "design-system"
    (ds / "components").mkdir(parents=True)
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    (ds / "components" / "btn.yaml").write_text("id: component:btn\n", encoding="utf-8")
    screens = tmp_path / "design" / "screens"
    screens.mkdir(parents=True)
    (screens / "home.yaml").write_text(
        "id: screen:home\ncomponents:\n  - component:btn\n"
        "tokens:\n  - color.text.primary\n  - color.bg.default\n",
        encoding="utf-8",
    )
    styles = tmp_path / "packs" / "styles" / "test"
    styles.mkdir(parents=True)
    (styles / "style.yaml").write_text("id: style:test\n", encoding="utf-8")
    (tmp_path / "graphcraft.config.yaml").write_text(
        "design:\n  style: style:test\naesthetic:\n  hard_floors:\n    contrast_min: 4.5\n",
        encoding="utf-8",
    )
    graph = build_design_graph(tmp_path)
    result = run_evaluate(tmp_path, graph)
    assert result["overall"] == "FAIL"
    assert any("FAIL Contrast" in w for w in result["warnings"])


def test_research_init_and_validate(tmp_path: Path) -> None:
    path = init_inspiration(tmp_path)
    assert path.is_file()
    issues = validate_inspiration(tmp_path)
    assert issues  # template has placeholders

    filled = path.read_text(encoding="utf-8").replace("YYYY-MM-DD", "2026-06-21")
    filled = filled.replace("1. \n", "1. mobile onboarding patterns 2026\n", 1)
    path.write_text(filled, encoding="utf-8")
    assert validate_inspiration(tmp_path) == []
