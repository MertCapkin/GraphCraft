"""Tests for GraphCraft design graph."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphcraft.design_graph.builder import build_design_graph
from graphcraft.design_graph.harmony import run_harmony_check
from graphcraft.design_graph.query import validate


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    tokens = {
        "color": {
            "action": {
                "primary": {"$value": "#000", "$type": "color"},
            }
        }
    }
    ds = tmp_path / "design-system"
    (ds / "components").mkdir(parents=True)
    (ds / "screens").mkdir(parents=True)
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    (ds / "components" / "btn.yaml").write_text(
        "id: component:btn\nuses_tokens:\n  - color.action.primary\n",
        encoding="utf-8",
    )
    screens = tmp_path / "design" / "screens"
    screens.mkdir(parents=True)
    (screens / "home.yaml").write_text(
        "id: screen:home\ntitle: Home\ncomponents:\n  - component:btn\n",
        encoding="utf-8",
    )
    styles = tmp_path / "packs" / "styles" / "test"
    styles.mkdir(parents=True)
    (styles / "style.yaml").write_text(
        "id: style:test\nlabel: Test\ncomponents:\n  preferred:\n    - component:btn\n",
        encoding="utf-8",
    )
    return tmp_path


def test_build_design_graph(project_root: Path) -> None:
    graph = build_design_graph(project_root)
    ids = {n["id"] for n in graph["nodes"]}
    assert "screen:home" in ids
    assert "component:btn" in ids
    assert "style:test" in ids
    assert any(n["id"].startswith("token:") for n in graph["nodes"])


def test_validate_passes(project_root: Path) -> None:
    graph = build_design_graph(project_root)
    assert validate(graph) == []


def test_harmony_pass(project_root: Path) -> None:
    graph = build_design_graph(project_root)
    result = run_harmony_check(graph)
    assert result["overall"] == "PASS"
