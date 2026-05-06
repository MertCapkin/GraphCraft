<div align="center">

# GraphStack 🧠⚡

**Graph-first, automatically orchestrated AI development workflow.**  
One prompt starts the entire lifecycle — from blank repo to production.

[![CI](https://github.com/MertCapkin/graphstack/actions/workflows/ci.yml/badge.svg)](https://github.com/MertCapkin/graphstack/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-blue)](https://cursor.sh)
[![Works with Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-orange)](https://claude.ai/code)

</div>

---

## Quick Start

### Step 1 — Install prerequisites

**Python 3.8+** and **Git** are required. Check if you have them:

```bash
py -3 --version   # need 3.8 or higher
git --version       # any recent version is fine
```

**Install Graphify** — the knowledge graph engine GraphStack is built on:

```bash
pip install graphifyy
```

Verify it worked:
```bash
graphify --version
```

If `graphify` is not found after install, try:
```bash
pip install graphifyy --user
# then add ~/.local/bin to your PATH, or use:
python3 -m graphify --version
```

> Graphify runs **entirely locally** — no API calls, no data sent anywhere.
> It uses tree-sitter to parse your code and builds the graph on your machine.

---

### Step 2 — Install GraphStack into your project

Navigate to your project folder and run:

```bash
git clone https://github.com/MertCapkin/graphstack /tmp/graphstack
cd your-project
bash /tmp/graphstack/install.sh
```

This copies all GraphStack files into your project:
- `.cursor/rules/graphstack.mdc` — Cursor loads this automatically on every session
- `orchestrator/`, `skills/`, `handoff/`, `scripts/` — the full workflow system

The install script is non-destructive: it won't overwrite existing `handoff/BRIEF.md` or `handoff/REVIEW.md` if they already exist.

---

### Step 3 — Build the knowledge graph

Open your project in Cursor. In the chat, type:

```
/graphify .
```

What happens:
- Graphify scans all source files (25 languages supported)
- Builds a dependency graph using tree-sitter (local, no API)
- Creates three files in `graphify-out/`:
  - `GRAPH_REPORT.md` — human-readable architecture summary
  - `graph.json` — machine-queryable full graph
  - `graph.html` — visual explorer, open in browser

**How long does it take?**

| Codebase size | Time |
|---|---|
| < 50 files | ~5 seconds |
| 50–200 files | ~15–30 seconds |
| 200–500 files | ~1–2 minutes |
| 500+ files | ~3–5 minutes |

Run this once. After that, use `/graphify --update` — it only re-scans changed files and takes a few seconds.

**New project with no code yet?** Skip this step — GraphStack's Bootstrap Mode handles it. Just go to Step 4.

---

### Step 4 — Start working

Open a **new Cursor chat** and paste one of these:

**Existing codebase:**
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
[Describe what you want to build or fix]
```

**New project from scratch:**
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
This is a new project with no existing codebase.
I want to build [describe your idea].
Tech stack: [language, framework, database].
```

GraphStack handles everything from here — planning, building, reviewing, testing, shipping.

---

## What Is GraphStack?

GraphStack combines two ideas into one installable system:

**[Graphify](https://github.com/safishamsi/graphify)** builds a queryable knowledge graph of your codebase. Every AI query navigates that compact map instead of re-reading raw files from scratch.

**Role-based orchestration** drives a structured lifecycle: Bootstrapper → Architect → Builder → Reviewer → QA → Ship. A central Orchestrator manages all transitions automatically. You never switch roles manually.

> You write one prompt. GraphStack runs the full cycle.

---

## The Problem

Without GraphStack, every AI coding session looks like this:

```
You:  "Add rate limiting to login."
AI:   reads login.ts... reads session.ts... reads crypto.ts... reads types.ts...
      (4 files, ~3 000 tokens — before writing a single line)

You:  "Now add tests."
AI:   reads login.ts again... reads session.ts again...
      (same files, same cost, zero memory)
```

Problems:
- **Token waste** — AI re-reads your codebase on every query
- **No structure** — planning, coding, reviewing blur together
- **No memory** — closing Cursor means starting from zero
- **No audit trail** — impossible to know what was decided and why

---

## The Solution

```
Step 1 — once:
  /graphify .  →  graphify-out/GRAPH_REPORT.md + graph.json

Step 2 — every session (one prompt):
  "Read orchestrator/ORCHESTRATOR.md. Add rate limiting to login."

  [ARCHITECT]   reads graph (not raw files) → scopes change → writes BRIEF.md
       ↓ auto
  [BUILDER]     reads brief → queries graph for deps → builds exactly the brief
       ↓ auto
  [REVIEWER]    checks criteria → inspects graph neighbors for side effects
       ↓ auto   (loops to Builder if rejected, max 3×)
  [QA]          traces call path through graph → verifies behavior
       ↓ auto
  [SHIP]        checklist → graph update → commit message → closes board task
```

**Zero manual role switching. Zero repeated file reads. Full git audit trail.**

---

## Bootstrap Mode — Start from Zero

No code yet? GraphStack handles that too.

```
"Read orchestrator/ORCHESTRATOR.md.
 New project: REST API for task management. TypeScript, Express, PostgreSQL."

  [BOOTSTRAPPER]  analyzes idea → decomposes into modules → orders by dependency
                  → writes BOOTSTRAP.md (the memory across all cycles)
                  → writes Cycle 1 brief
       ↓ auto
  [BUILDER → REVIEWER → QA → SHIP]   Cycle 1 (auth module)
       ↓
  run /graphify .                    ← first graph from real code
       ↓
  [BOOTSTRAPPER]  reads new graph → writes Cycle 2 brief with real knowledge
       ↓ auto
  [BUILDER → REVIEWER → QA → SHIP]   Cycle 2 (data models)
       ↓
  run /graphify --update  →  next cycle  →  ...
```

Each brief is written with knowledge of what was **actually built** — not just planned. The graph grows with the project.

---

## Token Savings

GraphStack's savings come from three mechanisms:

| Mechanism | How | Savings |
|-----------|-----|---------|
| Graph-first reads | GRAPH_REPORT.md replaces browsing 10+ files | ~85% on architecture queries |
| Role discipline | Each role reads only what its job requires | ~60% vs unstructured sessions |
| File-based state | STATE.md replaces chat history on resume | ~60% per new session |
| Parallel reads | Multiple files in one tool call | ~50% on multi-file ops |

**Net savings by codebase size:**

| Codebase | Tokens/day without | Tokens/day with | Saving |
|----------|--------------------|-----------------|--------|
| Small (10–20 files) | ~40k | ~28k | **~30%** |
| Medium (50–100 files) | ~180k | ~54k | **~70%** |
| Large (200+ files) | ~600k | ~90k | **~85%** |
| Very large (500+ files) | ~1.5M | ~180k | **~88%** |

*Estimates based on Graphify benchmarks and TOKEN_OPTIMIZER rules. Real savings depend on query patterns.*

---

## What Gets Installed

```
your-project/
├── .cursor/rules/graphstack.mdc          ← always-active rules (Cursor auto-loads)
├── orchestrator/
│   ├── ORCHESTRATOR.md                   ← state machine: all transitions
│   └── TOKEN_OPTIMIZER.md                ← token budget rules for all roles
├── .cursor/skills/
│   ├── bootstrapper/BOOTSTRAPPER.md      ← new project → module plan → cycles
│   ├── architect/ARCHITECT.md            ← scopes features, writes briefs
│   ├── builder/BUILDER.md                ← implements exactly the brief
│   ├── reviewer/REVIEWER.md              ← checks criteria + graph side effects
│   ├── qa/QA.md                          ← traces call paths, verifies behavior
│   └── ship/SHIP.md                      ← checklist + graph update + commit msg
├── handoff/
│   ├── BRIEF.md                          ← Architect → Builder
│   ├── REVIEW.md                         ← Reviewer + QA findings (append-only)
│   ├── STATE.md                          ← session state for resuming
│   ├── BOOTSTRAP.md                      ← cross-cycle project memory
│   └── board/
│       ├── todo/                         ← tasks waiting to be claimed
│       ├── doing/                        ← tasks in progress
│       └── done/                         ← completed tasks (audit trail)
├── graphify-out/                         ← generated by graphify (commit this)
│   ├── GRAPH_REPORT.md
│   ├── graph.json
│   └── graph.html
├── scripts/
│   ├── board.sh                          ← GNAP task board manager
│   └── post-commit                       ← smart graph update hook
```

---

## The GNAP Board

GraphStack uses Git-Native Agent Protocol for task tracking — no server, no database, just files and git commits.

```bash
# See everything at a glance
bash scripts/board.sh status

# Create a task (Architect does this automatically)
bash scripts/board.sh new add-oauth Add OAuth login with GitHub

# Claim before starting work
bash scripts/board.sh claim add-oauth builder

# Mark done after Ship
bash scripts/board.sh complete add-oauth

# Full audit trail
bash scripts/board.sh log
```

Every board operation is a git commit. `git log handoff/board/` shows who did what, when.

---

## Graph Update Strategy

GraphStack's Ship role manages graph updates automatically at the end of every cycle:

| Condition | Action |
|-----------|--------|
| Files were **added or deleted** this cycle | Always update |
| Bootstrap cycle completed | Always update (next brief needs fresh graph) |
| Content-only edits (bug fixes, refactors) | Skip — graph topology unchanged |

The post-commit hook enforces the same rules automatically. You never need to think about when to update.

---

## Project Suitability

| Project type | Suitability | Notes |
|---|---|---|
| REST / GraphQL API | ⭐⭐⭐⭐⭐ | Best fit — clear module boundaries |
| Monolithic web app | ⭐⭐⭐⭐⭐ | God node protection is critical here |
| Data pipeline / ETL | ⭐⭐⭐⭐⭐ | Graph mirrors pipeline topology |
| Library / SDK | ⭐⭐⭐⭐⭐ | Breaking change detection is precise |
| Microservice (single) | ⭐⭐⭐⭐⭐ | Integration edges clearly visible |
| CLI tool | ⭐⭐⭐⭐ | Good for medium+ complexity |
| Serverless / Lambda | ⭐⭐⭐⭐ | Shared util blast radius visible |
| Admin panel | ⭐⭐⭐⭐ | State + API integration coverage |
| Game server (backend) | ⭐⭐⭐⭐ | State machine edges map well |
| DevOps / automation | ⭐⭐⭐⭐ | Script dependency tracking |
| React / Vue SPA | ⭐⭐⭐ | Good, but UI churn increases update frequency |
| TypeScript monorepo | ⭐⭐⭐ | Cross-package deps very valuable |
| Mobile app (React Native) | ⭐⭐⭐ | JS/TS layer fully covered |
| Unity game (C#) | ⭐⭐⭐ | God node protection excellent |
| E-commerce backend | ⭐⭐⭐ | Checkout flow blast radius useful |
| AI / embedding pipeline | ⭐⭐⭐ | Static structure good; runtime behavior not |
| Flutter app | ⭐⭐ | Dart supported; widget tree less useful |
| Rapid prototype | ⭐⭐ | Brief discipline adds friction at this stage |
| Static site | ⭐ | Minimal dependencies — low graph value |
| Single-file script | ⭐ | No graph structure to analyze |

**Rule of thumb:** GraphStack pays off when your codebase exceeds ~20 files and queries regularly cross module boundaries.

---

## Comparison

| | GraphStack | gstack | loki-mode | code-review-graph |
|---|---|---|---|---|
| Knowledge graph | ✅ Graphify | ❌ | ❌ | ✅ |
| Auto role transitions | ✅ | ❌ manual | ✅ complex | ❌ |
| Bootstrap (0→project) | ✅ | ❌ | ❌ | ❌ |
| Git-native task board | ✅ GNAP | ❌ | ❌ | ❌ |
| Session resumability | ✅ STATE.md | ❌ | ❌ | ❌ |
| Token optimization rules | ✅ explicit | ❌ | ❌ | ✅ partial |
| Setup complexity | Low | Low | High | Low |

---

## Resuming a Session

```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
Resume from last session.
```

Orchestrator reads `handoff/STATE.md` and `handoff/board/doing/` and picks up exactly where it left off.

---

## All Prompts

### Standard session
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
[What you want to build or fix — any language]
```

### New project from scratch
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
This is a new project with no existing codebase.
I want to build [describe your idea].
Tech stack: [language, framework, database].
```

### Resume a previous session
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
Resume from last session.
```

### Manual role activation (advanced)

Use these when you want a single role without the full lifecycle:

**Architect** — plan and scope only, no building
```
Read .cursor/skills/architect/ARCHITECT.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
[What you want to plan]
```

**Builder** — build directly from an existing brief
```
Read .cursor/skills/builder/BUILDER.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
Brief is in handoff/BRIEF.md. Start building.
```

**Reviewer** — review existing code or a diff
```
Read .cursor/skills/reviewer/REVIEWER.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
Review the changes in [filename or "the last git diff"].
```

**QA** — trace and verify a specific feature
```
Read .cursor/skills/qa/QA.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
Trace and verify [feature name].
```

**Ship** — run pre-deploy checklist
```
Read .cursor/skills/ship/SHIP.md and follow it exactly.
Run the pre-ship checklist for task [task-id].
```

**Bootstrapper** — decompose an idea into a module plan only
```
Read .cursor/skills/bootstrapper/BOOTSTRAPPER.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
[Describe your project idea]
```

> **Note:** `.cursor/rules/graphstack.mdc` is loaded automatically by Cursor on every session. You never need to reference it manually.

---

## Compatibility

| Tool | Orchestrator | Manual roles |
|------|-------------|-------------|
| Cursor | ✅ Full (.mdc auto-loads) | ✅ |
| Claude Code | ✅ Full | ✅ |
| VS Code Copilot Chat | ✅ Full | ✅ |
| GitHub Copilot CLI | ⚠️ Paste per session | ✅ |
| Aider | ⚠️ Paste per session | ✅ |

---

## Demo

[`demo/DEMO_WALKTHROUGH.md`](demo/DEMO_WALKTHROUGH.md) — full end-to-end walkthrough: adding rate limiting to a Node.js auth service, showing every automatic transition, graph query, and board update.

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). GraphStack is just markdown and bash — the barrier is intentionally low.

---

## License

MIT — free forever. No telemetry. No accounts. No phoning home.
