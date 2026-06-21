# Brief: GraphCraft v2.1 — Stitch pull (official SDK)

**Date:** 2026-06-21  
**Architect:** Composer  
**Status:** Complete
**Task ID:** graphcraft-v8

---

## Objective

`graphcraft stitch pull` — one command to fetch screens from Stitch API into `.stitch/`, then import into design graph.

## Scope

1. Node helper `pull_export.mjs` using `@google/stitch-sdk` (via `npx -p`)
2. Python `pull.py` — auth doctor, subprocess orchestration, `fetch_export`, optional import
3. CLI: `graphcraft stitch pull [root] [--project-id] [--force] [--no-import]`
4. CLI: `graphcraft stitch doctor` — pull auth + MCP readiness
5. Tests with mocked subprocess; update STITCH_IMPORT skill + CHANGELOG

## Out of scope

- Replacing kof-stitch-mcp for Cursor MCP workflow
- Automatic flow/navigation inference from Stitch

## Acceptance

- [ ] `stitch doctor` reports missing `STITCH_API_KEY` clearly
- [ ] `stitch pull` with mock export produces valid `.stitch/` + design graph ingest
- [ ] Existing `stitch fetch` unchanged
- [ ] Tests pass
