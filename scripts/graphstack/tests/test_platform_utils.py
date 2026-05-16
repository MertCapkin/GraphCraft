"""Tests for the OS helpers in ``platform_utils``."""

from __future__ import annotations

import sys

import pytest

from graphstack import platform_utils


def test_find_python_returns_non_empty_list() -> None:
    result = platform_utils.find_python()
    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(s, str) and s for s in result)


def test_find_python_falls_back_to_sys_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform_utils.shutil, "which", lambda _name: None)
    monkeypatch.setattr(platform_utils, "IS_WINDOWS", False)
    assert platform_utils.find_python() == [sys.executable]


def test_find_python_prefers_python3_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    available = {"python3": "/usr/bin/python3"}
    monkeypatch.setattr(
        platform_utils.shutil,
        "which",
        lambda name: available.get(name),
    )
    assert platform_utils.find_python() == ["python3"]


def test_utc_now_iso_is_well_formed() -> None:
    stamp = platform_utils.utc_now_iso()
    # Looks like 2026-05-16T17:00:00+00:00 (or ...Z on some Pythons).
    assert "T" in stamp
    assert stamp.endswith("+00:00") or stamp.endswith("Z")


def test_emoji_safe_passthrough_on_utf(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Stream:
        encoding = "utf-8"

    monkeypatch.setattr(platform_utils.sys, "stdout", _Stream())
    text = "✅ done — 📋"
    assert platform_utils.emoji_safe(text) == text


def test_emoji_safe_downgrades_on_legacy_encoding(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Stream:
        encoding = "cp1254"

    monkeypatch.setattr(platform_utils.sys, "stdout", _Stream())
    out = platform_utils.emoji_safe("✅ ✗ ⚠️")
    assert "[ok]" in out
    assert "[x]" in out
    assert "[!]" in out
    assert "✅" not in out


def test_echo_never_raises_on_unprintable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    platform_utils.echo("plain ASCII line")
    platform_utils.echo("Türkçe ışık ✅")
    captured = capsys.readouterr()
    assert "plain ASCII line" in captured.out
