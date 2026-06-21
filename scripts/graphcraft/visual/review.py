"""Visual review against Stitch PNG ground truth."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..aesthetic.config_loader import design_settings, load_config
from ..constants import DESIGN_GRAPH_JSON, STITCH_DIR, VISUAL_REVIEW_REPORT
from ..design_graph.harmony import run_harmony_check
from ..design_graph.query import load_graph
from .png_utils import pixel_similarity, png_dimensions


def _screens_with_references(graph: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for node in graph.get("nodes") or []:
        if node.get("type") != "screen":
            continue
        ref = node.get("reference_png")
        if ref:
            out.append(node)
    return out


def _resolve_candidate(candidates_dir: Path, screen_id: str, label: str) -> Path | None:
    slug = screen_id.split(":", 1)[-1]
    names = [
        f"{slug}.png",
        f"{label.lower().replace(' ', '-')}.png",
        f"{slug.replace('-', '_')}.png",
    ]
    for name in names:
        path = candidates_dir / name
        if path.is_file():
            return path
    return None


def run_visual_review(
    root: Path,
    *,
    screen_id: str | None = None,
    candidates_dir: Path | None = None,
    threshold: float = 0.85,
) -> dict[str, Any]:
    root = root.resolve()
    graph_path = root / DESIGN_GRAPH_JSON
    if not graph_path.is_file():
        return {
            "overall": "FAIL",
            "screens": [],
            "warnings": [f"Missing {DESIGN_GRAPH_JSON} — run: graphcraft design update ."],
        }

    graph = load_graph(graph_path)
    config = load_config(root)
    design_cfg = design_settings(config)
    touch_min = design_cfg.get("touch_target_min", 44)

    cand_dir = candidates_dir or (root / "screenshots")
    screens = _screens_with_references(graph)
    if screen_id:
        screens = [s for s in screens if s["id"] == screen_id]
        if not screens:
            return {
                "overall": "FAIL",
                "screens": [],
                "warnings": [f"No screen with reference_png: {screen_id}"],
            }

    if not screens:
        stitch_designs = root / STITCH_DIR / "designs"
        if stitch_designs.is_dir():
            return {
                "overall": "WARN",
                "screens": [],
                "warnings": [
                    f"No reference_png on design graph nodes — run: graphcraft stitch import . "
                    f"({len(list(stitch_designs.glob('*.png')))} PNG in .stitch/designs/)"
                ],
            }
        return {
            "overall": "WARN",
            "screens": [],
            "warnings": ["No Stitch references found for visual review"],
        }

    harmony = run_harmony_check(graph, screen_id)
    results: list[dict[str, Any]] = []
    warnings: list[str] = list(harmony.get("warnings") or [])
    passed: list[str] = list(harmony.get("passed") or [])

    for screen in screens:
        sid = screen["id"]
        ref_path = Path(screen["reference_png"])
        if not ref_path.is_file():
            ref_path = root / ref_path
        entry: dict[str, Any] = {
            "screen": sid,
            "reference": str(ref_path),
            "overall": "FAIL",
        }

        if not ref_path.is_file():
            entry["error"] = "Reference PNG missing"
            warnings.append(f"{sid}: reference PNG missing")
            results.append(entry)
            continue

        ref_dims = png_dimensions(ref_path)
        entry["reference_dims"] = ref_dims

        candidate = _resolve_candidate(cand_dir, sid, str(screen.get("label", sid)))
        if candidate is None:
            entry["overall"] = "WARN"
            entry["error"] = f"No candidate in {cand_dir} (expected {sid.split(':')[-1]}.png)"
            warnings.append(entry["error"])
            results.append(entry)
            continue

        diff = pixel_similarity(ref_path, candidate)
        entry["candidate"] = str(candidate)
        entry["similarity"] = diff.get("similarity")
        entry["diff_method"] = diff.get("method")
        entry["overall"] = diff.get("overall", "WARN")

        if entry["overall"] == "PASS":
            passed.append(f"{sid}: visual match {entry['similarity']}")
        elif entry.get("similarity") is not None and entry["similarity"] < threshold:
            warnings.append(f"{sid}: similarity {entry['similarity']} below {threshold}")

        acceptance = screen.get("acceptance") or {}
        if isinstance(acceptance, dict):
            tmin = acceptance.get("touch_target_min")
            if tmin is not None and int(tmin) < int(touch_min):
                warnings.append(f"{sid}: touch target {tmin}px below {touch_min}px")
                entry["overall"] = "FAIL"

        results.append(entry)

    overall = "PASS"
    if any(r.get("overall") == "FAIL" for r in results):
        overall = "FAIL"
    elif warnings or any(r.get("overall") == "WARN" for r in results):
        overall = "WARN"
    if harmony.get("overall") == "FAIL":
        overall = "FAIL"

    return {
        "overall": overall,
        "threshold": threshold,
        "candidates_dir": str(cand_dir),
        "screens": results,
        "warnings": warnings,
        "passed": passed,
        "harmony": harmony.get("overall"),
    }


def format_visual_summary(result: dict[str, Any]) -> str:
    lines = [
        f"Visual review: {result.get('overall')}",
        f"  candidates={result.get('candidates_dir')} threshold={result.get('threshold')}",
    ]
    for row in result.get("screens") or []:
        sim = row.get("similarity")
        sim_txt = f" similarity={sim}" if sim is not None else ""
        lines.append(f"  {row['screen']}: {row.get('overall')}{sim_txt}")
    for w in result.get("warnings") or []:
        lines.append(f"  WARN: {w}")
    for p in result.get("passed") or []:
        lines.append(f"  OK: {p}")
    return "\n".join(lines)


def write_visual_report(root: Path, result: dict[str, Any]) -> Path:
    out_dir = root / "graphcraft-out"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / VISUAL_REVIEW_REPORT.name
    lines = [
        "# Visual Review Report",
        "",
        f"**Overall:** {result.get('overall')}",
        f"**Harmony:** {result.get('harmony')}",
        "",
        "## Screens",
        "",
        "| Screen | Result | Similarity | Reference | Candidate |",
        "|--------|--------|------------|-----------|-----------|",
    ]
    for row in result.get("screens") or []:
        lines.append(
            f"| {row.get('screen')} | {row.get('overall')} | {row.get('similarity', '-')} "
            f"| `{row.get('reference', '-')}` | `{row.get('candidate', '-')}` |"
        )
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


def run_diff(reference: Path, candidate: Path) -> dict[str, Any]:
    return pixel_similarity(reference.resolve(), candidate.resolve())
