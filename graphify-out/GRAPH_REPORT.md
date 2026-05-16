# Graph Report - graphstack  (2026-05-16)

## Corpus Check
- 34 files · ~14,994 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 420 nodes · 484 edges · 29 communities (25 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `98922cfc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]

## God Nodes (most connected - your core abstractions)
1. `GraphStack 🧠⚡` - 18 edges
2. `echo()` - 16 edges
3. `ORCHESTRATOR` - 12 edges
4. `Transition Rules` - 12 edges
5. `Token Optimizer` - 11 edges
6. `run_git()` - 9 edges
7. `GraphStack v4 — Cursor Prompts & Setup Guide` - 9 edges
8. `run_hook()` - 8 edges
9. `install()` - 8 edges
10. `All Prompts` - 8 edges

## Surprising Connections (you probably didn't know these)
- `_git_commit_board()` --calls--> `run_git()`  [INFERRED]
  scripts/graphstack/board.py → scripts/graphstack/platform_utils.py
- `cmd_log()` --calls--> `run_git()`  [INFERRED]
  scripts/graphstack/board.py → scripts/graphstack/platform_utils.py
- `_do_update()` --calls--> `echo()`  [INFERRED]
  scripts/graphstack/hook.py → scripts/graphstack/platform_utils.py
- `run_hook()` --calls--> `echo()`  [INFERRED]
  scripts/graphstack/hook.py → scripts/graphstack/platform_utils.py
- `run_hook()` --calls--> `file_mtime_seconds()`  [INFERRED]
  scripts/graphstack/hook.py → scripts/graphstack/platform_utils.py

## Communities (29 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (38): Adım 1 — GraphStack'i projeye yükle, Adım 2 — Graphify'ı yükle ve grafiği oluştur, Adım 3 — Başla, Architect (planlama), 📋 Board Komutları (Terminal), Builder (doğrudan build), code:bash (git clone https://github.com/MertCapkin/graphstack /tmp/grap), code:block10 (Boş bir repo için REST API yazıyorum: kullanıcılar proje olu) (+30 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (31): _build_parser(), cmd_claim(), cmd_complete(), cmd_log(), cmd_new(), cmd_status(), _get(), _git_commit_board() (+23 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (29): Activation, Before every file read, ask internally:, code:block1 (1a. Parallel read (once per session — same tool batch if bot), code:block15 (After Cycle 1 Ship:), code:block16 (Is this in Tier 1 or 2?  → Proceed), code:markdown (## [YYYY-MM-DD HH:MM] — [ROLE] → [NEXT_ROLE]), code:bash (# On role claim:), code:bash (python -m graphstack board new <task-id> "<title>") (+21 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (29): Always prefer:, Bootstrap Mode Graph Schedule, code:block1 (SESSION BUDGET), code:block10 (read([src/auth/login.ts, src/auth/session.ts])  // one tool ), code:block11 ("Context at ~80% capacity. Summarizing intermediate state to), code:block12 (TRIGGER 1 — Structural change (highest priority)), code:bash (# Force update now (run in Cursor or terminal)), code:block14 (Cycle 1 → Ship → STOP → "Run /graphify . now" → wait for con) (+21 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (24): Path and configuration constants used across the package.  Paths are resolved, _build_parser(), _do_update(), _has_previous_commit(), _last_commit_message(), _modified_count(), Smart graph-update logic — pure Python port of ``scripts/post-commit``.  Trigg, ``HEAD~1`` exists only after at least 2 commits — guard for first commit. (+16 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (27): Bootstrap Mode — Start from Zero, code:block12 (You:  "Add rate limiting to login."), code:block13 (Step 1 — once:), code:block14 (Composer (Cursor):), code:block15 (your-project/), code:bash (bash scripts/board.sh status), code:powershell (.\scripts\board.ps1 status), code:bash (python -m graphstack board status) (+19 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (27): code:bash (# 1. Install GraphStack into the demo project), code:block10 (Updating src/api/types.ts — adding RATE_LIMITED error code.), code:typescript (error?: "USER_NOT_FOUND" | "INVALID_PASSWORD" | "SESSION_ERR), code:block12 ([BUILDER → REVIEWER]), code:block13 ([REVIEWER MODE]), code:block14 ([QA MODE]), code:block15 ([SHIP MODE]), code:bash (# Clone and install) (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (24): ARCHITECT → BUILDER, BOOTSTRAPPER → BUILDER (cycle 1), BUILDER → REVIEWER, code:block10 ("This change has been revised 3 times. Here are the persiste), code:block11 ([REVIEWER → QA]), code:block12 ([QA → BUILDER]), code:block13 ([QA → SHIP]), code:block14 ([SHIP → IDLE]) (+16 more)

### Community 8 - "Community 8"
Cohesion: 0.1
Nodes (22): A) Easiest — new chat only (recommended), Any platform (Python, no shell preference), B) Slash command `/graphstack` (explicit nudge), C) Classic explicit prompt (fallback / other tools), code:bash (py -3 --version   # need 3.8 or higher), code:block10 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block11 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:bash (pip install -r requirements.txt) (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.14
Nodes (17): All Prompts, code:block20 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block21 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block22 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block23 (Read .cursor/skills/architect/ARCHITECT.md and follow it exa), code:block24 (Read .cursor/skills/builder/BUILDER.md and follow it exactly), code:block25 (Read .cursor/skills/reviewer/REVIEWER.md and follow it exact), code:block26 (Read .cursor/skills/qa/QA.md and follow it exactly.) (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (15): Added, Added, Added, Added, Changed, Changed, Changed, Changelog (+7 more)

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (13): 1. Improve a role instruction file, 2. Add a new role, 3. Improve the board script, 4. Add a demo, 5. Write a case study, 6. Cursor slash-command bootstrap snippets, Contributing to GraphStack, License (+5 more)

### Community 12 - "Community 12"
Cohesion: 0.19
Nodes (5): Round-trip tests for the GNAP board lifecycle., _read(), test_full_lifecycle_todo_to_done(), test_new_task_creates_file(), test_unicode_title_is_preserved()

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (13): "Are there tests for this?", code:block3 (graph.json → node["src/auth/login.ts"].edges.filter(e => e.t), code:block4 (graph.json → nodes.filter(n => n.edges.some(e => e.target ==), code:block5 (GRAPH_REPORT.md → cluster section → find cluster containing ), code:block6 (graph.json → BFS from node X, depth 2, outgoing edges only), code:block7 (graph.json → node["src/auth/login.ts"].edges.filter(e => e.t), code:block8 (GRAPH_REPORT.md → patterns section), Graph Query Patterns (+5 more)

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (5): login(), createSession(), comparePassword(), generateToken(), hashPassword()

### Community 15 - "Community 15"
Cohesion: 0.2
Nodes (9): Bootstrap Plan: [Project Name], code:block1 ([Project Name]), Cross-Cutting Concerns, Cycle Log, Cycle Sequence, Known Risks, Module Map, Project Summary (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.2
Nodes (9): Acceptance Criteria, Brief: [Feature/Change Name], Graph Context, Handoff Note, Implementation Hints, In Scope, Objective, Out of Scope (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.25
Nodes (6): _build_parser(), main(), Top-level CLI dispatcher.  Three sub-commands: - ``board``     — GNAP task bo, Entry point for both ``python -m graphstack`` and unit tests., GraphStack — cross-platform Python core.  This package replaces the bash/Power, Allow ``python -m graphstack`` to invoke the CLI.

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (5): Tests for the post-commit graph-update logic., When ``HEAD~1`` cannot be resolved, structural count must be 0., Files inside graphify-out/ or handoff/ never trigger an update by themselves., test_excludes_generated_paths_from_structural_count(), test_no_previous_commit_skips_structural_diff()

### Community 20 - "Community 20"
Cohesion: 0.33
Nodes (5): _disable_git_in_tests(), project_root(), Shared pytest fixtures for the graphstack package., Provide an isolated, writable directory and chdir into it.      All board oper, Prevent any board command from creating real git commits during tests.

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (5): code:block1 (board/), GraphStack GNAP Board, How It Works, Task File Format, Why Git?

## Knowledge Gaps
- **186 isolated node(s):** `GNAP board manager — pure Python port of ``scripts/board.sh``.  JSON schema is`, `Stage the board directory and commit silently — never fails the command.`, `Top-level CLI dispatcher.  Three sub-commands: - ``board``     — GNAP task bo`, `Entry point for both ``python -m graphstack`` and unit tests.`, `Path and configuration constants used across the package.  Paths are resolved` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GraphStack 🧠⚡` connect `Community 5` to `Community 8`, `Community 9`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Quick Start` connect `Community 8` to `Community 5`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `ORCHESTRATOR` connect `Community 2` to `Community 7`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `echo()` (e.g. with `_print_task()` and `cmd_status()`) actually correct?**
  _`echo()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `GNAP board manager — pure Python port of ``scripts/board.sh``.  JSON schema is`, `Stage the board directory and commit silently — never fails the command.`, `Top-level CLI dispatcher.  Three sub-commands: - ``board``     — GNAP task bo` to the rest of the system?**
  _186 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._