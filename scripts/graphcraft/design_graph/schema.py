"""Design graph schema helpers."""

from __future__ import annotations

from typing import Any

NODE_TYPES = frozenset({"screen", "component", "token", "style", "asset", "collection"})
EDGE_TYPES = frozenset({
    "uses_component",
    "uses_token",
    "variant_of",
    "navigates_to",
    "harmonizes_with",
    "clashes_with",
    "style_compatible",
    "implements",
    "uses_asset",
    "alternative",
})
ORIGINS = frozenset({"designed", "extracted", "bridge", "inferred", "stitch"})


def make_node(
    node_id: str,
    *,
    ntype: str,
    label: str,
    source: str = "",
    origin: str = "designed",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    node: dict[str, Any] = {
        "id": node_id,
        "type": ntype,
        "label": label,
        "source": source,
        "_origin": origin,
    }
    if extra:
        node.update(extra)
    return node


def make_edge(
    source: str,
    target: str,
    etype: str,
    *,
    origin: str = "designed",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    edge: dict[str, Any] = {
        "source": source,
        "target": target,
        "type": etype,
        "_origin": origin,
    }
    if extra:
        edge.update(extra)
    return edge


def empty_graph() -> dict[str, Any]:
    return {
        "directed": True,
        "graph": {"layer": "design", "version": "1.0", "generator": "graphcraft"},
        "nodes": [],
        "edges": [],
    }
