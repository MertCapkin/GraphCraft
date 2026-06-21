"""Build design-graph.json from declarative design sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from ..constants import (
    DESIGN_COMPONENTS_DIR,
    DESIGN_SCREENS_DIR,
    DESIGN_SYSTEM_DIR,
    STITCH_DIR,
    STYLES_DIR,
)
from .schema import empty_graph, make_edge, make_node
from .stitch_adapter import ingest_stitch
from .report import write_design_report


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _parse_tokens(tokens_path: Path, graph: dict[str, Any]) -> None:
    if not tokens_path.is_file():
        return
    data = json.loads(tokens_path.read_text(encoding="utf-8"))

    def walk(obj: Any, prefix: str = "") -> None:
        if not isinstance(obj, dict):
            return
        if "$value" in obj or "value" in obj:
            tid = f"token:{prefix}"
            val = obj.get("$value") or obj.get("value")
            graph["nodes"].append(
                make_node(
                    tid,
                    ntype="token",
                    label=prefix,
                    source=str(tokens_path),
                    origin="extracted",
                    extra={"value": val, "token_type": obj.get("$type", "unknown")},
                )
            )
            return
        for key, child in obj.items():
            if key.startswith("$"):
                continue
            child_prefix = f"{prefix}.{key}" if prefix else key
            walk(child, child_prefix)

    walk(data)


def _parse_component(path: Path, graph: dict[str, Any]) -> None:
    data = _load_yaml(path)
    cid = data.get("id") or f"component:{path.stem}"
    graph["nodes"].append(
        make_node(
            str(cid),
            ntype="component",
            label=data.get("label", path.stem),
            source=str(path),
            origin="designed",
            extra={
                "collection": data.get("collection"),
                "when_to_use": data.get("when_to_use"),
                "when_not_to_use": data.get("when_not_to_use"),
            },
        )
    )
    for tok in data.get("uses_tokens") or []:
        tid = tok if str(tok).startswith("token:") else f"token:{tok}"
        graph["edges"].append(make_edge(str(cid), tid, "uses_token"))
    for alt in data.get("alternatives") or []:
        graph["edges"].append(make_edge(str(cid), str(alt), "alternative"))
    for style in data.get("style_compatibility") or []:
        sid = style if str(style).startswith("style:") else f"style:{style}"
        graph["edges"].append(make_edge(str(cid), sid, "style_compatible"))
    for other, score in (data.get("harmony_score_with") or {}).items():
        etype = "harmonizes_with" if float(score) >= 0.5 else "clashes_with"
        graph["edges"].append(
            make_edge(str(cid), str(other), etype, extra={"score": float(score)})
        )


def _parse_screen(path: Path, graph: dict[str, Any]) -> None:
    data = _load_yaml(path)
    sid = data.get("id") or f"screen:{path.stem}"
    graph["nodes"].append(
        make_node(
            str(sid),
            ntype="screen",
            label=data.get("title", path.stem),
            source=str(path),
            origin="designed",
            extra={"platform": data.get("platform"), "status": data.get("status", "draft")},
        )
    )
    for comp in data.get("components") or []:
        cid = comp if str(comp).startswith("component:") else f"component:{comp}"
        graph["edges"].append(make_edge(str(sid), cid, "uses_component"))
    for tok in data.get("tokens") or []:
        tid = tok if str(tok).startswith("token:") else f"token:{tok}"
        graph["edges"].append(make_edge(str(sid), tid, "uses_token"))
    nav = data.get("navigation") or {}
    if isinstance(nav, dict):
        for _action, target in nav.items():
            tid = target if str(target).startswith("screen:") else f"screen:{target}"
            graph["edges"].append(make_edge(str(sid), tid, "navigates_to"))
    impl = data.get("implements")
    if impl:
        graph["edges"].append(
            make_edge(str(sid), str(impl), "implements", origin="bridge")
        )


def _parse_style(path: Path, graph: dict[str, Any]) -> None:
    data = _load_yaml(path)
    sid = data.get("id") or f"style:{path.parent.name}"
    graph["nodes"].append(
        make_node(
            str(sid),
            ntype="style",
            label=data.get("label", path.parent.name),
            source=str(path),
            origin="designed",
            extra={"mood": data.get("mood"), "priority": data.get("priority")},
        )
    )
    for comp in data.get("components", {}).get("preferred") or []:
        graph["edges"].append(make_edge(str(sid), str(comp), "style_compatible"))
    asset_set = data.get("assets", {}).get("icon_set")
    if asset_set:
        aid = asset_set if str(asset_set).startswith("assets:") else f"assets:{asset_set}"
        graph["edges"].append(make_edge(str(sid), aid, "uses_asset"))


def build_design_graph(root: Path) -> dict[str, Any]:
    graph = empty_graph()
    tokens = root / DESIGN_SYSTEM_DIR / "tokens.json"
    if not tokens.is_file():
        tokens = root / DESIGN_SYSTEM_DIR / "tokens.base.json"
    _parse_tokens(tokens, graph)

    components_dir = root / DESIGN_COMPONENTS_DIR
    if components_dir.is_dir():
        for path in sorted(components_dir.glob("*.yaml")):
            _parse_component(path, graph)

    screens_dir = root / DESIGN_SCREENS_DIR
    if screens_dir.is_dir():
        for path in sorted(screens_dir.glob("*.yaml")):
            _parse_screen(path, graph)

    styles_dir = root / STYLES_DIR
    if styles_dir.is_dir():
        for style_file in sorted(styles_dir.glob("*/style.yaml")):
            _parse_style(style_file, graph)

    stitch_dir = root / STITCH_DIR
    if stitch_dir.is_dir():
        ingest_stitch(stitch_dir, graph)

    _materialize_missing_targets(graph)
    return graph


def _materialize_missing_targets(graph: dict[str, Any]) -> None:
    """Create placeholder nodes for referenced IDs not explicitly defined."""
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    known = {n["id"] for n in nodes if "id" in n}
    prefix_type = {
        "screen:": "screen",
        "component:": "component",
        "token:": "token",
        "style:": "style",
        "assets:": "asset",
    }
    for e in edges:
        for end in (e.get("source"), e.get("target")):
            if not end or end in known:
                continue
            ntype = "component"
            for prefix, t in prefix_type.items():
                if str(end).startswith(prefix):
                    ntype = t
                    break
            graph["nodes"].append(
                make_node(
                    str(end),
                    ntype=ntype,
                    label=str(end).split(":", 1)[-1],
                    source="",
                    origin="inferred",
                )
            )
            known.add(str(end))


def update_design_graph(root: Path) -> dict[str, Any]:
    graph = build_design_graph(root)
    out_dir = root / "graphcraft-out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "design-graph.json"
    out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    write_design_report(graph, out_dir / "DESIGN_REPORT.md")
    return graph
