# Case Study: GraphStack Source Repository (Self-Analysis)

**Date:** 2026-05-17  
**Version:** GraphStack v4.1.0  
**Corpus:** GraphStack repo (workflow markdown + Python core + demo TypeScript)

---

## Context

GraphStack's own repository is mostly **instruction markdown** (~34 tracked source files in the first graph run). That makes it a poor benchmark for token savings on a typical app — but a good honesty check for graph quality.

---

## Graph quality (before `.graphifyignore`)

From `graphify-out/GRAPH_REPORT.md` (full-repo scan):

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Nodes | 420 | Many are README / prompt code blocks |
| Isolated nodes | 186 (~44%) | Doc fragments, not modules |
| Community cohesion | 0.07–0.12 | Clusters are narrative, not architecture |
| God nodes | `GraphStack 🧠⚡`, `echo()`, `ORCHESTRATOR` | Meta concepts, not code hubs |

**Takeaway:** Running `/graphify .` on the GraphStack repo without ignores produces a **documentation graph**, not a code topology map. Use `.graphifyignore` (shipped in v4.1) or scan only `scripts/graphstack/**/*.py` and `demo/src/**` for actionable structure.

---

## Token savings — what we can claim today

The README percentage table (30%–88%) is an **estimate** based on Graphify benchmarks and TOKEN_OPTIMIZER rules. This repo does not yet ship automated session token logging.

| Scenario | Expected effect | Confidence |
|----------|-----------------|------------|
| Architecture question on 50+ file API | High savings if agent reads GRAPH_REPORT first | Medium (depends on model compliance) |
| Single-file bugfix | Low or negative (handoff overhead) | High |
| Undisciplined session (skips graph, re-reads files) | Negative vs baseline | High |
| GraphStack meta-repo (mostly .md) | Low graph value | High |

**Planned:** Community case studies with real `tokens/day` logs from Cursor or Claude Code exports.

---

## v4.1 validation workflow (measurable)

These checks do not require an LLM:

```bash
pip install -e .
graphstack doctor          # human-readable health report
graphstack validate        # exit 1 on layout errors
graphstack validate --fail-stale-graph   # CI: graph must match HEAD
```

On a fresh clone with template `handoff/BRIEF.md`, `validate` reports **warnings** (template brief). With `--strict`, template brief is an **error** — useful before Builder handoff.

---

## Recommendations for adopters

1. **Commit** `graphify-out/GRAPH_REPORT.md` and `graph.json`; **ignore** `graphify-out/cache/`.
2. Run `graphstack validate --fail-stale-graph` in CI after code changes.
3. Use GraphStack on codebases with **20+ files** and clear module boundaries (see README suitability table).
4. Do not expect the orchestrator state machine to enforce itself — use `validate` + role discipline.

---

*This case study is part of GraphStack v4.1.0 transparency work. Replace estimates with measured data as contributors submit real projects.*
