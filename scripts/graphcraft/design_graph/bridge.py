"""Design ↔ code bridge — map screens/components to source files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from ..constants import BRIDGE_JSON, DESIGN_GRAPH_JSON, DESIGN_SCREENS_DIR

_CODE_SCAN_EXTENSIONS = frozenset(
    {".ts", ".tsx", ".js", ".jsx", ".dart", ".cs", ".gd", ".swift", ".kt", ".vue"}
)
_IMPLEMENTS_COMMENT = re.compile(
    r"(?:@graphcraft\s+implements?:?\s*|#\s*graphcraft-implements:\s*)"
    r"(?P<id>(?:screen|component):[\w.-]+)",
    re.IGNORECASE,
)


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _slug_from_design_id(design_id: str) -> str:
    return design_id.split(":", 1)[-1].replace("-", "").replace("_", "").lower()


def _file_matches_slug(path: Path, slug: str) -> bool:
    stem = path.stem.lower().replace("-", "").replace("_", "")
    return slug in stem or stem in slug


def _scan_declared_yaml(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    screens_dir = root / DESIGN_SCREENS_DIR
    if not screens_dir.is_dir():
        return rows
    for path in sorted(screens_dir.glob("*.yaml")):
        data = _load_yaml(path)
        sid = str(data.get("id") or f"screen:{path.stem}")
        impl = data.get("implements")
        if not impl:
            continue
        rows.append(
            {
                "design": sid,
                "code": str(impl),
                "type": "implements",
                "confidence": "declared",
                "origin": "yaml",
                "source": str(path),
            }
        )
    return rows


def _scan_code_comments(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    skip = {"node_modules", ".git", "graphcraft-out", "graphify-out", ".venv", "venv", "__pycache__"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in _CODE_SCAN_EXTENSIONS:
            continue
        if any(part in skip for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in _IMPLEMENTS_COMMENT.finditer(text):
            rel = path.relative_to(root).as_posix()
            rows.append(
                {
                    "design": match.group("id"),
                    "code": rel,
                    "type": "implements",
                    "confidence": "comment",
                    "origin": "scan",
                    "source": rel,
                }
            )
    return rows


def _scan_heuristic(root: Path, known_design_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    skip = {"node_modules", ".git", "graphcraft-out", "graphify-out", ".venv", "venv", "__pycache__", "scripts"}
    covered: set[tuple[str, str]] = set()
    for design_id in sorted(known_design_ids):
        if not design_id.startswith("screen:"):
            continue
        slug = _slug_from_design_id(design_id)
        if len(slug) < 3:
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _CODE_SCAN_EXTENSIONS:
                continue
            if any(part in skip for part in path.parts):
                continue
            if not _file_matches_slug(path, slug):
                continue
            rel = path.relative_to(root).as_posix()
            key = (design_id, rel)
            if key in covered:
                continue
            covered.add(key)
            rows.append(
                {
                    "design": design_id,
                    "code": rel,
                    "type": "implements",
                    "confidence": "heuristic",
                    "origin": "scan",
                    "source": rel,
                }
            )
    return rows


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = {"declared": 0, "comment": 1, "heuristic": 2}
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["design"], row["code"])
        existing = best.get(key)
        if existing is None or priority.get(row["confidence"], 9) < priority.get(
            existing["confidence"], 9
        ):
            best[key] = row
    return sorted(best.values(), key=lambda r: (r["design"], r["code"]))


def _find_gaps(design_graph: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    screens = [
        n["id"]
        for n in design_graph.get("nodes") or []
        if n.get("type") == "screen" and n.get("_origin") != "inferred"
    ]
    mapped = {r["design"] for r in rows if r["type"] == "implements"}
    gaps: list[dict[str, Any]] = []
    for sid in screens:
        if sid not in mapped:
            gaps.append({"design": sid, "reason": "no implementation mapping"})
    return gaps


def build_bridge(root: Path, *, heuristic: bool = True) -> dict[str, Any]:
    root = root.resolve()
    design_path = root / DESIGN_GRAPH_JSON
    if design_path.is_file():
        design_graph = json.loads(design_path.read_text(encoding="utf-8"))
    else:
        from .builder import build_design_graph

        design_graph = build_design_graph(root)

    rows: list[dict[str, Any]] = []
    rows.extend(_scan_declared_yaml(root))
    rows.extend(_scan_code_comments(root))

    if heuristic:
        screen_ids = {
            n["id"]
            for n in design_graph.get("nodes") or []
            if n.get("type") == "screen"
        }
        rows.extend(_scan_heuristic(root, screen_ids))

    rows = _dedupe_rows(rows)
    gaps = _find_gaps(design_graph, rows)

    bridge: dict[str, Any] = {
        "version": "1.0",
        "generator": "graphcraft",
        "design_graph": str(DESIGN_GRAPH_JSON),
        "code_graph": "graphify-out/graph.json",
        "mappings": rows,
        "gaps": gaps,
        "stats": {
            "mappings": len(rows),
            "gaps": len(gaps),
            "declared": sum(1 for r in rows if r["confidence"] == "declared"),
            "comment": sum(1 for r in rows if r["confidence"] == "comment"),
            "heuristic": sum(1 for r in rows if r["confidence"] == "heuristic"),
        },
    }
    return bridge


def write_bridge(root: Path, bridge: dict[str, Any]) -> Path:
    out_dir = root / "graphcraft-out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / BRIDGE_JSON.name
    out_path.write_text(json.dumps(bridge, indent=2), encoding="utf-8")
    return out_path


def format_bridge_summary(bridge: dict[str, Any]) -> str:
    stats = bridge.get("stats") or {}
    lines = [
        f"Bridge: {stats.get('mappings', 0)} mapping(s), {stats.get('gaps', 0)} gap(s)",
        f"  declared={stats.get('declared', 0)} comment={stats.get('comment', 0)} "
        f"heuristic={stats.get('heuristic', 0)}",
    ]
    for row in bridge.get("mappings") or []:
        lines.append(
            f"  {row['design']} -> {row['code']} ({row['confidence']})"
        )
    for gap in bridge.get("gaps") or []:
        lines.append(f"  GAP: {gap['design']} — {gap['reason']}")
    return "\n".join(lines)


def format_bridge_report(bridge: dict[str, Any]) -> str:
    lines = ["# Design ↔ Code Bridge", ""]
    stats = bridge.get("stats") or {}
    lines.append(f"- Mappings: **{stats.get('mappings', 0)}**")
    lines.append(f"- Gaps: **{stats.get('gaps', 0)}**")
    lines.append("")
    if bridge.get("mappings"):
        lines.append("## Mappings")
        lines.append("")
        lines.append("| Design | Code | Confidence |")
        lines.append("|--------|------|------------|")
        for row in bridge["mappings"]:
            lines.append(f"| {row['design']} | `{row['code']}` | {row['confidence']} |")
        lines.append("")
    if bridge.get("gaps"):
        lines.append("## Gaps")
        lines.append("")
        for gap in bridge["gaps"]:
            lines.append(f"- `{gap['design']}` — {gap['reason']}")
    return "\n".join(lines)


def load_bridge(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def unified_query(
    design_graph: dict[str, Any],
    bridge: dict[str, Any] | None,
    question: str,
) -> str:
    from .query import query as design_query

    parts = [design_query(design_graph, question)]
    if bridge is None:
        parts.append("Bridge: not built — run: graphcraft design bridge")
        return "\n\n".join(parts)

    q = question.lower()
    mappings = bridge.get("mappings") or []
    hits = [
        r
        for r in mappings
        if q in r["design"].lower() or q in r["code"].lower()
    ]
    if hits:
        parts.append("Bridge matches:")
        for row in hits:
            parts.append(f"  {row['design']} -> {row['code']} ({row['confidence']})")
    else:
        parts.append("Bridge: no mappings match this question.")
    return "\n".join(parts)
