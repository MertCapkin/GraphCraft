"""Tests for GraphCraft design graph."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphcraft.design_graph.bridge import build_bridge, unified_query
from graphcraft.design_graph.builder import build_design_graph
from graphcraft.design_graph.harmony import run_harmony_check
from graphcraft.design_graph.query import blast_radius, explain_node, find_path, validate


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
    (screens / "login.yaml").write_text(
        "id: screen:login\ntitle: Login\ncomponents:\n  - component:btn\n"
        "navigation:\n  success: screen:home\n"
        "implements: src/declared/Login.tsx\n",
        encoding="utf-8",
    )
    declared = tmp_path / "src" / "declared"
    declared.mkdir(parents=True)
    (declared / "Login.tsx").write_text("export {};\n", encoding="utf-8")
    src = tmp_path / "src" / "screens"
    src.mkdir(parents=True)
    (src / "Login.tsx").write_text(
        "// @graphcraft implements screen:login\nexport {};\n",
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
    assert "screen:login" in ids
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


def test_path_between_screens(project_root: Path) -> None:
    graph = build_design_graph(project_root)
    out = find_path(graph, "screen:login", "screen:home")
    assert "screen:login" in out
    assert "screen:home" in out
    assert "navigates_to" in out


def test_explain_screen(project_root: Path) -> None:
    graph = build_design_graph(project_root)
    out = explain_node(graph, "screen:login")
    assert "screen:login" in out
    assert "uses_component" in out
    assert "component:btn" in out


def test_radius(project_root: Path) -> None:
    graph = build_design_graph(project_root)
    out = blast_radius(graph, "screen:login", depth=2)
    assert "screen:home" in out
    assert "component:btn" in out


def test_bridge_scan(project_root: Path) -> None:
    build_design_graph(project_root)
    bridge = build_bridge(project_root, heuristic=False)
    designs = {m["design"] for m in bridge["mappings"]}
    assert "screen:login" in designs
    codes = {m["code"] for m in bridge["mappings"]}
    assert "src/declared/Login.tsx" in codes
    assert "src/screens/Login.tsx" in codes
    assert bridge["stats"]["declared"] >= 1
    assert bridge["stats"]["comment"] >= 1


def test_unified_query(project_root: Path) -> None:
    graph = build_design_graph(project_root)
    bridge = build_bridge(project_root, heuristic=False)
    out = unified_query(graph, bridge, "login")
    assert "screen:login" in out
    assert "src/screens/Login.tsx" in out
