<div align="center">

# GraphCraft 🎨📱

**Mobile game & app design layer on GraphStack.**  
Design graph · style packs · aesthetic engine · Stitch import · wide mobile stack support.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-blue)](https://cursor.sh)

</div>

GraphCraft is the **product you install and use**. [GraphStack](https://github.com/MertCapkin/GraphStack) is a **dependency** that provides orchestration (cycle, gate, roles, code graph). GraphCraft adds the **design layer** without forking or patching GraphStack.

```
Graphify     → code graph        (graphify-out/)
GraphStack   → orchestration     (cycle, gate, roles)     ← dependency
GraphCraft   → design layer      (graphcraft-out/, design-system/)
```

> **Important:** GraphCraft never modifies GraphStack source. Integration is **overlay-only**: extra rules, skills, `orchestrator/GRAPHCRAFT.md`, and `graphcraft` CLI. GraphStack files come from the `MertCapkin_GraphStack` package unchanged.

---

## Quick Start

**Requirements:** Python 3.8+, Git, [Cursor](https://cursor.sh)

### Install (PyPI)

```powershell
pip install "MertCapkin_GraphCraft[graphstack]"
```

For visual review and aesthetic PNG checks, add the `visual` extra:

```powershell
pip install "MertCapkin_GraphCraft[graphstack,visual]"
```

### Install (GitHub)

```powershell
pip install "MertCapkin_GraphCraft[graphstack] @ git+https://github.com/MertCapkin/GraphCraft.git@v2.0.0"
```

GraphStack + Graphify install automatically via the `[graphstack]` extra from PyPI.

### 2. Initialize your project

Open your **app/game repo** in Cursor, then in terminal:

```powershell
graphcraft init . -y --install-deps
```

This runs **`graphstack init`** first (GraphStack overlay), then **`graphcraft install`** (GraphCraft overlay). Both rule sets load in Cursor automatically.

### 3. Build graphs

```powershell
graphcraft design update .          # design graph
# In Cursor chat: /graphify .       # code graph (or: graphstack graph update .)
graphcraft doctor .
```

### 4. Start working

Describe your mobile app or game in Cursor chat. GraphCraft orchestrator activates first; GraphStack handles cycle/gate mechanics.

---

## Install from source (this repo — contributors)

```powershell
git clone https://github.com/MertCapkin/GraphCraft.git
cd GraphCraft
pip install -e ".[full]"
```

Initialize a **consumer project** (not this framework repo):

```powershell
cd C:\path\to\your-mobile-app
graphcraft init . -y --install-deps
```

See [docs/GRAPHSTACK.md](docs/GRAPHSTACK.md) for dependency details.

---

## What runs when you open a task?

GraphCraft uses an **overlay orchestrator** — GraphStack is not edited, but GraphCraft is not skipped.

| Step | What loads | Purpose |
|------|------------|---------|
| 1 | `.cursor/rules/graphcraft.mdc` | **Primary** greeting, design routing |
| 2 | `.cursor/rules/graphstack.mdc` | Cycle, gate, token discipline (unchanged) |
| 3 | `orchestrator/GRAPHCRAFT.md` | Design lifecycle extension |
| 4 | `orchestrator/ORCHESTRATOR.md` | GraphStack cycle mechanics |
| 5 | `graphcraft-out/DESIGN_REPORT.md` | Design graph summary |
| 6 | `graphify-out/GRAPH_REPORT.md` | Code graph summary |

### User request flow (UI/mobile task)

```
User goal in chat
    → [GRAPHCRAFT] greet + read design context
    → ARCHITECT (GraphStack cycle start + BRIEF.md)
    → DESIGN STRATEGIST (AESTHETIC_BRIEF.md)     ← GraphCraft adds
    → DESIGNER (design graph, screens, tokens)   ← GraphCraft adds
    → DESIGN AUDIT (validate + harmony)          ← GraphCraft adds
    → BUILDER (GraphStack — requires brief + design ready)
    → VISUAL REVIEW                              ← GraphCraft adds
    → REVIEWER → QA → SHIP (GraphStack unchanged)
```

Pure backend tasks (no UI): GraphStack flow only — design phases skipped.

Full detail: [docs/FLOW.md](docs/FLOW.md) · [orchestrator/GRAPHCRAFT.md](orchestrator/GRAPHCRAFT.md)

---

## Commands

| Command | Layer | Purpose |
|---------|-------|---------|
| `graphcraft init .` | GraphCraft | GraphStack init + GraphCraft overlay |
| `graphcraft doctor .` | GraphCraft | Health check (both layers) |
| `graphcraft design update .` | GraphCraft | Build design graph |
| `graphcraft design query "screens"` | GraphCraft | Query design graph |
| `graphcraft design validate` | GraphCraft | Validate design graph |
| `graphcraft design harmony` | GraphCraft | Component harmony check |
| `graphcraft design evaluate` | GraphCraft | Aesthetic rubric (contrast, touch targets) |
| `graphcraft aesthetic research run` | GraphCraft | Auto web research → INSPIRATION.md |
| `graphcraft design bridge` | GraphCraft | Design ↔ code bridge map |
| `graphcraft stitch import .` | GraphCraft | Import Stitch prototype |
| `graphcraft stitch pull .` | GraphCraft | Pull from Stitch API (official SDK) |
| `graphcraft stitch doctor` | GraphCraft | Stitch pull + MCP readiness |
| `graphcraft visual review` | GraphCraft | PNG reference vs implementation |
| `graphcraft ui validate all` | GraphCraft | Validate UI lib vs design tokens |
| `graphcraft cycle status` | GraphCraft | Design phase + GraphStack role |
| `graphcraft gate check` | GraphCraft | Design gate before ui-core edits |
| `python -m graphstack cycle start …` | GraphStack | Start dev cycle |
| `python -m graphstack graph query "…"` | GraphStack | Query code graph |

---

## Configuration

Edit `graphcraft.config.yaml`:

```yaml
profile: mobile-app          # mobile-app | mobile-game
design_source: native        # native | stitch | hybrid
active_stack: react-native   # see packs/mobile-app/STACKS.md
```

---

## Mobile stacks

| Profile | Targets |
|---------|---------|
| **mobile-app** | React Native, Expo, Flutter, SwiftUI, Jetpack Compose, KMP, Ionic, Capacitor |
| **mobile-game** | Unity UGUI, Unity UI Toolkit, Godot, Unreal UMG, Defold, Cocos |

Pack docs: `packs/mobile-app/STACKS.md` · `packs/mobile-game/STACKS.md`

---

## Project layout (after init)

```
your-project/
├── graphcraft.config.yaml
├── design-system/           # tokens, components
├── design/screens/          # screen specs
├── graphcraft-out/          # design-graph.json
├── graphify-out/            # code graph (Graphify)
├── handoff/                 # BRIEF, DESIGN_BRIEF, AESTHETIC_BRIEF
├── orchestrator/
│   ├── GRAPHCRAFT.md        # GraphCraft extension
│   └── ORCHESTRATOR.md      # GraphStack (from dependency)
├── .cursor/rules/
│   ├── graphcraft.mdc       # GraphCraft overlay (primary)
│   └── graphstack.mdc       # GraphStack (from dependency)
└── scripts/
    ├── graphcraft/          # GraphCraft CLI copy
    └── graphstack/          # GraphStack CLI copy
```

---

## Design sources

| Mode | Use when |
|------|----------|
| `native` | YAML design-system + screens from scratch |
| `stitch` | Google [Stitch](https://stitch.withgoogle.com/) prototype import |
| `hybrid` | Stitch visual reference + native refinement |

---

## Documentation

| Doc | Content |
|-----|---------|
| [docs/GRAPHSTACK.md](docs/GRAPHSTACK.md) | GraphStack dependency — install, what it provides |
| [docs/FLOW.md](docs/FLOW.md) | Orchestrator overlay — who runs first |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layer model — why GraphStack is untouched |
| [CHANGELOG_GRAPHCRAFT.md](CHANGELOG_GRAPHCRAFT.md) | GraphCraft releases |
| [docs/PYPI.md](docs/PYPI.md) | PyPI publish + install |

---

## License

MIT — see [LICENSE](LICENSE).

GraphStack is © its contributors, installed as a separate dependency under MIT.
