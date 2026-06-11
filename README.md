<div align="center">

# GraphStack 🧠⚡

**Graph-first, automatically orchestrated AI development workflow.**  
One prompt starts the entire lifecycle — from blank repo to production.

[![CI](https://github.com/MertCapkin/graphstack/actions/workflows/ci.yml/badge.svg)](https://github.com/MertCapkin/graphstack/actions)
[![PyPI](https://img.shields.io/pypi/v/MertCapkin_GraphStack)](https://pypi.org/project/MertCapkin_GraphStack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-success)](#compatibility)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-blue)](https://cursor.sh)
[![Works with Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-orange)](https://claude.ai/code)

</div>

> **v4.5 highlights:** Published on [PyPI](https://pypi.org/project/MertCapkin_GraphStack/) as **`MertCapkin_GraphStack`**, one-command bootstrap, `board reopen` / `list-done`. Plus v4.4 `graph query` + `init`, v4.3 gate. See [CHANGELOG.md](CHANGELOG.md).

---

## One command (Cursor terminal)

Open your **project folder** in Cursor, open the integrated terminal, and run:

**Windows (PowerShell) — recommended:**
```powershell
irm https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.ps1 | iex
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.sh | bash
```

**Or install from PyPI directly:**

> Package: **`MertCapkin_GraphStack`** on [PyPI](https://pypi.org/project/MertCapkin_GraphStack/) (`graphstack` name was taken). CLI command: **`graphstack`**.

```bash
pip install "MertCapkin_GraphStack[graphify]"
graphstack init . -y --install-deps
```

This installs GraphStack + Graphify, copies workflow files into **the current project**, refreshes the code graph, and runs `doctor`. Then describe your task in Cursor chat — rules load automatically.

---

## Quick Start

### Step 1 — Install GraphStack (PyPI)

**Python 3.8+** and **Git** are required.

```bash
py -3 --version
git --version
```

Install GraphStack + Graphify from PyPI, then initialize **your project** (run inside your project folder):

```bash
pip install "MertCapkin_GraphStack[graphify]"
graphstack init . -y --install-deps
```

Or use the [one-command bootstrap](#one-command-cursor-terminal) above (same result; installs from PyPI, falls back to GitHub if needed).

Verify:

```bash
graphstack --version
graphstack doctor
pip show graphifyy
```

> **PyPI:** [pypi.org/project/MertCapkin_GraphStack](https://pypi.org/project/MertCapkin_GraphStack/)  
> **CLI name:** `graphstack` (unchanged — only the pip package name differs)

Graphify runs **entirely locally** — tree-sitter AST, no API calls for code graphs.

---

### Step 1 (alternative) — Manual Graphify only

If you prefer to install Graphify separately first:

```bash
pip install "graphifyy>=0.7,<0.9"
graphify cursor install
pip install "MertCapkin_GraphStack[graphify]"
graphstack init . -y --install-deps
```

---

### Step 2 — Install from source (contributors / offline)

For hacking on GraphStack itself or air-gapped installs, clone the repo instead of PyPI:

```bash
git clone https://github.com/MertCapkin/graphstack /tmp/graphstack
cd /path/to/your-project
bash /tmp/graphstack/install.sh
# or, equivalently:
# python3 -m graphstack install . --no-interactive
```

#### Windows (PowerShell — native, no Git Bash needed)

```powershell
git clone https://github.com/MertCapkin/graphstack $env:TEMP\graphstack
cd C:\path\to\your-project
& $env:TEMP\graphstack\install.ps1 .
```

If `python.exe` on Windows redirects you to the Microsoft Store, the installer detects that and falls back to the official `py -3` launcher automatically.

#### Any platform (Python, no shell preference)

```bash
git clone https://github.com/MertCapkin/graphstack /path/to/graphstack
cd /path/to/your-project
python -m graphstack install . --non-interactive
```

This copies all GraphStack files into your project:
- `.cursor/rules/graphstack.mdc` — Cursor loads this automatically on every session
- `orchestrator/`, `.cursor/skills/`, `handoff/`, `scripts/` — the full workflow system
- `scripts/graphstack/` — the Python helper package (used by both the bash and PowerShell shims)

The install script is non-destructive: it won't overwrite existing `handoff/BRIEF.md`, `handoff/REVIEW.md`, or `handoff/BOOTSTRAP.md` if they already exist.

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

**New project with no code yet?** Skip this step — GraphStack's Bootstrap Mode handles it.

**Already ran `graphstack init --install-deps`?** You have a code-only graph in `graphify-out/`; run `/graphify .` in Cursor for the full semantic graph when ready.

---

### Step 4 — Start working

The repo ships two ways to bootstrap the orchestrator — pick whichever feels natural.

#### A) Easiest — new chat only (recommended)

Because `.cursor/rules/graphstack.mdc` is **`alwaysApply: true`**, every new Composer / Agent
session already carries GraphStack’s binding rules. Simply open chat and describe your goal in
natural language (`Add …`, `Fix …`). The assistant’s first turn must still **execute**
`orchestrator/ORCHESTRATOR.md → Activation** (parallel `TOKEN_OPTIMIZER` + `GRAPH_REPORT`),
but **you don’t paste** `Read orchestrator/...` anymore.

#### B) Slash command `/graphstack` (explicit nudge)

In Cursor Chat/Composer press `/` → choose **`graphstack`**. That injects the Bootstrap command
stored in `.cursor/commands/graphstack.md` (helps when you want deterministic orchestrator wording
or onboarding teammates).

*If `/graphstack` doesn't appear immediately, restart Cursor once so it rescans `.cursor/commands/`.*

#### C) Classic explicit prompt (fallback / other tools)

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

Step 2 — every session (minimal typing):
  Open Composer + describe the task (rules already activate GraphStack automatically),
  optionally type `/graphstack` once for an explicit orchestrator preamble,
  or paste the legacy `Read orchestrator/ORCHESTRATOR.md …` snippet if working outside Cursor.

Example natural-language kickoff:
  "Add rate limiting to login."

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
Composer (Cursor):
  Describe the product + tech stack naturally (alwaysApply rules bootstrap GraphStack),
  optionally `/graphstack` beforehand to inject the scripted opener.

Bootstrap example:
"/graphstack then: New project REST API for task mgmt — TS, Express, PostgreSQL."

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
| Shell compaction | `graphstack run` shrinks git/test output before it hits context | ~60–80% on verbose shell ops |

**Net savings by codebase size:**

| Codebase | Tokens/day without | Tokens/day with | Saving |
|----------|--------------------|-----------------|--------|
| Small (10–20 files) | ~40k | ~28k | **~30%** |
| Medium (50–100 files) | ~180k | ~54k | **~70%** |
| Large (200+ files) | ~600k | ~90k | **~85%** |
| Very large (500+ files) | ~1.5M | ~180k | **~88%** |

*Estimates based on Graphify benchmarks and TOKEN_OPTIMIZER rules. Real savings depend on query patterns. See [docs/case-studies/graphstack-self.md](docs/case-studies/graphstack-self.md) for an honest self-analysis — measured community benchmarks are welcome via PR.*

---

## Limitations (read before adopting)

GraphStack is a **workflow protocol** (markdown + handoff files), not a runtime that enforces AI behavior.

| Topic | Reality |
|-------|---------|
| Role automation | Prompts alone cannot guarantee discipline. v4.3+ **`graphstack gate`** + v4.4 Cursor **`preToolUse`**. Hooks block commits and (on Cursor/Claude) code writes without a claimed task; `afterFileEdit` on Cursor remains advisory-only backup. |
| Token savings | The table above is **estimated**, not guaranteed. Small repos or undisciplined sessions may use **more** tokens than unstructured chat. |
| Knowledge graph | Value appears on **20+ file** codebases with module boundaries. Meta-repos full of markdown produce noisy graphs — use `.graphifyignore` (included in this repo). |
| Setup | Graphify + `pip install MertCapkin_GraphStack` + `graphstack init` — or one bootstrap command. See [PyPI](https://pypi.org/project/MertCapkin_GraphStack/). |

**v4.1 helpers:** `graphstack doctor` (health report) and `graphstack validate` (exit code for CI). Use `--strict` before Builder handoff; use `--fail-stale-graph` in CI after code changes.

```bash
graphstack doctor
graphstack validate
graphstack validate --strict --fail-stale-graph
```

---

## Shell Output Compaction (`graphstack run`)

Graph-first rules reduce **file reads**. Shell compaction reduces **terminal output** (git status, diffs, test runners) before it enters the AI context — without installing third-party proxies.

**Who uses it:** Cursor/Claude agents follow `TOKEN_OPTIMIZER.md` and `.cursor/rules/graphstack.mdc` — they call `graphstack run`, not raw `git`/`pytest`. You do not need to remember a separate workflow.

```bash
python -m graphstack run -- git status
python -m graphstack run -- git diff
python -m graphstack run -- git log -n 20
python -m graphstack run -- pytest -q
```

**Quality safeguards (not “blind compression”):**

- File paths, branch names, diff hunks (`@@`), and `+`/`-` lines are preserved
- Test failures, tracebacks, and stderr are kept (stderr is never compacted)
- If compaction would drop too much signal, output **falls back to raw** automatically
- Full output when debugging: `python -m graphstack run --raw -- git diff`

Independent Python implementation (MIT) — inspired by common agent-tooling patterns, no RTK dependency or vendored code.

`graphstack doctor` reports whether the compact module is installed in your project.

---

## Graph Queries (`graphstack graph`)

Graph-first rules mean **query the graph before opening raw files**. v4.4 wraps Graphify's CLI so agents use one consistent command:

```bash
python -m graphstack graph query "who calls login"
python -m graphstack graph query "blast radius of crypto.ts" --budget 1500
python -m graphstack graph path src/auth/login.ts src/utils/crypto.ts
python -m graphstack graph explain "login()"
python -m graphstack graph update .     # AST-only refresh after code changes
```

Requires `graphify` on PATH (`pip install -r requirements.txt`). Agents should prefer `graph query` over reading full `GRAPH_REPORT.md` or grepping source for structural questions.

---

## Process Gate (`graphstack gate`)

v4.3+ adds **mechanical enforcement** so Architect → Builder → Reviewer steps are harder to skip silently. v4.4 extends Cursor with `preToolUse` blocking.

| Rule | What it blocks | Cursor | Claude Code |
|------|----------------|--------|-------------|
| R1 | `git commit` touching code while `doing/` is empty | deny (`beforeShellExecution` + `preToolUse` Shell) | deny (`PreToolUse` Bash) |
| R2 | Edit/Write on code paths while `doing/` is empty | deny (`preToolUse` Write/Edit) | deny (`PreToolUse` Edit/Write) |
| R3 | Commit while `BRIEF.md` is still the template | deny | deny |
| R4 | `STATE.json` not updated this cycle | advisory (`stop`) | advisory (`Stop`) |
| — | Edit already applied (legacy hook) | advisory only (`afterFileEdit`) | — |

```bash
python -m graphstack gate check          # CI / manual — exit 1 on violation
python -m graphstack state set --role builder --task my-feature
GRAPHSTACK_GATE=off                      # emergency bypass (one session)
GRAPHSTACK_GATE=strict                   # fail-closed on hook internal errors
```

**Install** writes `.cursor/hooks.json` and `.claude/settings.json` with OS-specific shim commands (`scripts/gate-hook.ps1` on Windows, `scripts/gate-hook.sh` on macOS/Linux). By default hooks **fail open** if Python is missing — use `GRAPHSTACK_GATE=strict` for teams that prefer blocking over availability.

> **Framework repo note:** This GitHub repo ships `handoff/` as **templates** (empty brief, no `done/` tasks). Your installed project fills those files during real work. Before contributing here, reset handoff — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## What Gets Installed

```
your-project/
├── .cursor/rules/graphstack.mdc          ← always-active rules (Cursor auto-loads)
├── .cursor/commands/graphstack.md        ← `/graphstack` Cursor slash-command bootstrapper
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
│   ├── board.sh                          ← GNAP board shim (bash)
│   ├── board.ps1                         ← GNAP board shim (PowerShell)
│   ├── post-commit                       ← smart graph-update hook (bash)
│   ├── post-commit.ps1                   ← smart graph-update hook (PowerShell)
│   └── graphstack/                       ← Python core (single source of truth)
│       ├── board.py                      ← GNAP board logic
│       ├── installer.py                  ← project installer logic
│       ├── hook.py                       ← post-commit graph-update logic
│       ├── platform_utils.py             ← OS detection, Python finder, encoding-safe echo
│       ├── cli.py                        ← entry point dispatcher
│       ├── validate.py                   ← layout / brief / graph checks
│       ├── run.py                        ← shell runner with compaction
│       ├── compact/                      ← git / pytest / generic compactors
│       └── tests/                        ← pytest suite
├── pyproject.toml                        ← pip install -e . (v4.1+)
├── .graphifyignore                       ← code-focused graph for this repo
```

---

## The GNAP Board

GraphStack uses Git-Native Agent Protocol for task tracking — no server, no database, just files and git commits.

All three forms below are equivalent. Pick whichever fits your shell.

#### macOS / Linux (bash)

```bash
bash scripts/board.sh status
bash scripts/board.sh new add-oauth Add OAuth login with GitHub
bash scripts/board.sh claim add-oauth builder
bash scripts/board.sh complete add-oauth
bash scripts/board.sh log
```

#### Windows (PowerShell)

```powershell
.\scripts\board.ps1 status
.\scripts\board.ps1 new add-oauth Add OAuth login with GitHub
.\scripts\board.ps1 claim add-oauth builder
.\scripts\board.ps1 complete add-oauth
.\scripts\board.ps1 log
```

#### Cross-platform (any shell with Python)

```bash
python -m graphstack board status
python -m graphstack board new add-oauth Add OAuth login with GitHub
python -m graphstack board claim add-oauth builder
python -m graphstack board complete add-oauth
python -m graphstack board log
python -m graphstack run -- git status
python -m graphstack doctor
python -m graphstack validate --fail-stale-graph
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
| Cursor `/graphstack` slash bootstrap | ✅ | ❌ | ❌ | ❌ |
| Setup complexity | Low | Low | High | Low |

---

## Resuming a Session

Default (Cursor Composer with GraphStack repo open): reopen chat and paste a short cue such as `"Resume GraphStack STATE.md"` or select `/graphstack` followed by `"Resume"` — Activation still runs tokens + graph loaders automatically.

Classic explicit prompt:

```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
Resume from last session.
```

Orchestrator reads `handoff/STATE.md` and `handoff/board/doing/` and picks up exactly where it left off.

---

## All Prompts

**Quick path:** describe work directly (rules + optional `/graphstack`). Legacy blocks remain for deterministic copy/paste workflows or non‑Cursor tooling.

### Standard session *(legacy explicit)*
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
[What you want to build or fix — any language]
```

### New project from scratch *(legacy explicit)*
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
This is a new project with no existing codebase.
I want to build [describe your idea].
Tech stack: [language, framework, database].
```

### Resume a previous session *(legacy explicit)*
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
