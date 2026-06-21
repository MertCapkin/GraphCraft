"""Build focused aesthetic research queries from project config and brief."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..constants import HANDOFF_AESTHETIC
from .config_loader import aesthetic_settings, load_config

_PROFILE_QUERIES: dict[str, list[str]] = {
    "mobile-app": [
        "{stack} mobile app UI patterns 2026",
        "mobile app onboarding UX best practices",
        "{priority} mobile app color typography trends",
    ],
    "mobile-game": [
        "mobile game HUD menu UI design patterns",
        "mobile game shop inventory UI UX",
        "{priority} mobile game meta UI readability",
    ],
}

_PRIORITY_PHRASES = {
    "balanced": "balanced marketing usability",
    "marketing": "marketing screenshot hero visual",
    "usability": "accessibility forms readability",
}


def _read_brief_identity(root: Path) -> str:
    path = root / HANDOFF_AESTHETIC
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"## Project identity\s*\n+>\s*(.+?)(?:\n\n|\n---)",
        text,
        re.DOTALL,
    )
    if not match:
        return ""
    line = match.group(1).strip()
    if not line or line.startswith("One sentence"):
        return ""
    return line


def _read_brief_queries(root: Path) -> list[str]:
    path = root / HANDOFF_AESTHETIC
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    block_match = re.search(
        r"### Queries \(max 5\)\s*\n(.*?)(?:\n###|\n---)",
        text,
        re.DOTALL,
    )
    if not block_match:
        return []
    queries: list[str] = []
    for line in block_match.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            q = line[2:].strip()
            if q:
                queries.append(q)
    return queries


def build_research_queries(root: Path, *, max_queries: int = 5) -> list[str]:
    """Return up to max_queries search strings for aesthetic research."""
    root = root.resolve()
    config = load_config(root)
    profile = str(config.get("profile") or "mobile-app")
    stack = str(config.get("active_stack") or "react-native")
    aesthetic = aesthetic_settings(config)
    priority = str(aesthetic.get("priority") or "balanced")
    priority_phrase = _PRIORITY_PHRASES.get(priority, priority)

    queries: list[str] = []

    brief_queries = _read_brief_queries(root)
    queries.extend(brief_queries[:max_queries])

    identity = _read_brief_identity(root)
    if identity and len(queries) < max_queries:
        queries.append(f"{identity} mobile UI design patterns")

    templates = _PROFILE_QUERIES.get(profile, _PROFILE_QUERIES["mobile-app"])
    for template in templates:
        if len(queries) >= max_queries:
            break
        q = template.format(stack=stack, priority=priority_phrase)
        if q not in queries:
            queries.append(q)

    return queries[:max_queries]
