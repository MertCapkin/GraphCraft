"""Distill INSPIRATION.md — filter generic slop and inject differentiation thesis."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from ..constants import RESEARCH_INSPIRATION
from .originality import (
    _DISTILL_FAIL_MARKER,
    _DISTILL_MARKER,
    _patterns_blob,
    _read_brief_field,
    detect_generic_phrases,
)

DISTILL_REPORT = "DISTILL_REPORT.md"


def _extract_pattern_bullets(inspiration: str) -> list[str]:
    bullets: list[str] = []
    if "## Patterns observed" not in inspiration:
        return bullets
    block = inspiration.split("## Patterns observed", 1)[1]
    block = block.split("## References", 1)[0]
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def _duplicate_clusters(bullets: list[str]) -> list[str]:
    """Find repeated sub-phrases across bullets."""
    clusters: list[str] = []
    normalized = [re.sub(r"\s+", " ", b.lower()) for b in bullets]
    for i, a in enumerate(normalized):
        for b in normalized[i + 1 :]:
            words_a = set(re.findall(r"[a-z]{4,}", a))
            words_b = set(re.findall(r"[a-z]{4,}", b))
            overlap = words_a & words_b
            if len(overlap) >= 4:
                clusters.append(", ".join(sorted(overlap)[:6]))
    return clusters


def _identity_overlap(identity: str, patterns: str) -> float:
    if not identity:
        return 0.0
    tokens = [t for t in re.findall(r"[a-z]{4,}", identity.lower()) if len(t) > 3]
    if not tokens:
        return 0.0
    hits = sum(1 for t in tokens if t in patterns)
    return hits / len(tokens)


def _build_thesis(identity: str, profile: str, generic: list[str]) -> str:
    if identity:
        base = identity.rstrip(".")
    else:
        base = f"A distinct {profile.replace('-', ' ')} experience that avoids generic mobile UI templates"
    return f"{base}; differentiation through intentional constraints, not trend copying."


def _will_not_items(generic: list[str], clusters: list[str]) -> list[str]:
    items: list[str] = []
    mapping = {
        "card grid": "Default card-grid dashboards without a signature layout",
        "bottom navigation": "Stock bottom-nav shell with no brand-specific nav pattern",
        "best practices": "Generic 'best practices' copy-paste without project identity",
        "clean and modern": "Unlabeled 'clean modern' aesthetic with no mood anchor",
        "warm minimal": "Trend-only warm-minimal palette without token customization",
    }
    for phrase in generic:
        if phrase in mapping and mapping[phrase] not in items:
            items.append(mapping[phrase])
    for cluster in clusters[:2]:
        items.append(f"Repeated generic cluster: {cluster}")
    defaults = [
        "Pixel clones of well-known consumer apps",
        "INSPIRATION snippets pasted verbatim into screen specs",
    ]
    for d in defaults:
        if d not in items:
            items.append(d)
        if len(items) >= 3:
            break
    return items[:3]


def _render_thesis_section(
    thesis: str,
    will_not: list[str],
    generic: list[str],
    overall: str,
) -> str:
    marker = _DISTILL_MARKER if overall in ("PASS", "WARN") else _DISTILL_FAIL_MARKER
    generic_lines = "\n".join(f"- `{g}`" for g in generic[:8]) or "- (none detected)"
    will_not_lines = "\n".join(f"- {w}" for w in will_not)
    return f"""## Differentiation thesis

{marker}

> {thesis}

### We will NOT
{will_not_lines}

### Generic phrases flagged
{generic_lines}

**Distill:** {overall} ({date.today().isoformat()})

---
"""


def _inject_section(inspiration: str, section: str) -> str:
    if "## Differentiation thesis" in inspiration:
        inspiration = re.sub(
            r"## Differentiation thesis[\s\S]*?---\s*\n",
            "",
            inspiration,
            count=1,
        )
    anchor = "## Accessibility floors"
    if anchor in inspiration:
        return inspiration.replace(anchor, section + anchor, 1)
    return inspiration.rstrip() + "\n\n" + section


def run_distill(root: Path, *, write: bool = True) -> dict[str, Any]:
    root = root.resolve()
    path = root / RESEARCH_INSPIRATION
    if not path.is_file():
        raise FileNotFoundError(f"Missing {RESEARCH_INSPIRATION} — run: graphcraft aesthetic research run")

    text = path.read_text(encoding="utf-8")
    patterns = _patterns_blob(text)
    bullets = _extract_pattern_bullets(text)
    generic = detect_generic_phrases(patterns)
    clusters = _duplicate_clusters(bullets)
    identity = _read_brief_field(root, "Project identity")
    profile_match = re.search(r"\*\*Project profile:\*\*\s*(\S+)", text)
    profile = profile_match.group(1) if profile_match else "mobile-app"
    overlap = _identity_overlap(identity, patterns)

    warnings: list[str] = []
    if len(generic) >= 4:
        warnings.append(f"High generic phrase density ({len(generic)})")
    if clusters:
        warnings.append(f"Duplicate pattern clusters: {clusters[0]}")
    if identity and overlap < 0.15:
        warnings.append("Project identity does not overlap with observed patterns — refine thesis")

    slop_score = len(generic) + len(clusters) * 2
    if slop_score >= 6:
        overall = "FAIL"
    elif slop_score >= 3:
        overall = "WARN"
    else:
        overall = "PASS"

    thesis = _build_thesis(identity, profile, generic)
    will_not = _will_not_items(generic, clusters)
    section = _render_thesis_section(thesis, will_not, generic, overall)

    if write:
        updated = _inject_section(text, section)
        path.write_text(updated, encoding="utf-8")
        report_dir = root / "graphcraft-out"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / DISTILL_REPORT
        lines = [
            "# Distill Report",
            "",
            f"**Overall:** {overall}",
            f"**Generic phrases:** {len(generic)}",
            f"**Duplicate clusters:** {len(clusters)}",
            f"**Identity overlap:** {overlap:.2f}",
            "",
            "## Thesis",
            "",
            f"> {thesis}",
            "",
        ]
        if warnings:
            lines.append("## Warnings")
            lines.append("")
            for w in warnings:
                lines.append(f"- {w}")
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "overall": overall,
        "generic_phrases": generic,
        "duplicate_clusters": clusters,
        "identity_overlap": round(overlap, 3),
        "thesis": thesis,
        "will_not": will_not,
        "warnings": warnings,
    }


def format_distill_summary(result: dict[str, Any]) -> str:
    lines = [
        f"Research distill: {result.get('overall', '?')}",
        f"  generic_phrases={len(result.get('generic_phrases') or [])} "
        f"clusters={len(result.get('duplicate_clusters') or [])} "
        f"identity_overlap={result.get('identity_overlap')}",
    ]
    for w in result.get("warnings") or []:
        lines.append(f"  WARN: {w}")
    return "\n".join(lines)
