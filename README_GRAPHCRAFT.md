# GraphCraft — Mobile Design Layer on GraphStack

GraphCraft extends [GraphStack](https://github.com/MertCapkin/GraphStack) with a **design intelligence layer** for **mobile games** and **mobile apps**.

## Stack model

```
Graphify     → code graph (graphify-out/)
GraphStack   → orchestration (cycle, gate, roles)
GraphCraft   → design graph, style packs, UI/asset libs, aesthetic engine
```

## Quick start

```powershell
pip install "MertCapkin_GraphCraft[graphstack]"
graphcraft init . -y --install-deps
graphcraft design update .
graphcraft doctor .
```

From source (this repo):

```powershell
py -3 -m pip install -e ".[graphstack,dev]"
py -3 -m graphcraft init . -y --skip-graphstack
py -3 -m graphcraft design update .
```

## Commands

| Command | Purpose |
|---------|---------|
| `graphcraft init` | GraphStack + GraphCraft overlay |
| `graphcraft design update` | Build `graphcraft-out/design-graph.json` |
| `graphcraft design query "screens"` | Query design graph |
| `graphcraft design harmony` | Component harmony check |
| `graphcraft design validate` | Schema validation |
| `graphcraft stitch import` | Ingest `.stitch/` prototypes |
| `graphcraft doctor` | Health check |
| `python -m graphstack cycle ...` | Full dev lifecycle (unchanged) |

## Mobile tech stacks (supported targets)

### Mobile app (`profile: mobile-app`)
React Native · Expo · Flutter · SwiftUI · Jetpack Compose · Kotlin Multiplatform · Ionic · Capacitor

### Mobile game (`profile: mobile-game`)
Unity (UGUI · UI Toolkit) · Godot · Unreal (UMG) · Defold · Cocos

Configure in `graphcraft.config.yaml`.

## Design sources

| Mode | Description |
|------|-------------|
| `native` | YAML design-system + screens |
| `stitch` | Google Stitch prototype import (`.stitch/`) |
| `hybrid` | Stitch reference + native refinement |

## Lifecycle (GraphCraft extension)

```
Architect → Design Strategist → Designer/Curator → Design Audit
    → Builder → Visual Review → Reviewer → QA → Ship
```

See `orchestrator/GRAPHCRAFT.md`.

## Repository layout

```
design-system/     tokens + component metadata
design/screens/    screen specs
packs/styles/      style packs (themes)
packs/mobile-app/  app stack guidance
packs/mobile-game/ game stack guidance
packages/ui-core/  shared UI primitives (expand per stack)
packages/assets/   icon/sprite libraries
graphcraft-out/    design-graph.json, DESIGN_REPORT.md
.stitch/           Stitch import (optional)
```

## License

MIT — see LICENSE.
