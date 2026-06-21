# Brief: GraphCraft v2.3 — Originality Engine

**Date:** 2026-06-21  
**Status:** Complete
**Task ID:** graphcraft-v10

---

## Objective

Anti-slop **originality** layer: `research distill` + `originality` evaluate score + design-audit gate.

## Scope

1. **`aesthetic/distill.py`** — generic phrase detection, overlap, thesis injection → INSPIRATION.md
2. **`aesthetic/originality.py`** — token distance, layout diversity, reference independence, signature, distill quality
3. **`evaluate`** — add `originality` score; FAIL/WARN thresholds
4. **`design_audit`** — originality FAIL blocks audit
5. AESTHETIC_BRIEF differentiation fields; tests; v2.3.0

## Acceptance

- [ ] `research distill` updates INSPIRATION with `## Differentiation thesis`
- [ ] `evaluate` reports `originality` score
- [ ] `design-audit` fails when originality < floor
- [ ] Tests pass
