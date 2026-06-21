"""Shared graph/token helpers for aesthetic evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..constants import DESIGN_SYSTEM_DIR


def index_graph(graph: dict[str, Any]) -> tuple[dict[str, dict], list[dict]]:
    nodes = {n["id"]: n for n in graph.get("nodes") or [] if "id" in n}
    return nodes, list(graph.get("edges") or [])


def load_tokens(root: Path) -> dict[str, Any]:
    for name in ("tokens.json", "tokens.base.json"):
        path = root / DESIGN_SYSTEM_DIR / name
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    return {}


def flatten_tokens(obj: Any, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if not isinstance(obj, dict):
        return out
    if "$value" in obj or "value" in obj:
        val = obj.get("$value") or obj.get("value")
        if isinstance(val, str) and val.startswith("#"):
            out[prefix] = val
        return out
    for key, child in obj.items():
        if key.startswith("$"):
            continue
        child_prefix = f"{prefix}.{key}" if prefix else key
        out.update(flatten_tokens(child, child_prefix))
    return out


def screen_components(graph: dict[str, Any], screen_id: str) -> list[str]:
    _, edges = index_graph(graph)
    return [
        str(e["target"])
        for e in edges
        if e.get("source") == screen_id and e.get("type") == "uses_component"
    ]
