"""Simple design graph queries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_graph(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _index(graph: dict[str, Any]) -> tuple[dict[str, dict], list[dict]]:
    nodes = {n["id"]: n for n in graph.get("nodes") or [] if "id" in n}
    return nodes, list(graph.get("edges") or [])


def query(graph: dict[str, Any], question: str) -> str:
    q = question.lower()
    nodes, edges = _index(graph)

    if "screen" in q:
        screens = [n for n in nodes.values() if n.get("type") == "screen"]
        lines = [f"Screens ({len(screens)}):"]
        for s in screens:
            comps = [
                e["target"]
                for e in edges
                if e.get("source") == s["id"] and e.get("type") == "uses_component"
            ]
            lines.append(f"  {s['id']}: {s.get('label')} → components: {', '.join(comps) or 'none'}")
        return "\n".join(lines)

    if "token" in q:
        tokens = [n for n in nodes.values() if n.get("type") == "token"]
        return f"Tokens: {len(tokens)} defined. Sample: " + ", ".join(
            t["id"] for t in tokens[:8]
        )

    if "style" in q:
        styles = [n["id"] for n in nodes.values() if n.get("type") == "style"]
        return "Styles: " + (", ".join(styles) or "none")

    if "harmony" in q or "clash" in q:
        clashes = [e for e in edges if e.get("type") == "clashes_with"]
        harmonizes = [e for e in edges if e.get("type") == "harmonizes_with"]
        return (
            f"Harmony edges: {len(harmonizes)} harmonizes_with, "
            f"{len(clashes)} clashes_with"
        )

    return (
        f"Design graph: {len(nodes)} nodes, {len(edges)} edges. "
        "Try: 'screens', 'tokens', 'styles', 'harmony'"
    )


def validate(graph: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    nodes, edges = _index(graph)
    node_ids = set(nodes)

    for e in edges:
        if e.get("source") not in node_ids:
            issues.append(f"Edge source missing node: {e.get('source')}")
        if e.get("target") not in node_ids:
            issues.append(f"Edge target missing node: {e.get('target')}")

    for n in nodes.values():
        if n.get("type") == "screen":
            sid = n["id"]
            if n.get("_origin") == "inferred":
                continue
            has_comp = any(
                e.get("source") == sid and e.get("type") == "uses_component" for e in edges
            )
            if not has_comp and n.get("_origin") != "stitch":
                issues.append(f"Screen {sid} has no uses_component edges")

    return issues
