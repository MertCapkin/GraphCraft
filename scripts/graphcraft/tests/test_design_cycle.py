"""Tests for GraphCraft design cycle and gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphcraft.design_brief_utils import set_design_brief_status, design_brief_is_ready
from graphcraft.design_state import design_is_ready, save_design_state
from graphcraft.gate_cmd import (
    MSG_DESIGN_NOT_READY,
    design_gate_enabled,
    evaluate_design_file_edit,
    is_ui_implementation_path,
)


@pytest.fixture
def gated_root(tmp_path: Path) -> Path:
    (tmp_path / "graphcraft.config.yaml").write_text(
        "gates:\n  require_design_approval: true\n", encoding="utf-8"
    )
    handoff = tmp_path / "handoff"
    handoff.mkdir()
    (handoff / "DESIGN_BRIEF.md").write_text(
        "# Design Brief\n\n**Status:** Draft\n\n---\n", encoding="utf-8"
    )
    (tmp_path / "packages" / "ui-core" / "rn" / "src").mkdir(parents=True)
    return tmp_path


def test_is_ui_implementation_path() -> None:
    assert is_ui_implementation_path("packages/ui-core/rn/src/foo.tsx")
    assert not is_ui_implementation_path("design/screens/login.yaml")


def test_gate_blocks_ui_core_when_not_ready(gated_root: Path) -> None:
    assert design_gate_enabled(gated_root)
    allow, reason = evaluate_design_file_edit(
        "packages/ui-core/rn/src/components/ButtonPrimary.tsx", gated_root
    )
    assert not allow
    assert reason == MSG_DESIGN_NOT_READY


def test_gate_allows_ui_core_when_ready(gated_root: Path) -> None:
    save_design_state("ready", "t1", root=gated_root, design_ready=True)
    allow, _ = evaluate_design_file_edit(
        "packages/ui-core/rn/src/components/ButtonPrimary.tsx", gated_root
    )
    assert allow


def test_design_brief_ready(gated_root: Path) -> None:
    set_design_brief_status("Ready for Builder", gated_root)
    assert design_brief_is_ready(gated_root)
    assert design_is_ready(gated_root) or design_brief_is_ready(gated_root)


def test_gate_off_file(gated_root: Path) -> None:
    (gated_root / "handoff" / ".design-gate-off").write_text("", encoding="utf-8")
    assert not design_gate_enabled(gated_root)
    allow, _ = evaluate_design_file_edit("packages/ui-core/rn/x.tsx", gated_root)
    assert allow
