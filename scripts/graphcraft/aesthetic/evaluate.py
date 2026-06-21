"""Aesthetic rubric evaluation over design graph + config."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..constants import AESTHETIC_REPORT, DESIGN_SYSTEM_DIR
from ..design_graph.harmony import run_harmony_check
from .config_loader import (
    active_style_id,
    aesthetic_settings,
    design_settings,
    load_config,
    load_style_pack,
)
from .graph_utils import flatten_tokens, index_graph, load_tokens, screen_components
from .contrast import contrast_ratio, passes_contrast
from .originality import run_originality_evaluate


def _screen_token_ids(graph: dict[str, Any], screen_id: str) -> list[str]:
    _, edges = index_graph(graph)
    ids: list[str] = []
    for e in edges:
        if e.get("source") == screen_id and e.get("type") == "uses_token":
            target = str(e.get("target", ""))
            ids.append(target.removeprefix("token:"))
    return ids


def _screen_components(graph: dict[str, Any], screen_id: str) -> list[str]:
    return screen_components(graph, screen_id)


def _check_contrast(
    token_map: dict[str, str],
    token_ids: list[str],
    contrast_min: float,
) -> tuple[list[str], list[str], float]:
    warnings: list[str] = []
    passed: list[str] = []
    scores: list[float] = []

    text_colors = [
        token_map[t]
        for t in token_ids
        if t in token_map and t.startswith("color.text")
    ]
    bg_colors = [
        token_map[t]
        for t in token_ids
        if t in token_map and t.startswith("color.bg")
    ]
    if not text_colors:
        text_colors = [token_map[t] for t in token_map if t.startswith("color.text")]
    if not bg_colors:
        bg_colors = [token_map[t] for t in token_map if t.startswith("color.bg")]

    if not text_colors or not bg_colors:
        warnings.append("Contrast: no text/bg token pair on screen — using global tokens")
        text_colors = text_colors or [token_map.get("color.text.primary", "")]
        bg_colors = bg_colors or [token_map.get("color.bg.default", "")]

    for fg in text_colors:
        if not fg.startswith("#"):
            continue
        for bg in bg_colors:
            if not bg.startswith("#"):
                continue
            ratio = contrast_ratio(fg, bg)
            if ratio is None:
                continue
            ok = ratio >= contrast_min
            scores.append(min(ratio / contrast_min, 1.0))
            msg = f"Contrast {fg} on {bg}: {ratio:.2f} (min {contrast_min})"
            if ok:
                passed.append(msg)
            else:
                warnings.append(f"FAIL {msg}")

    if not scores:
        warnings.append("Contrast: no hex color pairs to evaluate")
        return warnings, passed, 0.0
    return warnings, passed, sum(scores) / len(scores)


def _check_style_fit(
    graph: dict[str, Any],
    style_id: str,
    style_pack: dict[str, Any],
    screen_id: str,
    component_ids: list[str],
) -> tuple[list[str], list[str], float]:
    nodes, edges = index_graph(graph)
    warnings: list[str] = []
    passed: list[str] = []
    preferred = set(style_pack.get("components", {}).get("preferred") or [])
    discouraged = set(style_pack.get("components", {}).get("discouraged") or [])

    if not component_ids:
        warnings.append(f"{screen_id}: no components to check style fit")
        return warnings, passed, 0.5

    hits = 0
    total = len(component_ids)
    for cid in component_ids:
        if cid in discouraged:
            warnings.append(f"{screen_id}: {cid} discouraged for {style_id}")
            continue
        if cid in preferred:
            hits += 1
            passed.append(f"{screen_id}: {cid} preferred for {style_id}")
            continue
        compatible = any(
            e.get("source") == cid
            and e.get("target") == style_id
            and e.get("type") == "style_compatible"
            for e in edges
        )
        if compatible:
            hits += 1
            passed.append(f"{screen_id}: {cid} style_compatible with {style_id}")
        else:
            warnings.append(f"{screen_id}: {cid} not listed for {style_id}")

    score = hits / total if total else 0.0
    return warnings, passed, score


def _check_touch_targets(
    screen: dict[str, Any],
    design_cfg: dict[str, Any],
) -> tuple[list[str], list[str], float]:
    warnings: list[str] = []
    passed: list[str] = []
    required = design_cfg.get("touch_target_min", 44)
    acceptance = screen.get("acceptance") or {}
    if not isinstance(acceptance, dict):
        acceptance = {}
    screen_min = acceptance.get("touch_target_min")
    if screen_min is None:
        warnings.append(f"{screen['id']}: touch_target_min not declared in screen acceptance")
        return warnings, passed, 0.7
    if int(screen_min) >= int(required):
        passed.append(f"{screen['id']}: touch target {screen_min}px >= {required}px")
        return warnings, passed, 1.0
    warnings.append(
        f"{screen['id']}: touch target {screen_min}px below floor {required}px"
    )
    return warnings, passed, 0.0


def _check_priority_alignment(
    screen: dict[str, Any],
    priority: str,
) -> tuple[list[str], list[str], float]:
    warnings: list[str] = []
    passed: list[str] = []
    sid = screen.get("id", "")
    label = str(screen.get("label", "")).lower()
    platform = str(screen.get("platform", "")).lower()
    form_like = any(k in sid.lower() or k in label for k in ("login", "signup", "form", "settings"))

    if priority == "marketing":
        if form_like:
            warnings.append(f"{sid}: marketing priority but screen looks utility/form-heavy")
            return warnings, passed, 0.6
        passed.append(f"{sid}: suitable for marketing-first profile")
        return warnings, passed, 1.0

    if priority == "usability":
        if not form_like and platform:
            passed.append(f"{sid}: non-form screen under usability-first (OK)")
        elif form_like:
            passed.append(f"{sid}: form/settings screen aligns with usability-first")
        return warnings, passed, 1.0

    passed.append(f"{sid}: balanced priority - no strict heuristic applied")
    return warnings, passed, 0.85


def _overall_from_scores(
    warnings: list[str],
    contrast_score: float,
    style_score: float,
    touch_score: float,
    harmony_ok: bool,
) -> str:
    if any(w.startswith("FAIL") for w in warnings):
        return "FAIL"
    if not harmony_ok:
        return "FAIL"
    avg = (contrast_score + style_score + touch_score) / 3.0
    if avg >= 0.75 and len(warnings) <= 2:
        return "PASS"
    if avg >= 0.5:
        return "WARN"
    return "FAIL"


def run_evaluate(
    root: Path,
    graph: dict[str, Any],
    *,
    screen_id: str | None = None,
    style_id: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    config = load_config(root)
    aesthetic = aesthetic_settings(config)
    design_cfg = design_settings(config)
    style = style_id or active_style_id(config)
    style_pack = load_style_pack(root, style)
    contrast_min = float((aesthetic.get("hard_floors") or {}).get("contrast_min", 4.5))
    priority = str(aesthetic.get("priority", "balanced"))

    token_map = flatten_tokens(load_tokens(root))
    nodes, _ = index_graph(graph)
    screens = [
        n
        for n in nodes.values()
        if n.get("type") == "screen" and (not screen_id or n["id"] == screen_id)
    ]
    if screen_id and not screens:
        return {
            "overall": "FAIL",
            "warnings": [f"Unknown screen: {screen_id}"],
            "passed": [],
            "scores": {},
        }

    all_warnings: list[str] = []
    all_passed: list[str] = []
    contrast_scores: list[float] = []
    style_scores: list[float] = []
    touch_scores: list[float] = []
    priority_scores: list[float] = []

    for screen in screens:
        sid = screen["id"]
        token_ids = _screen_token_ids(graph, sid)
        components = _screen_components(graph, sid)

        cw, cp, cs = _check_contrast(token_map, token_ids, contrast_min)
        all_warnings.extend(cw)
        all_passed.extend(cp)
        contrast_scores.append(cs)

        sw, sp, ss = _check_style_fit(graph, style, style_pack, sid, components)
        all_warnings.extend(sw)
        all_passed.extend(sp)
        style_scores.append(ss)

        tw, tp, ts = _check_touch_targets(screen, design_cfg)
        all_warnings.extend(tw)
        all_passed.extend(tp)
        touch_scores.append(ts)

        pw, pp, ps = _check_priority_alignment(screen, priority)
        all_warnings.extend(pw)
        all_passed.extend(pp)
        priority_scores.append(ps)

    harmony = run_harmony_check(graph, screen_id)
    if harmony["warnings"]:
        all_warnings.extend(harmony["warnings"])
    all_passed.extend(harmony["passed"])

    originality = run_originality_evaluate(root, graph)
    all_warnings.extend(originality.get("warnings") or [])
    all_passed.extend(originality.get("passed") or [])

    def _avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    scores = {
        "contrast": round(_avg(contrast_scores), 3),
        "style_fit": round(_avg(style_scores), 3),
        "touch_target": round(_avg(touch_scores), 3),
        "priority_alignment": round(_avg(priority_scores), 3),
        "harmony": 1.0 if harmony["overall"] == "PASS" else 0.0,
        "originality": originality.get("score", 0.0),
    }

    overall = _overall_from_scores(
        all_warnings,
        scores["contrast"],
        scores["style_fit"],
        scores["touch_target"],
        harmony["overall"] == "PASS",
    )
    if originality.get("overall") == "FAIL":
        overall = "FAIL"
    elif originality.get("overall") == "WARN" and overall == "PASS":
        overall = "WARN"

    return {
        "overall": overall,
        "style": style,
        "priority": priority,
        "contrast_min": contrast_min,
        "scores": scores,
        "warnings": all_warnings,
        "passed": all_passed,
        "screens_evaluated": [s["id"] for s in screens],
        "originality": originality,
    }


def format_evaluate_summary(result: dict[str, Any]) -> str:
    lines = [
        f"Aesthetic evaluate: {result.get('overall', '?')}",
        f"  style={result.get('style')} priority={result.get('priority')} "
        f"contrast_min={result.get('contrast_min')}",
    ]
    scores = result.get("scores") or {}
    lines.append(
        "  scores: "
        + ", ".join(f"{k}={v}" for k, v in scores.items())
    )
    for w in result.get("warnings") or []:
        lines.append(f"  WARN: {w}")
    for p in result.get("passed") or []:
        lines.append(f"  OK: {p}")
    return "\n".join(lines)


def write_aesthetic_report(root: Path, result: dict[str, Any]) -> Path:
    out_dir = root / "graphcraft-out"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / AESTHETIC_REPORT.name
    lines = [
        "# Aesthetic Evaluation Report",
        "",
        f"**Overall:** {result.get('overall')}",
        f"**Style:** {result.get('style')}",
        f"**Priority:** {result.get('priority')}",
        "",
        "## Scores",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
    ]
    for key, val in (result.get("scores") or {}).items():
        lines.append(f"| {key} | {val} |")
    lines.append("")
    if result.get("warnings"):
        lines.append("## Warnings")
        lines.append("")
        for w in result["warnings"]:
            lines.append(f"- {w}")
        lines.append("")
    if result.get("passed"):
        lines.append("## Passed")
        lines.append("")
        for p in result["passed"]:
            lines.append(f"- {p}")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
