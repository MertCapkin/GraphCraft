"""Design graph queries — keyword, path, explain, radius."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any


def load_graph(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _index(graph: dict[str, Any]) -> tuple[dict[str, dict], list[dict]]:
    nodes = {n["id"]: n for n in graph.get("nodes") or [] if "id" in n}
    return nodes, list(graph.get("edges") or [])


def _resolve_node_id(nodes: dict[str, dict], ref: str) -> str | None:
    if ref in nodes:
        return ref
    ref_lower = ref.lower()
    for nid, node in nodes.items():
        if nid.lower() == ref_lower:
            return nid
        if node.get("label", "").lower() == ref_lower:
            return nid
    if not ref.startswith(("screen:", "component:", "token:", "style:")):
        for prefix in ("screen:", "component:", "token:", "style:"):
            candidate = f"{prefix}{ref}"
            if candidate in nodes:
                return candidate
            for nid in nodes:
                if nid.lower() == candidate.lower():
                    return nid
    return None


def _adjacency(edges: list[dict], *, directed: bool = False) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {}
    for e in edges:
        src, tgt = e.get("source"), e.get("target")
        if not src or not tgt:
            continue
        adj.setdefault(str(src), set()).add(str(tgt))
        if not directed:
            adj.setdefault(str(tgt), set()).add(str(src))
    return adj


def find_path(graph: dict[str, Any], start: str, end: str) -> str:
    nodes, edges = _index(graph)
    start_id = _resolve_node_id(nodes, start)
    end_id = _resolve_node_id(nodes, end)
    if not start_id:
        return f"Unknown node: {start}"
    if not end_id:
        return f"Unknown node: {end}"
    if start_id == end_id:
        return f"Path: {start_id} (same node)"

    adj = _adjacency(edges, directed=False)
    queue: deque[str] = deque([start_id])
    prev: dict[str, str | None] = {start_id: None}

    while queue:
        current = queue.popleft()
        if current == end_id:
            break
        for nxt in adj.get(current, ()):
            if nxt in prev:
                continue
            prev[nxt] = current
            queue.append(nxt)

    if end_id not in prev:
        return f"No path between {start_id} and {end_id}"

    path: list[str] = []
    cur: str | None = end_id
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    edge_by_pair: dict[tuple[str, str], str] = {}
    for e in edges:
        s, t = str(e.get("source")), str(e.get("target"))
        etype = e.get("type", "?")
        edge_by_pair[(s, t)] = etype
        edge_by_pair[(t, s)] = etype

    lines = [f"Path ({len(path) - 1} hop(s)):"]
    for i, node_id in enumerate(path):
        label = nodes.get(node_id, {}).get("label", node_id)
        lines.append(f"  {i + 1}. {node_id} ({label})")
        if i + 1 < len(path):
            a, b = path[i], path[i + 1]
            etype = edge_by_pair.get((a, b), "?")
            lines.append(f"     --[{etype}]-->")
    return "\n".join(lines)


def explain_node(graph: dict[str, Any], node_ref: str) -> str:
    nodes, edges = _index(graph)
    node_id = _resolve_node_id(nodes, node_ref)
    if not node_id:
        return f"Unknown node: {node_ref}"

    node = nodes[node_id]
    lines = [
        f"Node: {node_id}",
        f"  type: {node.get('type')}",
        f"  label: {node.get('label')}",
        f"  origin: {node.get('_origin')}",
    ]
    if node.get("source"):
        lines.append(f"  source: {node['source']}")
    for key in ("platform", "status", "collection", "mood", "value", "token_type"):
        if key in node:
            lines.append(f"  {key}: {node[key]}")

    outgoing: dict[str, list[str]] = {}
    incoming: dict[str, list[str]] = {}
    for e in edges:
        etype = str(e.get("type", "?"))
        if e.get("source") == node_id:
            outgoing.setdefault(etype, []).append(str(e.get("target")))
        if e.get("target") == node_id:
            incoming.setdefault(etype, []).append(str(e.get("source")))

    lines.append("")
    lines.append("Outgoing:")
    if outgoing:
        for etype, targets in sorted(outgoing.items()):
            lines.append(f"  {etype}: {', '.join(targets)}")
    else:
        lines.append("  (none)")

    lines.append("Incoming:")
    if incoming:
        for etype, sources in sorted(incoming.items()):
            lines.append(f"  {etype}: {', '.join(sources)}")
    else:
        lines.append("  (none)")

    return "\n".join(lines)


def blast_radius(graph: dict[str, Any], node_ref: str, depth: int = 2) -> str:
    nodes, edges = _index(graph)
    node_id = _resolve_node_id(nodes, node_ref)
    if not node_id:
        return f"Unknown node: {node_ref}"

    adj = _adjacency(edges, directed=False)
    seen: dict[str, int] = {node_id: 0}
    queue: deque[str] = deque([node_id])

    while queue:
        current = queue.popleft()
        d = seen[current]
        if d >= depth:
            continue
        for nxt in adj.get(current, ()):
            if nxt not in seen:
                seen[nxt] = d + 1
                queue.append(nxt)

    by_depth: dict[int, list[str]] = {}
    for nid, d in seen.items():
        by_depth.setdefault(d, []).append(nid)

    lines = [f"Radius from {node_id} (depth={depth}): {len(seen) - 1} reachable node(s)"]
    for d in sorted(by_depth):
        if d == 0:
            continue
        ids = sorted(by_depth[d])
        typed = [f"{nid} ({nodes.get(nid, {}).get('type', '?')})" for nid in ids]
        lines.append(f"  depth {d}: {', '.join(typed)}")
    return "\n".join(lines)


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
            impl = [
                e["target"]
                for e in edges
                if e.get("source") == s["id"] and e.get("type") == "implements"
            ]
            suffix = ""
            if impl:
                suffix = f" implements: {', '.join(impl)}"
            lines.append(
                f"  {s['id']}: {s.get('label')} → components: {', '.join(comps) or 'none'}{suffix}"
            )
        return "\n".join(lines)

    if "component" in q:
        comps = [n for n in nodes.values() if n.get("type") == "component"]
        lines = [f"Components ({len(comps)}):"]
        for c in comps:
            toks = [
                e["target"]
                for e in edges
                if e.get("source") == c["id"] and e.get("type") == "uses_token"
            ]
            lines.append(f"  {c['id']}: {c.get('label')} tokens: {', '.join(toks) or 'none'}")
        return "\n".join(lines)

    if "navigation" in q or "navigates" in q:
        nav = [e for e in edges if e.get("type") == "navigates_to"]
        lines = [f"Navigation edges ({len(nav)}):"]
        for e in nav:
            lines.append(f"  {e['source']} --navigates_to--> {e['target']}")
        return "\n".join(lines) if nav else "Navigation edges: none"

    if "implement" in q:
        impl = [e for e in edges if e.get("type") == "implements"]
        lines = [f"Implements edges ({len(impl)}):"]
        for e in impl:
            lines.append(f"  {e['source']} -> {e['target']}")
        return "\n".join(lines) if impl else "Implements edges: none (run: graphcraft design bridge)"

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
        "Try: 'screens', 'components', 'tokens', 'styles', 'navigation', 'implements', 'harmony'"
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
