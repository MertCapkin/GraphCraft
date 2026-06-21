"""Stitch MCP configuration helper for @keeponfirst/kof-stitch-mcp."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from ..constants import CONFIG_FILE

MCP_SERVER_KEY = "stitch"
MCP_PACKAGE = "@keeponfirst/kof-stitch-mcp"


def _load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_FILE
    if not path.is_file() or yaml is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def project_id_from_config(root: Path) -> str:
    config = _load_config(root)
    stitch = config.get("stitch") or {}
    pid = stitch.get("project_id") or stitch.get("google_cloud_project") or ""
    return str(pid).strip()


def build_mcp_entry(project_id: str) -> dict[str, Any]:
    env: dict[str, str] = {}
    if project_id:
        env["GOOGLE_CLOUD_PROJECT"] = project_id
    return {
        "command": "npx",
        "args": ["-y", MCP_PACKAGE],
        "env": env,
    }


def build_mcp_config(project_id: str) -> dict[str, Any]:
    return {"mcpServers": {MCP_SERVER_KEY: build_mcp_entry(project_id)}}


def format_mcp_json(project_id: str) -> str:
    return json.dumps(build_mcp_config(project_id), indent=2)


def _read_mcp_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def install_mcp_config(root: Path, *, project_id: str | None = None) -> Path:
    root = root.resolve()
    pid = project_id or project_id_from_config(root)
    target = root / ".mcp.json"
    existing = _read_mcp_file(target)
    servers = dict(existing.get("mcpServers") or {})
    servers[MCP_SERVER_KEY] = build_mcp_entry(pid)
    merged = {**existing, "mcpServers": servers}
    target.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return target


def doctor_mcp(root: Path) -> list[str]:
    issues: list[str] = []
    root = root.resolve()
    pid = project_id_from_config(root)

    mcp_path = root / ".mcp.json"
    if not mcp_path.is_file():
        issues.append("Missing .mcp.json — run: graphcraft stitch mcp install")
        return issues

    data = _read_mcp_file(mcp_path)
    servers = data.get("mcpServers") or {}
    entry = servers.get(MCP_SERVER_KEY)
    if not entry:
        issues.append(f".mcp.json has no '{MCP_SERVER_KEY}' server — run: graphcraft stitch mcp install")
        return issues

    args = entry.get("args") or []
    if MCP_PACKAGE not in args and "kof-stitch-mcp" not in " ".join(str(a) for a in args):
        issues.append(f"Stitch MCP entry does not reference {MCP_PACKAGE}")

    env = entry.get("env") or {}
    gcp = env.get("GOOGLE_CLOUD_PROJECT") or env.get("GCLOUD_PROJECT") or pid
    if not gcp:
        issues.append("GOOGLE_CLOUD_PROJECT not set in .mcp.json env or graphcraft.config.yaml stitch.project_id")

    if shutil.which("npx") is None:
        issues.append("npx not found on PATH (required for Stitch MCP)")

    return issues
