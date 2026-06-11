"""Tests for bundled assets and install source resolution."""

from __future__ import annotations

from pathlib import Path

from graphstack.installer import PACKAGE_ROOT, install_source_root


def test_install_source_root_from_dev_repo() -> None:
    root = install_source_root()
    assert (root / "orchestrator" / "ORCHESTRATOR.md").is_file()


def test_bundled_assets_exist_in_package() -> None:
    assets = PACKAGE_ROOT / "assets"
    assert (assets / "orchestrator" / "ORCHESTRATOR.md").is_file()
    assert (assets / ".cursor" / "rules" / "graphstack.mdc").is_file()


def test_install_from_bundled_assets_only(tmp_path: Path, monkeypatch) -> None:
    from graphstack import installer

    assets = PACKAGE_ROOT / "assets"
    monkeypatch.setattr(
        installer,
        "_source_root",
        lambda: assets,
    )
    target = tmp_path / "consumer"
    target.mkdir()
    assert installer.install(target, non_interactive=True) == 0
    assert (target / "orchestrator" / "ORCHESTRATOR.md").is_file()
    assert (target / ".cursor" / "rules" / "graphstack.mdc").is_file()
    assert (target / "handoff" / "BRIEF.md").is_file()
