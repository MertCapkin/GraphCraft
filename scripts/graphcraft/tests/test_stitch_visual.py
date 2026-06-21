"""Tests for Stitch MCP, fetch, validate, and visual review."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from graphcraft.design_graph.builder import build_design_graph, update_design_graph
from graphcraft.stitch.fetch import fetch_export
from graphcraft.stitch.mcp import build_mcp_config, doctor_mcp, install_mcp_config
from graphcraft.stitch.validate import validate_stitch_dir
from graphcraft.visual.png_utils import pixel_similarity, png_dimensions
from graphcraft.visual.review import run_visual_review

# 1x1 PNG
_TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


@pytest.fixture
def stitch_export(tmp_path: Path) -> Path:
    export = tmp_path / "export"
    designs = export / "designs"
    designs.mkdir(parents=True)
    (designs / "login.png").write_bytes(_TINY_PNG)
    (export / "DESIGN.md").write_text("# Stitch Design\n", encoding="utf-8")
    (export / "metadata.json").write_text(
        json.dumps(
            {
                "project_id": "test-proj",
                "screens": {
                    "login": {
                        "id": "screen:login",
                        "title": "Login",
                        "png": "login.png",
                    }
                },
                "flows": [],
            }
        ),
        encoding="utf-8",
    )
    return export


@pytest.fixture
def stitch_project(tmp_path: Path, stitch_export: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    fetch_export(project, stitch_export)
    update_design_graph(project)
    return project


def test_mcp_config_build() -> None:
    cfg = build_mcp_config("my-gcp-project")
    entry = cfg["mcpServers"]["stitch"]
    assert entry["command"] == "npx"
    assert "@keeponfirst/kof-stitch-mcp" in entry["args"]
    assert entry["env"]["GOOGLE_CLOUD_PROJECT"] == "my-gcp-project"


def test_mcp_install_and_doctor(tmp_path: Path) -> None:
    (tmp_path / "graphcraft.config.yaml").write_text(
        "stitch:\n  project_id: proj-123\n", encoding="utf-8"
    )
    path = install_mcp_config(tmp_path)
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "stitch" in data["mcpServers"]
    # doctor may warn on npx missing in CI — only assert config structure
    issues = doctor_mcp(tmp_path)
    assert not any("Missing .mcp.json" in i for i in issues)


def test_stitch_validate_passes(stitch_project: Path) -> None:
    assert validate_stitch_dir(stitch_project) == []


def test_stitch_validate_missing_png(stitch_project: Path) -> None:
    (stitch_project / ".stitch" / "designs" / "login.png").unlink()
    issues = validate_stitch_dir(stitch_project)
    assert any("login.png" in i for i in issues)


def test_stitch_fetch(stitch_export: Path, tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    target = fetch_export(project, stitch_export)
    assert (target / "metadata.json").is_file()
    assert (target / "designs" / "login.png").is_file()


def test_png_dimensions(stitch_export: Path) -> None:
    dims = png_dimensions(stitch_export / "designs" / "login.png")
    assert dims == (1, 1)


def test_pixel_similarity_identical(stitch_export: Path, tmp_path: Path) -> None:
    a = stitch_export / "designs" / "login.png"
    b = tmp_path / "copy.png"
    b.write_bytes(a.read_bytes())
    result = pixel_similarity(a, b)
    assert result["overall"] in ("PASS", "WARN")
    assert result["reference_dims"] == (1, 1)


def test_visual_review_warn_without_candidates(stitch_project: Path) -> None:
    result = run_visual_review(stitch_project)
    assert result["overall"] in ("WARN", "FAIL")
    assert result["screens"] or result["warnings"]
