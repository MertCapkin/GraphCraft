"""WCAG contrast helpers for token hex values."""

from __future__ import annotations

import re
from typing import Tuple


_HEX_RE = re.compile(r"^#([0-9a-fA-F]{6})$")


def parse_hex(color: str) -> Tuple[float, float, float] | None:
    color = color.strip()
    if not _HEX_RE.match(color):
        return None
    r = int(color[1:3], 16) / 255.0
    g = int(color[3:5], 16) / 255.0
    b = int(color[5:7], 16) / 255.0
    return r, g, b


def _linearize(channel: float) -> float:
    if channel <= 0.03928:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: Tuple[float, float, float]) -> float:
    r, g, b = (_linearize(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: str, background: str) -> float | None:
    fg = parse_hex(foreground)
    bg = parse_hex(background)
    if fg is None or bg is None:
        return None
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def passes_contrast(foreground: str, background: str, minimum: float = 4.5) -> bool | None:
    ratio = contrast_ratio(foreground, background)
    if ratio is None:
        return None
    return ratio >= minimum
