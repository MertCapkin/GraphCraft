# GRAPHCRAFT Orchestrator Extension

GraphCraft extends GraphStack with **design-first mobile production**. Load this after `orchestrator/ORCHESTRATOR.md`.

---

## When GraphCraft Is Active

If `.graphcraft-framework` exists or `graphcraft.config.yaml` is present → apply GraphCraft lifecycle extensions.

Announce: `[GRAPHCRAFT]` when entering design phases.

---

## Extended Lifecycle

```
ARCHITECT          → BRIEF.md (functional)
DESIGN STRATEGIST  → AESTHETIC_BRIEF.md + research/INSPIRATION.md
DESIGNER/CURATOR   → design/, design-system/, optional .stitch/
DESIGN AUDIT       → design validate + harmony + DESIGN_BRIEF Ready for Builder
BUILDER            → uses design graph + UI/asset packages
VISUAL REVIEW      → PNG reference vs implementation
REVIEWER → QA → SHIP   (GraphStack unchanged)
```

Mechanical commands (GraphCraft):

```bash
python -m graphcraft design update .
python -m graphcraft design validate
python -m graphcraft design harmony
python -m graphcraft stitch import .    # when design_source: stitch|hybrid
python -m graphcraft doctor .
```

State roles (handoff/STATE.json): `design-strategist`, `designer`, `design-audit`, `visual-review`

---

## Design Graph First

Before UI implementation, query design graph:

```bash
python -m graphcraft design query "screens"
python -m graphcraft design query "tokens"
```

Code structure: `python -m graphstack graph query "..."`

---

## Profiles

| Profile | Pack | Stacks |
|---------|------|--------|
| mobile-app | packs/mobile-app/ | RN, Flutter, SwiftUI, Compose… |
| mobile-game | packs/mobile-game/ | Unity, Godot, Unreal… |

Read `graphcraft.config.yaml` for `active_stack`.

---

## Design Source Modes

| Mode | Behavior |
|------|----------|
| native | Designer writes YAML specs |
| stitch | Import `.stitch/`, Curator approves screens |
| hybrid | Stitch reference + native overrides |

---

## Gate Extensions (advisory v0.1)

- Builder should not implement screens absent from design graph
- `design_source: stitch` → prefer `.stitch/designs/*.png` as visual ground truth
- Visual Review before Code Reviewer when `gates.require_visual_qa: true`

---

## Token Discipline

- DESIGN_REPORT.md — read once per session (like GRAPH_REPORT.md)
- design graph query before opening design YAML files
- research/INSPIRATION.md for aesthetic research corpus

---

*GraphCraft v0.1 — mobile game & app design layer on GraphStack*
