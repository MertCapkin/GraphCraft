"""Originality scoring — anti-generic / anti-slop heuristics."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..constants import DESIGN_SCREENS_DIR, DESIGN_SYSTEM_DIR, HANDOFF_AESTHETIC, RESEARCH_INSPIRATION
from .config_loader import active_style_id, aesthetic_settings, load_config, load_style_pack
from .graph_utils import flatten_tokens, index_graph, load_tokens, screen_components

GENERIC_PHRASES: tuple[str, ...] = (
    "clean and modern",
    "clean modern",
    "best practices",
    "user-friendly",
    "user friendly",
    "card grid",
    "bottom navigation",
    "minimal design",
    "intuitive",
    "seamless",
    "sleek",
    "beautiful ui",
    "engaging",
    "delightful",
    "industry standard",
    "mobile-first",
    "onboarding flow",
    "call to action",
    "hero section",
    "warm minimal",
    "friendly warm",
    "clear heading",
    "scanability",
)

_DISTILL_MARKER = "<!-- graphcraft-distill: PASS -->"
_DISTILL_FAIL_MARKER = "<!-- graphcraft-distill: FAIL -->"


def detect_generic_phrases(text: str) -> list[str]:
    lower = text.lower()
    return [p for p in GENERIC_PHRASES if p in lower]


def _read_inspiration(root: Path) -> str:
    path = root / RESEARCH_INSPIRATION
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _read_brief_field(root: Path, section: str) -> str:
    path = root / HANDOFF_AESTHETIC
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    pattern = rf"## {re.escape(section)}\s*\n+>\s*(.+?)(?:\n\n|\n---)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        line = match.group(1).strip()
        if line.startswith("One sentence"):
            return ""
        return line
    block = re.search(rf"## {re.escape(section)}\s*\n(.*?)(?:\n##|\n---)", text, re.DOTALL | re.IGNORECASE)
    if not block:
        return ""
    lines = [
        ln.strip().lstrip("- ").strip()
        for ln in block.group(1).splitlines()
        if ln.strip().startswith("-") and ln.strip() != "-"
    ]
    return lines[0] if lines else ""


def _patterns_blob(inspiration: str) -> str:
    if "## Patterns observed" not in inspiration:
        return inspiration.lower()
    start = inspiration.index("## Patterns observed")
    end = inspiration.find("## References", start)
    block = inspiration[start:end] if end > start else inspiration[start:]
    return block.lower()


def score_reference_independence(root: Path) -> tuple[float, list[str], list[str]]:
    """Penalize verbatim generic INSPIRATION phrases appearing in design YAML."""
    warnings: list[str] = []
    passed: list[str] = []
    inspiration = _read_inspiration(root)
    if not inspiration:
        warnings.append("Originality: no INSPIRATION.md for reference check")
        return 0.5, warnings, passed

    patterns = _patterns_blob(inspiration)
    generic_hits = detect_generic_phrases(patterns)
    screens_dir = root / DESIGN_SCREENS_DIR
    if not screens_dir.is_dir():
        return 0.6, warnings, passed

    yaml_blob = ""
    for path in screens_dir.glob("*.yaml"):
        yaml_blob += path.read_text(encoding="utf-8").lower() + "\n"

    if not yaml_blob.strip():
        warnings.append("Originality: no design screen YAML to compare")
        return 0.55, warnings, passed

    copies = [p for p in generic_hits if p in yaml_blob]
    if copies:
        warnings.append(
            f"Originality: generic INSPIRATION phrases copied into design YAML: {', '.join(copies[:3])}"
        )
        score = max(0.0, 1.0 - len(copies) * 0.2)
    else:
        passed.append("Originality: no generic research phrases copied verbatim into screens")
        score = 1.0
    return score, warnings, passed


def score_token_customization(root: Path) -> tuple[float, list[str], list[str]]:
    warnings: list[str] = []
    passed: list[str] = []
    tokens = flatten_tokens(load_tokens(root))
    if not tokens:
        warnings.append("Originality: no design tokens to score customization")
        return 0.4, warnings, passed

    hex_tokens = {k: v for k, v in tokens.items() if isinstance(v, str) and v.startswith("#")}
    if not hex_tokens:
        warnings.append("Originality: no hex color tokens found")
        return 0.5, warnings, passed

    config = load_config(root)
    style_pack = load_style_pack(root, active_style_id(config))
    mood = " ".join(str(m) for m in (style_pack.get("mood") or [])).lower()

    # Heuristic: more than default-like palette spread suggests customization
    unique_hex = len(set(hex_tokens.values()))
    depth = len(hex_tokens)
    spread_score = min(1.0, unique_hex / max(depth, 1))
    depth_score = min(1.0, depth / 8.0)
    score = (spread_score * 0.6) + (depth_score * 0.4)

    if unique_hex <= 2:
        warnings.append("Originality: token palette looks minimal/default (few unique colors)")
        score = min(score, 0.45)
    else:
        passed.append(f"Originality: {unique_hex} unique colors across {depth} token paths")

    if mood and any(m in mood for m in ("calm", "friendly", "premium")) and unique_hex <= 3:
        warnings.append("Originality: style pack mood set but tokens barely customized")

    return round(score, 3), warnings, passed


def score_layout_diversity(graph: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    warnings: list[str] = []
    passed: list[str] = []
    nodes, _ = index_graph(graph)
    screens = [n for n in nodes.values() if n.get("type") == "screen"]
    if len(screens) < 2:
        passed.append("Originality: single screen — layout diversity N/A")
        return 0.75, warnings, passed

    sets: list[set[str]] = []
    for screen in screens:
        comps = set(screen_components(graph, screen["id"]))
        sets.append(comps)

    pairwise: list[float] = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            a, b = sets[i], sets[j]
            union = a | b
            if not union:
                continue
            inter = a & b
            pairwise.append(1.0 - (len(inter) / len(union)))

    if not pairwise:
        warnings.append("Originality: screens share identical empty component sets")
        return 0.3, warnings, passed

    avg = sum(pairwise) / len(pairwise)
    if avg < 0.15:
        warnings.append("Originality: screens use nearly identical component layouts")
    else:
        passed.append(f"Originality: layout diversity {avg:.2f} across screens")
    return round(avg, 3), warnings, passed


def score_signature_presence(root: Path, graph: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    warnings: list[str] = []
    passed: list[str] = []
    signature = _read_brief_field(root, "Signature element")
    if not signature:
        signature = _read_brief_field(root, "Project identity")
    if not signature:
        warnings.append("Originality: no signature element or project identity in AESTHETIC_BRIEF")
        return 0.4, warnings, passed

    tokens = re.findall(r"[a-z]{4,}", signature.lower())
    if not tokens:
        return 0.5, warnings, passed

    nodes, _ = index_graph(graph)
    blob = json.dumps(nodes, ensure_ascii=False).lower()
    screens_dir = root / DESIGN_SCREENS_DIR
    if screens_dir.is_dir():
        for path in screens_dir.glob("*.yaml"):
            blob += path.read_text(encoding="utf-8").lower()

    hits = sum(1 for t in tokens if t in blob)
    ratio = hits / len(tokens)
    if ratio >= 0.25:
        passed.append(f"Originality: signature/identity terms reflected in design ({hits}/{len(tokens)})")
        return min(1.0, 0.5 + ratio), warnings, passed

    warnings.append("Originality: signature element from brief not reflected in design graph/screens")
    return 0.35, warnings, passed


def score_distill_quality(root: Path) -> tuple[float, list[str], list[str]]:
    warnings: list[str] = []
    passed: list[str] = []
    text = _read_inspiration(root)
    if not text:
        warnings.append("Originality: INSPIRATION missing — run research run + distill")
        return 0.3, warnings, passed

    if _DISTILL_FAIL_MARKER in text:
        warnings.append("Originality: research distill marked FAIL")
        return 0.25, warnings, passed

    if "## Differentiation thesis" not in text:
        warnings.append("Originality: missing Differentiation thesis — run: graphcraft aesthetic research distill")
        return 0.35, warnings, passed

    if _DISTILL_MARKER in text:
        passed.append("Originality: research distill PASS marker present")

    thesis_block = text.split("## Differentiation thesis")[1].split("##")[0]
    if "TODO:" in thesis_block or thesis_block.strip().endswith(">"):
        warnings.append("Originality: differentiation thesis still placeholder")
        return 0.4, warnings, passed

    generic = detect_generic_phrases(_patterns_blob(text))
    if len(generic) >= 5:
        warnings.append(f"Originality: high generic phrase count in INSPIRATION ({len(generic)})")
        return 0.4, warnings, passed

    passed.append(f"Originality: distill thesis present; {len(generic)} generic phrase(s) flagged")
    return max(0.5, 1.0 - len(generic) * 0.08), warnings, passed


def run_originality_evaluate(root: Path, graph: dict[str, Any]) -> dict[str, Any]:
    root = root.resolve()
    config = load_config(root)
    aesthetic = aesthetic_settings(config)
    floor = float((aesthetic.get("hard_floors") or {}).get("originality_min", 0.45))
    warn_floor = float((aesthetic.get("hard_floors") or {}).get("originality_warn", 0.65))

    warnings: list[str] = []
    passed: list[str] = []
    subscores: dict[str, float] = {}

    for name, fn in (
        ("token_customization", lambda: score_token_customization(root)),
        ("layout_diversity", lambda: score_layout_diversity(graph)),
        ("reference_independence", lambda: score_reference_independence(root)),
        ("signature_presence", lambda: score_signature_presence(root, graph)),
        ("distill_quality", lambda: score_distill_quality(root)),
    ):
        score, w, p = fn()
        subscores[name] = score
        warnings.extend(w)
        passed.extend(p)

    weights = {
        "token_customization": 0.2,
        "layout_diversity": 0.2,
        "reference_independence": 0.2,
        "signature_presence": 0.2,
        "distill_quality": 0.2,
    }
    total = sum(subscores[k] * weights[k] for k in weights)
    total = round(total, 3)

    if total < floor:
        overall = "FAIL"
        warnings.append(f"FAIL Originality {total:.2f} below floor {floor}")
    elif total < warn_floor:
        overall = "WARN"
        warnings.append(f"WARN Originality {total:.2f} below recommended {warn_floor}")
    else:
        overall = "PASS"
        passed.append(f"Originality score {total:.2f} meets target")

    return {
        "overall": overall,
        "score": total,
        "floor": floor,
        "warn_floor": warn_floor,
        "subscores": subscores,
        "warnings": warnings,
        "passed": passed,
    }
