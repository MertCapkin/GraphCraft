"""Harmony checks on design graph."""

from __future__ import annotations

from typing import Any


def run_harmony_check(graph: dict[str, Any], screen_id: str | None = None) -> dict[str, Any]:
    nodes = {n["id"]: n for n in graph.get("nodes") or [] if "id" in n}
    edges = graph.get("edges") or []

    clashes: list[dict] = []
    warnings: list[str] = []
    passed: list[str] = []

    for e in edges:
        if e.get("type") == "clashes_with":
            clashes.append(e)

    screens = [
        n for n in nodes.values() if n.get("type") == "screen" and (not screen_id or n["id"] == screen_id)
    ]

    for screen in screens:
        sid = screen["id"]
        comp_ids = [
            e["target"]
            for e in edges
            if e.get("source") == sid and e.get("type") == "uses_component"
        ]
        for i, a in enumerate(comp_ids):
            for b in comp_ids[i + 1 :]:
                for e in edges:
                    if e.get("type") == "clashes_with" and (
                        (e.get("source") == a and e.get("target") == b)
                        or (e.get("source") == b and e.get("target") == a)
                    ):
                        warnings.append(f"CLASH on {sid}: {a} ↔ {b}")
        if not warnings:
            passed.append(f"{sid}: no component clashes detected")

    return {
        "overall": "FAIL" if warnings else "PASS",
        "clashes_in_graph": len(clashes),
        "warnings": warnings,
        "passed": passed,
    }
