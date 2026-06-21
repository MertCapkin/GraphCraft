"""Synthesize patterns and style directions from search results."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..constants import STYLES_DIR
from .config_loader import aesthetic_settings, load_config, load_style_pack
from .web_search import SearchResult

_PATTERN_RULES: dict[str, tuple[str, ...]] = {
    "layout": (
        "grid",
        "card",
        "tab",
        "navigation",
        "bottom",
        "list",
        "sidebar",
        "safe area",
        "spacing",
        "layout",
    ),
    "typography": (
        "font",
        "typography",
        "heading",
        "hierarchy",
        "readable",
        "text",
        "scale",
        "line height",
    ),
    "color": (
        "color",
        "palette",
        "contrast",
        "dark",
        "light",
        "warm",
        "accent",
        "neutral",
        "mood",
    ),
    "motion": (
        "animation",
        "motion",
        "transition",
        "gesture",
        "micro",
        "haptic",
        "interaction",
    ),
}

_RISK_KEYWORDS = ("clone", "copy", "trademark", "copyright", "ripoff", "knockoff")


def _text_blob(results: list[SearchResult]) -> str:
    parts = [f"{r.title} {r.snippet}" for r in results]
    return " ".join(parts).lower()


def synthesize_patterns(results: list[SearchResult]) -> dict[str, list[str]]:
    blob = _text_blob(results)
    patterns: dict[str, list[str]] = {
        "layout": [],
        "typography": [],
        "color": [],
        "motion": [],
    }

    for category, keywords in _PATTERN_RULES.items():
        hits = [kw for kw in keywords if kw in blob]
        if hits:
            patterns[category].append(
                f"Research highlights: {', '.join(sorted(set(hits))[:6])}."
            )
        for item in results:
            snippet = item.snippet.lower()
            if any(kw in snippet for kw in keywords):
                line = f"{item.title}: {item.snippet[:140].rstrip()}."
                if line not in patterns[category]:
                    patterns[category].append(line)

    for category in patterns:
        if not patterns[category]:
            patterns[category].append("No strong signal — refine queries or run with live search.")

    return patterns


def _score_style_pack(pack: dict[str, Any], blob: str, priority: str) -> tuple[int, str, str]:
    mood = " ".join(str(m) for m in (pack.get("mood") or []))
    label = str(pack.get("label") or pack.get("id") or "style")
    style_id = str(pack.get("id") or "style:unknown")
    score = 0
    for token in re.findall(r"[a-z]+", f"{label} {mood}".lower()):
        if token in blob:
            score += 2
    pack_priority = str(pack.get("priority") or "balanced")
    if pack_priority == priority:
        score += 3
    marketing = "high" if pack_priority == "marketing" else "medium"
    usability = "high" if pack_priority == "balanced" else "medium"
    if priority == "usability":
        usability = "high"
        marketing = "medium"
    elif priority == "marketing":
        marketing = "high"
    return score, marketing, usability


def suggest_style_directions(root: Path, results: list[SearchResult]) -> list[dict[str, str]]:
    root = root.resolve()
    config = load_config(root)
    priority = str(aesthetic_settings(config).get("priority") or "balanced")
    blob = _text_blob(results)

    styles_dir = root / STYLES_DIR
    candidates: list[tuple[int, dict[str, str]]] = []
    if styles_dir.is_dir():
        for child in sorted(styles_dir.iterdir()):
            if not child.is_dir():
                continue
            pack = load_style_pack(root, f"style:{child.name}")
            if not pack:
                continue
            score, marketing, usability = _score_style_pack(pack, blob, priority)
            mood = ", ".join(str(m) for m in (pack.get("mood") or [])) or "—"
            candidates.append(
                (
                    score,
                    {
                        "id": str(pack.get("id") or f"style:{child.name}"),
                        "name": str(pack.get("label") or child.name),
                        "mood": mood,
                        "marketing": marketing,
                        "usability": usability,
                    },
                )
            )

    candidates.sort(key=lambda x: x[0], reverse=True)
    directions = [item[1] for item in candidates[:3]]
    while len(directions) < 3:
        n = len(directions) + 1
        directions.append(
            {
                "id": f"style:direction-{n}",
                "name": f"Direction {n}",
                "mood": "—",
                "marketing": "medium",
                "usability": "medium",
            }
        )
    return directions


def detect_risk_notes(results: list[SearchResult]) -> list[str]:
    notes: list[str] = []
    for item in results:
        text = f"{item.title} {item.snippet}".lower()
        if any(k in text for k in _RISK_KEYWORDS):
            notes.append(f"Review source for clone risk: {item.url}")
    if not notes:
        notes.append("Avoid pixel-level clones of branded apps; extract layout and flow patterns only.")
    return notes
