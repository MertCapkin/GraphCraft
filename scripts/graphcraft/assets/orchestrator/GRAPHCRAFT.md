# GRAPHCRAFT Orchestrator Extension

**GraphCraft overlay on GraphStack (dependency).**  
GraphStack's `orchestrator/ORCHESTRATOR.md` is **not modified** — read it for cycle/gate mechanics.  
This file extends the lifecycle for **mobile game/app design**.

Load order: `TOKEN_OPTIMIZER.md` → `GRAPHCRAFT.md` (this file) → `ORCHESTRATOR.md`

Announce: `[GRAPHCRAFT]` when entering design phases.

---

## Primary greeting (overrides GraphStack step 8)

```
GraphCraft ready.
Profile: … | Design graph: … | Code graph: … | Board: …
```

---

## Extended Lifecycle (UI/mobile tasks)

```
ARCHITECT          → BRIEF.md (functional)              [GraphStack]
DESIGN STRATEGIST  → AESTHETIC_BRIEF.md                 [GraphCraft]
DESIGNER/CURATOR   → design/, design-system/, .stitch/  [GraphCraft]
DESIGN AUDIT       → validate + harmony → DESIGN_BRIEF  [GraphCraft]
BUILDER            → design graph + UI packages         [GraphStack + GraphCraft context]
VISUAL REVIEW      → PNG reference vs code              [GraphCraft]
REVIEWER → QA → SHIP                                     [GraphStack unchanged]
```

Non-UI tasks: skip GraphCraft phases → GraphStack only.

---

## Mechanical commands

```bash
# GraphCraft
python -m graphcraft design update .
python -m graphcraft design validate
python -m graphcraft design harmony
python -m graphcraft stitch import .
python -m graphcraft doctor .

# GraphStack (dependency — unchanged)
python -m graphstack cycle start <id> "<title>"
python -m graphstack cycle enter-builder <id>
python -m graphstack cycle enter-reviewer <id>
python -m graphstack cycle enter-qa <id>
python -m graphstack cycle enter-ship <id>
python -m graphstack cycle close <id>
```

---

## Design Graph First (UI tasks)

```bash
python -m graphcraft design query "screens"
python -m graphcraft design query "tokens"
python -m graphstack graph query "…"    # code structure
```

---

## Profiles & packs

| Profile | Config | Pack doc |
|---------|--------|----------|
| mobile-app | `profile: mobile-app` | `packs/mobile-app/STACKS.md` |
| mobile-game | `profile: mobile-game` | `packs/mobile-game/STACKS.md` |

`graphcraft.config.yaml` → `design_source`, `active_stack`, `aesthetic`, `stitch`

---

## Integration principle

GraphCraft **never patches GraphStack**. Overlay files only.  
See `docs/ARCHITECTURE.md` · `docs/FLOW.md` · `docs/GRAPHSTACK.md`

---

*GraphCraft v0.1 — mobile game & app design layer on GraphStack*
