# GraphStack Dependency

GraphCraft **depends on** [GraphStack](https://github.com/MertCapkin/GraphStack). GraphStack is **not** part of GraphCraft source — it is installed as a Python package and copied into your project by `graphstack init`.

---

## What GraphStack provides

| Capability | CLI / path |
|------------|------------|
| Dev cycle (Architect → Builder → Reviewer → QA → Ship) | `python -m graphstack cycle …` |
| Process gate (role enforcement) | `.cursor/hooks.json` + `graphstack gate` |
| Code graph queries | `python -m graphstack graph query "…"` |
| Task board | `python -m graphstack board …` |
| Orchestrator | `orchestrator/ORCHESTRATOR.md` |
| Cursor rules | `.cursor/rules/graphstack.mdc` |
| Role skills | `.cursor/skills/architect/`, `builder/`, etc. |

GraphCraft **does not modify** any of these files. They arrive unchanged from the GraphStack package.

---

## How GraphStack gets installed

### Recommended (via GraphCraft)

```powershell
pip install "MertCapkin_GraphCraft[graphstack]"
graphcraft init . -y --install-deps
```

`graphcraft init` calls `graphstack init` internally, then adds the GraphCraft overlay.

### Manual (GraphStack only — not recommended alone for GraphCraft projects)

```powershell
pip install "MertCapkin_GraphStack[graphify]"
graphstack init . -y --install-deps
graphcraft install .          # add GraphCraft overlay after
```

---

## Version pinning

GraphCraft pins compatible GraphStack versions:

```
MertCapkin_GraphStack[graphify] >= 4.7, < 5
```

If GraphStack releases breaking changes, GraphCraft releases a compatible version bump.

---

## Updating GraphStack

```powershell
pip install -U "MertCapkin_GraphStack[graphify]"
graphstack init . -y          # refresh GraphStack managed files
graphcraft install .            # refresh GraphCraft overlay (safe, non-destructive)
```

GraphCraft overlay files (`graphcraft.mdc`, `GRAPHCRAFT.md`, `design-system/`) are **not** overwritten if they already exist.

---

## Upstream repository

- GitHub: https://github.com/MertCapkin/GraphStack
- PyPI: https://pypi.org/project/MertCapkin_GraphStack/
- Issues for GraphStack bugs: GraphStack repo
- Issues for GraphCraft design layer: GraphCraft repo

---

## Why keep GraphStack separate?

1. **No fork drift** — GraphStack updates flow independently
2. **Same install for all GraphStack users** — GraphCraft users get identical gate/cycle behavior
3. **Overlay integration** — GraphCraft adds files GraphStack never lists in its installer
4. **No stale GraphStack copies** — `graphstack init` always pulls current package assets

This repo bundles `scripts/graphstack/` **only for monorepo development and offline installs**. End users should rely on the PyPI GraphStack package via `graphcraft init`.
