# Brief: GraphCraft v1 — Mobile Platform Foundation

**Date:** 2026-06-21  
**Architect:** Composer (Architect role)  
**Status:** Ready for Builder  
**Task ID:** graphcraft-v1

---

## Objective

Build **GraphCraft** as a domain layer on **GraphStack** (not a fork): mobile game + mobile app production with design graph, style/component/asset packs, aesthetic engine hooks, and optional Stitch import — wide tech stack support.

---

## Scope

### In Scope (v1 foundation — this cycle)

1. **Layer bootstrap**
   - `scripts/graphcraft/` Python package with CLI `graphcraft`
   - `graphcraft init` → `graphstack init` + GraphCraft overlay
   - PyPI-ready `pyproject.toml` (`MertCapkin_GraphCraft`, depends on `MertCapkin_GraphStack[graphify]`)
   - `.graphcraft-framework` marker

2. **Design graph (D1)**
   - Parse `design-system/tokens.json`, `design-system/components/*.yaml`, `design/screens/*.yaml`
   - Parse `packs/styles/*/style.yaml` for style nodes
   - Output `graphcraft-out/design-graph.json`, `DESIGN_REPORT.md`
   - Commands: `graphcraft design update`, `graphcraft design query`, `graphcraft design validate`, `graphcraft design harmony`

3. **Directory templates & config**
   - `graphcraft.config.yaml` (profile, design_source, aesthetic, stacks)
   - Example tokens, components, screens, style pack
   - `packages/ui-core/`, `packages/assets/` placeholders with README

4. **GraphCraft assets (Cursor)**
   - `.cursor/rules/graphcraft.mdc` (extends GraphStack, does not replace)
   - Skills: designer, design-strategist, stitch-import, visual-review, mobile-app, mobile-game
   - `orchestrator/GRAPHCRAFT.md` lifecycle extension
   - Handoff templates: `AESTHETIC_BRIEF.md`, `DESIGN_BRIEF.md`

5. **Packs**
   - `packs/styles/minimal-dark/`
   - `packs/mobile-app/` (RN, Flutter, SwiftUI, Kotlin Compose stacks doc)
   - `packs/mobile-game/` (Unity UGUI, Unity UI Toolkit, Godot, Unreal stacks doc)
   - `packs/stitch/` import skill + adapter skeleton

6. **Stitch adapter**
   - `graphcraft stitch import` from `.stitch/` directory (DESIGN.md + manifest)
   - `graphcraft stitch report`

7. **Documentation**
   - Root `README.md` repositioned as GraphCraft (GraphStack as dependency)
   - `CHANGELOG.md` entry for v0.1.0

8. **Tests**
   - `scripts/graphcraft/tests/` for design graph builder, harmony, stitch adapter

### Out of Scope (later cycles)

- Full UI library implementation per platform
- Figma MCP integration
- Visual diff subagent automation
- PyPI publish / GitHub release (user will push separately)
- GraphStack upstream plugin API changes
- Renaming GraphStack code in this repo (keep `scripts/graphstack/` for local dev)

---

## Graph Context

**Relevant modules:**
- `scripts/graphstack/installer.py` — pattern for overlay install
- `scripts/graphstack/graph.py` — delegate pattern for graph queries
- `scripts/graphstack/init_cmd.py` — init sequence pattern

**Blast radius:**
- New `scripts/graphcraft/` only + root docs + pyproject + cursor assets
- GraphStack core unchanged

---

## Implementation Hints

- Mirror GraphStack package layout (`cli`, `init_cmd`, `installer`, `bootstrap`, `assets/`)
- GraphCraft gate hook: merge into `.cursor/hooks.json` like GraphStack (optional v1: document only, hook script skeleton)
- Design graph node `type`: screen, component, token, style, asset, collection
- Edge types: uses_component, uses_token, variant_of, navigates_to, harmonizes_with, clashes_with, style_compatible
- Wide stack: document in pack READMEs; config `stacks:` lists supported targets

**Files Builder must read:**
- `scripts/graphstack/installer.py`
- `scripts/graphstack/init_cmd.py`
- `scripts/graphstack/cli.py`

---

## Acceptance Criteria

- [x] `py -3 -m graphcraft --version` works
- [x] `py -3 -m graphcraft init . -y --install-deps` installs overlay (rules, skills, templates)
- [x] `py -3 -m graphcraft design update .` produces `graphcraft-out/design-graph.json`
- [x] `py -3 -m graphcraft design harmony .` runs without error on examples
- [x] `py -3 -m graphcraft doctor .` reports GraphStack + GraphCraft status
- [x] `py -3 -m pytest scripts/graphcraft/tests -q` passes
- [x] README describes GraphCraft vision, layer model, mobile stacks, aesthetic engine

---

## Handoff Note

User goal: comprehensive mobile game/app platform. v1 is foundation; aesthetic web research and full UI libs are scaffolded via skills/templates. GraphStack cycle discipline preserved — Designer phases documented in GRAPHCRAFT.md.

---

*— Architect handoff complete.*
