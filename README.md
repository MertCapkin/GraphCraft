<div align="center">

# GraphCraft 🎨📱

**Mobile game & app design layer on GraphStack.**  
Design graph · aesthetic engine · originality · Stitch · multi-stack UI

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/MertCapkin_GraphCraft)](https://pypi.org/project/MertCapkin_GraphCraft/)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-blue)](https://cursor.sh)

</div>

GraphCraft is what you **install and run** in your mobile project. [GraphStack](https://github.com/MertCapkin/GraphStack) is a **dependency** (cycle, gate, code graph). GraphCraft adds the **design intelligence layer** without forking GraphStack.

```
Graphify     → code graph         (graphify-out/)
GraphStack   → orchestration      (cycle, gate, roles)
GraphCraft   → design layer       (graphcraft-out/, design-system/, research/)
```

---

## Install

**Requirements:** Python 3.8+, Git, [Cursor](https://cursor.sh)

```powershell
pip install "MertCapkin_GraphCraft[graphstack,visual]"
```

| Extra | Purpose |
|-------|---------|
| `graphstack` | GraphStack + Graphify (required for full workflow) |
| `visual` | PNG visual review (`pillow`) |
| `dev` | pytest (contributors) |

**Pin a release:**

```powershell
pip install "MertCapkin_GraphCraft[graphstack] @ git+https://github.com/MertCapkin/GraphCraft.git@v2.4.0"
```

---

## Quick start (your app repo)

```powershell
cd C:\path\to\your-mobile-app
graphcraft init . -y --install-deps
graphcraft doctor .
graphcraft design update .
```

`graphcraft init` runs **GraphStack init** then **GraphCraft install**. You get clean handoff templates, empty `graphcraft-out/`, and example design files — **no cycle history or generated reports**.

---

## Typical UI task workflow

```
1. Architect     → handoff/BRIEF.md
2. Design Strategist → AESTHETIC_BRIEF.md + research pipeline (below)
3. Designer        → design/, design-system/, DESIGN_BRIEF Ready for Builder
4. Design audit    → graphcraft cycle enter-design-audit <task>
5. Builder         → packages/ui-core/ (gated)
6. Visual review   → graphcraft visual review
7. Reviewer → QA → Ship (GraphStack)
```

Mechanical design commands:

```powershell
graphcraft cycle start my-feature "Login flow"
graphcraft cycle enter-design-strategist my-feature
# … strategist work …
graphcraft cycle enter-design-audit my-feature
graphcraft cycle enter-builder my-feature
```

---

## Aesthetic & originality (anti-slop)

```powershell
# 1. Fill handoff/AESTHETIC_BRIEF.md (identity + signature element)
# 2. Automated research
graphcraft aesthetic research doctor .
graphcraft aesthetic research run . --force
graphcraft aesthetic research distill .

# 3. Evaluate (includes originality score)
graphcraft design evaluate .
```

| Score | Meaning |
|-------|---------|
| `originality` ≥ 0.65 | PASS — sufficiently distinct |
| 0.45 – 0.65 | WARN — refine thesis / tokens |
| &lt; 0.45 | FAIL — generic / pack-default slop |

Config floors in `graphcraft.config.yaml`:

```yaml
aesthetic:
  hard_floors:
    originality_min: 0.45
    originality_warn: 0.65
```

---

## Google Stitch integration

Three paths — pick one:

### A. One-command pull (API — recommended for scripts)

```powershell
$env:STITCH_API_KEY = "your-key"
# graphcraft.config.yaml → stitch.project_id: "<numeric-project-id>"

graphcraft stitch doctor .
graphcraft stitch pull . --force
```

Uses official `@google/stitch-sdk` via `npx`. Downloads screens → `.stitch/` → design graph.

### B. MCP (Cursor agent in chat)

```powershell
graphcraft stitch mcp install
graphcraft stitch mcp doctor
# Authenticate: gcloud auth application-default login
# Use Stitch MCP tools in Cursor, then:
graphcraft stitch import .
```

### C. Manual export

```powershell
graphcraft stitch fetch --export-dir C:\path\to\stitch-export
graphcraft stitch import .
graphcraft stitch report .
```

Set `design_source: stitch|hybrid` in `graphcraft.config.yaml`.

---

## Design graph

```powershell
graphcraft design update .              # build graph
graphcraft design query "screens"       # keyword query
graphcraft design bridge                # design ↔ code map
graphcraft design unified "login flow"  # design + bridge
graphcraft design validate
graphcraft design harmony
```

Output: `graphcraft-out/design-graph.json`, `DESIGN_REPORT.md`

---

## UI library (four stacks)

| Stack | Path |
|-------|------|
| React Native / Expo | `packages/ui-core/rn` |
| Flutter | `packages/ui-core/flutter` |
| Unity UGUI | `packages/ui-core/unity` |
| Godot 4 | `packages/ui-core/godot` |

```powershell
graphcraft ui tokens emit rn
graphcraft ui validate all
```

---

## Commands reference

| Command | Purpose |
|---------|---------|
| `graphcraft init .` | GraphStack + GraphCraft overlay |
| `graphcraft doctor .` | Health check |
| `graphcraft design update .` | Build design graph |
| `graphcraft design evaluate` | Contrast, harmony, **originality** |
| `graphcraft aesthetic research run` | Web research → `INSPIRATION.md` |
| `graphcraft aesthetic research distill` | Anti-slop + differentiation thesis |
| `graphcraft stitch pull` | Stitch API → `.stitch/` |
| `graphcraft stitch doctor` | Stitch auth + MCP check |
| `graphcraft visual review` | PNG vs implementation |
| `graphcraft cycle status` | Design phase + GraphStack role |
| `graphcraft gate check` | Block ui-core until design ready |

Full GraphStack commands: `python -m graphstack --help`

---

## Configuration

```yaml
profile: mobile-app              # mobile-app | mobile-game
design_source: native            # native | stitch | hybrid
active_stack: react-native

design:
  style: style:minimal-dark
  touch_target_min: 44

aesthetic:
  priority: balanced             # marketing | usability | balanced
  research_enabled: true
  max_research_queries: 5
  hard_floors:
    contrast_min: 4.5
    originality_min: 0.45

stitch:
  enabled: false
  project_id: ""                 # Stitch numeric project id
```

---

## Project layout (after `graphcraft init`)

```
your-project/
├── graphcraft.config.yaml
├── design-system/              # tokens, components
├── design/screens/             # screen YAML specs
├── research/
│   └── INSPIRATION.template.md # run research to generate INSPIRATION.md
├── graphcraft-out/             # generated (gitignore in your app)
├── handoff/
│   ├── BRIEF.md                # templates — fill per task
│   ├── AESTHETIC_BRIEF.md
│   ├── DESIGN_BRIEF.md
│   ├── REVIEW.md
│   ├── STATE.json
│   ├── DESIGN_STATE.json
│   └── board/                  # todo / doing / done (empty)
├── .stitch/                    # Stitch reference (optional)
└── packages/ui-core/           # per-stack UI implementations
```

**Do not commit:** `graphcraft-out/*`, `research/INSPIRATION.md`, `handoff/board/*/*.json` (cycle tasks) — regenerate via CLI.

---

## Mobile stacks

| Profile | Targets |
|---------|---------|
| **mobile-app** | React Native, Expo, Flutter, SwiftUI, Jetpack Compose, KMP, Ionic, Capacitor |
| **mobile-game** | Unity UGUI, Unity UI Toolkit, Godot, Unreal UMG, Defold, Cocos |

See `packs/mobile-app/STACKS.md` and `packs/mobile-game/STACKS.md`.

---

## Documentation

| Doc | Content |
|-----|---------|
| [CHANGELOG_GRAPHCRAFT.md](CHANGELOG_GRAPHCRAFT.md) | Release history (v0.1 → v2.4) |
| [docs/GRAPHSTACK.md](docs/GRAPHSTACK.md) | GraphStack dependency |
| [docs/FLOW.md](docs/FLOW.md) | Orchestrator overlay |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layer model |
| [docs/PYPI.md](docs/PYPI.md) | PyPI install & publish |
| [packs/stitch/README.md](packs/stitch/README.md) | Stitch pack notes |

---

## Contributors (this repo)

```powershell
git clone https://github.com/MertCapkin/GraphCraft.git
cd GraphCraft
pip install -e ".[full]"
py -3 -m pytest scripts/graphcraft/tests -q
python scripts/sync_graphcraft_assets.py
```

---

## License

MIT — see [LICENSE](LICENSE). GraphStack is a separate MIT dependency.
