# GraphCraft changelog

## v2.3.0 — Originality engine (2026-06-21)

- **`graphcraft aesthetic research distill`** — anti-slop filter, differentiation thesis in INSPIRATION.md
- **`originality` score** in `aesthetic evaluate` (token, layout, reference, signature, distill)
- **Design audit** blocks on originality FAIL; `originality_min` / `originality_warn` config floors

## v2.2.0 — Aesthetic web research automation (2026-06-21)

- **`graphcraft aesthetic research run`** — query builder, DuckDuckGo search, pattern synthesis → `INSPIRATION.md`
- **`graphcraft aesthetic research doctor`** — network + config preflight
- `--offline` fixture mode for CI; `aesthetic.max_research_queries` config

## v2.1.0 — Stitch pull via official SDK (2026-06-21)

- **`graphcraft stitch pull`** — fetch screens from Stitch API into `.stitch/` + design graph import
- Node helper `pull_export.mjs` via `npx -p @google/stitch-sdk`
- Auth: `STITCH_API_KEY` (recommended) or OAuth env vars
- **`graphcraft stitch doctor`** — combined pull + MCP readiness

## v2.0.0 — Design intelligence milestone (2026-06-21)

Major release bundling design graph bridge, aesthetic engine, multi-stack UI lib,
Stitch/visual tooling, and mechanical design-cycle gates (v0.2–v0.7 work).

### Design graph (D2–D3)
- `design path`, `design explain`, `design radius`, `design unified`
- `design bridge` → `graphcraft-out/bridge.json`; `design update --bridge`

### Aesthetic engine
- `graphcraft aesthetic evaluate` — contrast, style fit, touch targets, harmony rubric
- `aesthetic research init|validate` → `research/INSPIRATION.md`
- Style pack `warm-light`; output `graphcraft-out/AESTHETIC_REPORT.md`

### Stitch & visual
- `stitch mcp print|install|doctor`, `stitch validate`, `stitch fetch`
- `visual review`, `visual diff` (optional Pillow via `[visual]` extra)

### UI library (four stacks)
- React Native, Flutter, Unity UGUI, Godot 4 — ButtonPrimary, LoginScreen, tokens
- `graphcraft ui tokens emit|validate` per stack; `ui validate all`

### Design cycle & gate
- `graphcraft cycle` — design-strategist → designer → design-audit → visual-review
- Gated `enter-builder`; `graphcraft gate check|hook cursor`
- `handoff/DESIGN_STATE.json` design phase machine

### Tests
- 37 graphcraft tests passing

## v0.1.0 — Mobile platform foundation

## Added
- GraphCraft Python package (`graphcraft` CLI) as layer on GraphStack
- Design graph: tokens, components, screens, styles, stitch import
- Commands: `design update|query|validate|harmony`, `stitch import|report`
- Style pack template (`minimal-dark`)
- Mobile app/game stack packs and Cursor skills
- Aesthetic + design handoff templates
- Optional Stitch prototype import (`.stitch/`)

## v0.1.1 — Docs, overlay clarity, PyPI publish (2026-06-21)

- README GraphCraft-only; GraphStack documented as dependency
- Orchestrator overlay (`graphcraft.mdc`, `docs/FLOW.md`, `docs/ARCHITECTURE.md`)
- GraphCraft PyPI wheel ships overlay only (GraphStack via `[graphstack]` extra)
- `publish.yml` for GraphCraft; `docs/PYPI.md` maintainer guide

## v0.7.0 — Design cycle + gate hooks (2026-06-21)

- **`graphcraft cycle`** — enter-design-strategist/designer/design-audit/visual-review; gated enter-builder
- **`graphcraft gate`** — blocks `packages/ui-core/` edits until design ready
- **`handoff/DESIGN_STATE.json`** — design phase machine
- **`scripts/gate-hook.ps1`** — GraphCraft design gate before GraphStack gate

## v0.6.0 — UI lib Flutter, Unity, Godot (2026-06-21)

- **Flutter:** `packages/ui-core/flutter` — ButtonPrimary, LoginScreen
- **Unity UGUI:** `packages/ui-core/unity` — ButtonPrimary, LoginScreen
- **Godot 4:** `packages/ui-core/godot` — button_primary, login_screen
- **CLI:** `ui tokens emit|validate` for all four stacks; `ui validate all`

## v0.5.0 — UI lib React Native v1 (2026-06-21)

- **RN package:** `packages/ui-core/rn` — ButtonPrimary, LoginScreen, tokens, theme
- **CLI:** `graphcraft ui tokens emit rn`, `graphcraft ui validate rn`
- Design graph bridge: `screen:login` → LoginScreen.tsx

## v0.4.0 — Stitch MCP bridge + visual review (2026-06-21)

- **Stitch MCP:** `stitch mcp print|install|doctor` for `@keeponfirst/kof-stitch-mcp`
- **Stitch ops:** `stitch validate`, `stitch fetch --export-dir`
- **Visual:** `visual review`, `visual diff`; optional Pillow via `[visual]` extra
- Subagent block in visual-review skill

## v0.3.0 — Aesthetic Engine v1 (2026-06-21)

- **Evaluate:** `graphcraft design evaluate` / `aesthetic evaluate` — contrast, style fit, touch targets, harmony rubric
- **Research:** `aesthetic research init|validate` → `research/INSPIRATION.md` scaffold
- **Style pack:** `warm-light` (marketing-friendly light theme)
- Output: `graphcraft-out/AESTHETIC_REPORT.md`

## v0.2.0 — Design graph D2–D3 bridge (2026-06-21)

- **D2:** `design path`, `design explain`, `design radius`; richer keyword query
- **D3:** `design bridge` → `graphcraft-out/bridge.json`; YAML + comment + heuristic scan
- **Unified:** `design unified "<question>"` merges design query + bridge matches
- `design update --bridge` rebuilds bridge after graph update
- Example `implements` on login screen + RN placeholder screen file

## v0.1.0 — Mobile platform foundation
