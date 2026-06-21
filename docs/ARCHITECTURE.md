# GraphCraft Architecture

## Layer model

GraphCraft is a **domain extension layer**, not a GraphStack fork.

```
pip install MertCapkin_GraphCraft[graphstack]
         │
         ├── graphcraft package    ← design CLI, design graph, overlay installer
         └── MertCapkin_GraphStack  ← dependency (orchestration, gate, board)
                  └── graphifyy     ← dependency (code graph)
```

---

## Integration strategy: overlay only

GraphStack upstream files are **never patched**:

| GraphStack file | GraphCraft approach |
|-----------------|---------------------|
| `orchestrator/ORCHESTRATOR.md` | **Untouched** — read as dependency |
| `.cursor/rules/graphstack.mdc` | **Untouched** — installed by `graphstack init` |
| `scripts/graphstack/*.py` | **Untouched** — PyPI package |
| Cycle / gate logic | **Untouched** — delegate via CLI |

GraphCraft adds **parallel files**:

| GraphCraft file | Role |
|-----------------|------|
| `orchestrator/GRAPHCRAFT.md` | Design lifecycle extension |
| `.cursor/rules/graphcraft.mdc` | Primary greet + design routing |
| `.cursor/skills/designer/` etc. | New roles |
| `scripts/graphcraft/` | Design CLI |
| `graphcraft-out/` | Design graph output |

---

## v0.1 verification: GraphStack unchanged

The GraphCraft v0.1 commit (`4bb5e5c`) did **not** modify any file under `scripts/graphstack/`. Zero matches for `graphcraft` in GraphStack Python source.

Repo-level changes only:
- Added `scripts/graphcraft/` (new)
- Added GraphCraft docs, config, design templates
- `pyproject.toml` primary package → `MertCapkin_GraphCraft` (monorepo ships both packages for dev)
- `README.md` (now GraphCraft-only)

---

## Monorepo vs end-user install

| Audience | GraphStack source |
|----------|-------------------|
| **End user** | PyPI `MertCapkin_GraphStack` via `graphcraft init` |
| **Contributor (this repo)** | Bundled `scripts/graphstack/` for offline dev + pytest |

Contributors must not edit GraphStack files for GraphCraft features — add overlay instead.

---

## Design graph vs code graph

| | Code graph | Design graph |
|--|------------|--------------|
| Tool | Graphify / `graphstack graph` | `graphcraft design` |
| Output | `graphify-out/` | `graphcraft-out/` |
| Models | AST imports, calls | screen ↔ component ↔ token |

No merge into Graphify — separate query CLIs.

---

## Future development rule

> **If a feature needs GraphStack changes → propose upstream PR to GraphStack.**  
> **If GraphCraft-specific → overlay only (graphcraft.mdc, GRAPHCRAFT.md, graphcraft CLI).**

This keeps `graphstack init` safe for GraphCraft users.
