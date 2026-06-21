# GraphCraft Request Flow

How GraphCraft and GraphStack work together when a user opens a task in Cursor.

---

## Layer responsibility

```
┌─────────────────────────────────────────────────────────┐
│  GraphCraft (overlay — PRIMARY for greeting & design)   │
│  graphcraft.mdc · GRAPHCRAFT.md · graphcraft CLI        │
├─────────────────────────────────────────────────────────┤
│  GraphStack (dependency — cycle, gate, code graph)    │
│  graphstack.mdc · ORCHESTRATOR.md · graphstack CLI      │
├─────────────────────────────────────────────────────────┤
│  Graphify (dependency — AST code graph)                 │
│  graphify-out/ · /graphify                              │
└─────────────────────────────────────────────────────────┘
```

**Rule:** GraphCraft rules load **in addition to** GraphStack rules. GraphCraft overrides **greeting and design routing only**. GraphStack owns **cycle, gate, and ship**.

---

## Session activation (every chat)

Both `alwaysApply: true` rules fire. Agent must follow **both**, with this order:

| Order | Read | Owner |
|-------|------|-------|
| 1 | `orchestrator/TOKEN_OPTIMIZER.md` | GraphStack |
| 2 | `graphcraft-out/DESIGN_REPORT.md` | GraphCraft |
| 3 | `graphify-out/GRAPH_REPORT.md` | Graphify |
| 4 | `orchestrator/GRAPHCRAFT.md` | GraphCraft |
| 5 | `graphcraft.config.yaml` | GraphCraft |
| 6 | `handoff/BRIEF.md` | GraphStack |
| 7 | `handoff/board/doing/*.json` | GraphStack |

**Greeting:** `GraphCraft ready.` (not `GraphStack ready.`) — see `graphcraft.mdc`.

---

## Task routing decision tree

```
User message
    │
    ├─ Empty / greeting only
    │     → GraphCraft greet → wait
    │
    ├─ Task with UI / design / mobile screens / style / Stitch
    │     → GraphCraft: check profile + design_source
    │     → GraphStack: cycle start + ARCHITECT + BRIEF.md
    │     → GraphCraft: DESIGN STRATEGIST → DESIGNER → DESIGN AUDIT
    │     → GraphStack: enter-builder (requires DESIGN_BRIEF Ready)
    │     → GraphCraft: VISUAL REVIEW
    │     → GraphStack: REVIEWER → QA → SHIP
    │
    └─ Task without UI (API, tooling, docs-only)
          → GraphStack flow only (skip design phases)
          → graphcraft design update NOT required
```

---

## What GraphCraft adds (never skip for UI tasks)

| Phase | Handoff file | Gate |
|-------|--------------|------|
| Design Strategist | `handoff/AESTHETIC_BRIEF.md` | Before Designer |
| Designer | `design/`, `design-system/`, `handoff/DESIGN_BRIEF.md` | Before Builder |
| Design Audit | `graphcraft design validate` + `harmony` | Before `enter-builder` |
| Visual Review | `handoff/REVIEW.md` section | Before Code Reviewer |

---

## Mechanical commands by phase

```bash
# GraphStack (always for code tasks)
python -m graphstack cycle start <id> "<title>"
python -m graphstack cycle enter-builder <id>
python -m graphstack cycle enter-reviewer <id>
python -m graphstack cycle enter-qa <id>
python -m graphstack cycle enter-ship <id>
python -m graphstack cycle close <id>

# GraphCraft (UI/design tasks)
python -m graphcraft design update .
python -m graphcraft design validate
python -m graphcraft design harmony
python -m graphcraft stitch import .    # if design_source: stitch|hybrid
python -m graphcraft doctor .
```

---

## Conflict prevention

| Risk | Solution |
|------|----------|
| Agent skips design phases | `graphcraft.mdc` mandates design routing for UI tasks |
| GraphStack greet hides GraphCraft | GraphCraft rule overrides greeting text |
| Patching ORCHESTRATOR.md | **Forbidden** — use `GRAPHCRAFT.md` extension only |
| Stale GraphStack in repo | Users install via PyPI; `graphstack init` refreshes |
| GraphCraft assets bundle GraphStack files | **Forbidden** — GraphCraft wheel ships overlay only |

---

## Slash command

In Cursor: `/graphcraft` — loads GraphCraft context (see `.cursor/commands/graphcraft.md`).

GraphStack `/graphstack` still works for cycle mechanics.
