# Brief: GraphCraft v0.7 — Design Cycle + Gate Hooks

**Date:** 2026-06-21  
**Architect:** Composer (Architect role)  
**Status:** Complete
**Task ID:** graphcraft-v6

---

## Objective

Mechanical **design phase** commands and **design gate** for UI implementation paths — overlay only, GraphStack core untouched.

---

## Scope

1. **`handoff/DESIGN_STATE.json`** — design phase machine (`design-strategist` → `designer` → `design-audit` → `ready` → `visual-review`)
2. **`graphcraft cycle`** commands:
   - `enter-design-strategist|designer|design-audit|visual-review <task-id>`
   - `enter-builder <task-id>` — design gate then delegate to `graphstack cycle enter-builder`
   - `status` — role + design phase
   - Delegate `start|enter-reviewer|enter-qa|enter-ship|close` to graphstack
3. **`graphcraft gate`** — `check`, `hook cursor`; blocks `packages/ui-core/` edits until design `ready`
4. **`scripts/gate-hook.ps1`** — GraphCraft projects call `graphcraft gate hook` (chains graphstack)
5. **`design-audit`** runs validate + harmony + evaluate + ui validate (active stack)
6. Tests + docs update

---

## Acceptance

- [ ] `cycle enter-design-audit` sets DESIGN_BRIEF Ready for Builder on PASS
- [ ] `cycle enter-builder` blocked until design ready (when gate on)
- [ ] `gate check` denies ui-core edit when phase != ready
- [ ] GraphStack `scripts/graphstack/` unchanged
