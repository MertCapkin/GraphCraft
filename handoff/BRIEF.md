# Brief: GraphCraft v2.2 — Aesthetic web research automation

**Date:** 2026-06-21  
**Architect:** Composer  
**Status:** Complete
**Task ID:** graphcraft-v9

---

## Objective

`graphcraft aesthetic research run` — auto-generate queries, fetch web results, synthesize patterns into `research/INSPIRATION.md`.

## Scope

1. **Query builder** — from `graphcraft.config.yaml` (profile, stack, priority) + optional `AESTHETIC_BRIEF.md`
2. **Web search** — DuckDuckGo HTML (stdlib urllib); `--offline` for tests/CI
3. **Synthesis** — rule-based pattern buckets + style pack scoring
4. **CLI** — `research run`, `research doctor`; keep `init`/`validate`
5. Tests with mocked/offline search; update DESIGN_STRATEGIST skill

## Out of scope

- LLM summarization in CLI (Cursor agent refines INSPIRATION)
- Paid search APIs

## Acceptance

- [ ] `research run --offline` writes valid INSPIRATION.md passing validate
- [ ] `research doctor` checks network + config
- [ ] `aesthetic.research_enabled: false` blocks run unless `--force`
- [ ] Tests pass
