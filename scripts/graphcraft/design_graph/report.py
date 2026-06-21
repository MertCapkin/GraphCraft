"""Generate DESIGN_REPORT.md from design graph."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


def write_design_report(graph: dict[str, Any], path: Path) -> None:
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    by_type = Counter(n.get("type", "?") for n in nodes)
    by_edge = Counter(e.get("type", "?") for e in edges)
    lines = [
        "# Design Graph Report",
        "",
        f"- {len(nodes)} nodes · {len(edges)} edges",
        "",
        "## Node types",
    ]
    for t, c in sorted(by_type.items()):
        lines.append(f"- {t}: {c}")
    lines.extend(["", "## Edge types"])
    for t, c in sorted(by_edge.items()):
        lines.append(f"- {t}: {c}")
    lines.extend(["", "## Screens"])
    for n in nodes:
        if n.get("type") == "screen":
            lines.append(f"- `{n.get('id')}` — {n.get('label')} ({n.get('_origin')})")
    lines.extend(["", "## Styles"])
    for n in nodes:
        if n.get("type") == "style":
            lines.append(f"- `{n.get('id')}` — {n.get('label')}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
