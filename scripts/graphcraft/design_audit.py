"""Design audit — mechanical design graph + aesthetic + UI checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .aesthetic.config_loader import load_config
from .aesthetic.evaluate import run_evaluate
from .constants import DESIGN_GRAPH_JSON
from .design_graph.harmony import run_harmony_check
from .design_graph.query import load_graph, validate as validate_design_graph
from .ui.validate import validate_stack


def run_design_audit(root: Path) -> dict[str, Any]:
    root = root.resolve()
    results: dict[str, Any] = {
        "overall": "PASS",
        "checks": {},
        "issues": [],
    }

    graph_path = root / DESIGN_GRAPH_JSON
    if not graph_path.is_file():
        results["overall"] = "FAIL"
        results["issues"].append(f"Missing {DESIGN_GRAPH_JSON} — run: graphcraft design update .")
        return results

    graph = load_graph(graph_path)
    dg_issues = validate_design_graph(graph)
    results["checks"]["design_validate"] = "PASS" if not dg_issues else "FAIL"
    if dg_issues:
        results["issues"].extend(dg_issues)

    harmony = run_harmony_check(graph)
    results["checks"]["design_harmony"] = harmony["overall"]
    if harmony["overall"] != "PASS":
        results["issues"].extend(harmony.get("warnings") or [])

    aesthetic = run_evaluate(root, graph)
    results["checks"]["aesthetic_evaluate"] = aesthetic["overall"]
    if aesthetic["overall"] == "FAIL":
        results["issues"].extend(aesthetic.get("warnings") or [])

    config = load_config(root)
    stack = str(config.get("active_stack", "react-native"))
    stack_map = {
        "react-native": "rn",
        "expo": "rn",
        "flutter": "flutter",
        "unity-ugui": "unity",
        "unity-ui-toolkit": "unity",
        "godot": "godot",
    }
    ui_stack = stack_map.get(stack, "rn")
    ui_issues = validate_stack(root, ui_stack)
    results["checks"][f"ui_validate_{ui_stack}"] = "PASS" if not ui_issues else "FAIL"
    if ui_issues:
        results["issues"].extend(ui_issues)

    if results["issues"] or any(
        v == "FAIL" for v in results["checks"].values()
    ):
        if any(v == "FAIL" for v in results["checks"].values()):
            results["overall"] = "FAIL"
        else:
            results["overall"] = "WARN"

    return results
