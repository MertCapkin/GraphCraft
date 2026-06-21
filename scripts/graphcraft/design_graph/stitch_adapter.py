"""Ingest .stitch/ directory into design graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import make_edge, make_node


def ingest_stitch(stitch_dir: Path, graph: dict[str, Any]) -> None:
    meta_path = stitch_dir / "metadata.json"
    if not meta_path.is_file():
        return

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    project_id = meta.get("project_id", "unknown")
    graph["graph"]["stitch_project"] = project_id

    screens = meta.get("screens") or {}
    if isinstance(screens, dict):
        items = screens.items()
    elif isinstance(screens, list):
        items = ((s.get("id", f"screen-{i}"), s) for i, s in enumerate(screens))
    else:
        items = []

    for key, spec in items:
        if isinstance(spec, str):
            sid = f"screen:{key}"
            label = key
            png = stitch_dir / "designs" / f"{key}.png"
        elif isinstance(spec, dict):
            sid = spec.get("id") or f"screen:{key}"
            label = spec.get("title") or key
            png = stitch_dir / "designs" / spec.get("png", f"{key}.png")
        else:
            continue

        graph["nodes"].append(
            make_node(
                sid,
                ntype="screen",
                label=label,
                source=str(meta_path),
                origin="stitch",
                extra={
                    "reference_png": str(png) if png.is_file() else None,
                    "status": spec.get("status", "imported") if isinstance(spec, dict) else "imported",
                },
            )
        )

    flows = meta.get("flows") or meta.get("navigation") or []
    if isinstance(flows, list):
        for flow in flows:
            if not isinstance(flow, dict):
                continue
            src = flow.get("from")
            dst = flow.get("to")
            if src and dst:
                s_id = src if str(src).startswith("screen:") else f"screen:{src}"
                d_id = dst if str(dst).startswith("screen:") else f"screen:{dst}"
                graph["edges"].append(
                    make_edge(s_id, d_id, "navigates_to", origin="stitch")
                )

    design_md = stitch_dir / "DESIGN.md"
    if design_md.is_file():
        graph["nodes"].append(
            make_node(
                "style:stitch-imported",
                ntype="style",
                label="Stitch imported theme",
                source=str(design_md),
                origin="stitch",
            )
        )
