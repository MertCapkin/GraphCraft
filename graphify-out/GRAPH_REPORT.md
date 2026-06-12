# Graph Report - graphstack  (2026-06-12)

## Corpus Check
- 66 files · ~26,052 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 953 nodes · 1873 edges · 69 communities (58 shown, 11 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1b8d8f80`
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
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]

## God Nodes (most connected - your core abstractions)
1. `echo()` - 44 edges
2. `run_checks()` - 26 edges
3. `main()` - 21 edges
4. `hook_cursor()` - 21 edges
5. `MonkeyPatch` - 20 edges
6. `CaptureFixture` - 19 edges
7. `run_git()` - 18 edges
8. `Report` - 18 edges
9. `GraphStack 🧠⚡` - 18 edges
10. `compact_command_output()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `run_doctor()`  [INFERRED]
  scripts/graphstack/cli.py → scripts/graphstack/validate.py
- `main()` --calls--> `run_validate()`  [INFERRED]
  scripts/graphstack/cli.py → scripts/graphstack/validate.py
- `CompactResult` --uses--> `CompactResult`  [INFERRED]
  scripts/graphstack/compact/registry.py → scripts/graphstack/compact/base.py
- `_brief_is_unwritten()` --calls--> `_brief_is_template()`  [INFERRED]
  scripts/graphstack/gate.py → scripts/graphstack/validate.py
- `_changed_files()` --calls--> `git_available()`  [INFERRED]
  scripts/graphstack/gate.py → scripts/graphstack/platform_utils.py

## Import Cycles
- None detected.

## Communities (69 total, 11 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (45): _ask_yes_no(), _build_parser(), _claude_settings_payload(), _copy_if_exists(), _cursor_hooks_payload(), _ensure_state_md(), _gate_hook_command(), _hook_command_key() (+37 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (61): git_available(), _brief_is_template(), _brief_status(), _build_parser(), check_board_tasks(), check_brief(), check_compact_module(), check_framework_handoff() (+53 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (39): CompactResult, dedupe_consecutive(), is_critical_line(), Shared helpers for safe output compaction., Keep critical lines and a head/tail window; return (lines, omitted_count)., Return compacted text unless it lost too much signal vs raw., safe_compact(), truncate_preserving_critical() (+31 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (42): Always prefer:, "Are there tests for this?", Bootstrap Mode Graph Schedule, code:block1 (SESSION BUDGET), code:block10 (read([src/auth/login.ts, src/auth/session.ts])  // one tool ), code:block11 ("Context at ~80% capacity. Summarizing intermediate state to), code:block12 (TRIGGER 1 — Structural change (highest priority)), code:bash (# Force update now (run in Cursor or terminal)) (+34 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (59): Exception, True when the latest ## section in REVIEW.md contains Verdict: Approved., review_last_verdict_approved(), _brief_is_unwritten(), _changed_files(), _code_edit_checks(), _commit_candidate_files(), _commit_strict_checks() (+51 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (50): CaptureFixture, MonkeyPatch, Path, _enable_builder_edits(), _feed_stdin(), _gate_enabled(), _hook_output(), _make_doing_task() (+42 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (74): CompletedProcess, _build_parser(), cmd_claim(), cmd_complete(), cmd_list_done(), cmd_log(), cmd_new(), cmd_reopen() (+66 more)

### Community 7 - "Community 7"
Cohesion: 0.20
Nodes (10): Adım 1 — GraphStack'i projeye yükle, Adım 2 — Graphify'ı yükle ve grafiği oluştur, Adım 3 — Başla, code:bash (git clone https://github.com/MertCapkin/graphstack /tmp/grap), code:powershell (git clone https://github.com/MertCapkin/graphstack $env:TEMP), code:bash (git clone https://github.com/MertCapkin/graphstack /path/to/), code:bash (pip install -r requirements.txt), code:block5 (/graphify .) (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (13): Activation, code:block1 (1a. Parallel read (once per session — same tool batch if bot), code:block15 (After Cycle 1 Ship:), code:bash (python -m graphstack board new <task-id> "<title>"), code:block2 (┌──────────────┐), code:block20 (1. Read handoff/STATE.md (last entry only)), GNAP Board Rules, Graphify Schedule (Bootstrap Mode) (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (16): code:block12 (You:  "Add rate limiting to login."), code:block13 (Step 1 — once:), code:block15 (your-project/), Comparison, Compatibility, Contributing, Demo, Graph Update Strategy (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (27): code:bash (# 1. Install GraphStack into the demo project), code:block10 (Updating src/api/types.ts — adding RATE_LIMITED error code.), code:typescript (error?: "USER_NOT_FOUND" | "INVALID_PASSWORD" | "SESSION_ERR), code:block12 ([BUILDER → REVIEWER]), code:block13 ([REVIEWER MODE]), code:block14 ([QA MODE]), code:block15 ([SHIP MODE]), code:bash (# Clone and install) (+19 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (17): ARCHITECT → BUILDER, BOOTSTRAPPER → BUILDER (cycle 1), code:block11 ([REVIEWER → QA]), code:block12 ([QA → BUILDER]), code:block13 ([QA → SHIP]), code:block14 ([SHIP → IDLE]), code:block3 ([BOOTSTRAPPER MODE]), code:block4 ([BOOTSTRAPPER → BUILDER]) (+9 more)

### Community 12 - "Community 12"
Cohesion: 0.22
Nodes (9): code:bash (py -3 --version   # need 3.8 or higher), code:bash (pip install -r requirements.txt), code:bash (graphify cursor install), code:bash (pip show graphifyy), code:bash (pip install --user "graphifyy>=0.7,<0.9"), code:block9 (/graphify .), Quick Start, Step 1 — Install prerequisites (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.14
Nodes (17): All Prompts, code:block20 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block21 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block22 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block23 (Read .cursor/skills/architect/ARCHITECT.md and follow it exa), code:block24 (Read .cursor/skills/builder/BUILDER.md and follow it exactly), code:block25 (Read .cursor/skills/reviewer/REVIEWER.md and follow it exact), code:block26 (Read .cursor/skills/qa/QA.md and follow it exactly.) (+9 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (15): Added, Added, Added, Added, Changed, Changed, Changed, Changelog (+7 more)

### Community 15 - "Community 15"
Cohesion: 0.14
Nodes (13): 1. Improve a role instruction file, 2. Add a new role, 3. Improve the board script, 4. Add a demo, 5. Write a case study, 6. Cursor slash-command bootstrap snippets, Contributing to GraphStack, License (+5 more)

### Community 16 - "Community 16"
Cohesion: 0.08
Nodes (40): brief_is_draft(), brief_is_ready_for_builder(), brief_is_template(), brief_status(), Shared handoff/BRIEF/REVIEW helpers for gate, validate, and cycle., Update **Status:** line in BRIEF.md. Returns False if file missing., read_brief_text(), set_brief_status() (+32 more)

### Community 17 - "Community 17"
Cohesion: 0.27
Nodes (18): CaptureFixture, Path, Round-trip tests for the GNAP board lifecycle., _read(), test_claim_already_doing_is_idempotent(), test_claim_missing_task_returns_error(), test_complete_already_done_is_idempotent(), test_full_lifecycle_todo_to_done() (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.19
Nodes (14): Credentials, LoginResult, User, login(), logout(), createSession(), destroySession(), Session (+6 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (9): Bootstrap Plan: [Project Name], code:block1 ([Project Name]), Cross-Cutting Concerns, Cycle Log, Cycle Sequence, Known Risks, Module Map, Project Summary (+1 more)

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (9): Acceptance Criteria, Brief: [Feature/Change Name], Graph Context, Handoff Note, Implementation Hints, In Scope, Objective, Out of Scope (+1 more)

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (10): CaptureFixture, MonkeyPatch, Tests for graphstack graph (graphify wrapper)., test_graph_help_lists_subcommands(), test_graph_path_delegates(), test_graph_query_delegates(), test_graph_unknown_command(), test_graph_update_delegates() (+2 more)

### Community 22 - "Community 22"
Cohesion: 0.33
Nodes (10): CaptureFixture, MonkeyPatch, Tests for the OS helpers in ``platform_utils``., test_echo_never_raises_on_unprintable(), test_emoji_safe_downgrades_on_legacy_encoding(), test_emoji_safe_passthrough_on_utf(), test_find_python_falls_back_to_sys_executable(), test_find_python_prefers_python3_when_available() (+2 more)

### Community 23 - "Community 23"
Cohesion: 0.27
Nodes (10): CaptureFixture, MonkeyPatch, Path, Tests for the post-commit graph-update logic., When ``HEAD~1`` cannot be resolved, structural count must be 0., Files inside graphify-out/ or handoff/ never trigger an update by themselves., test_excludes_generated_paths_from_structural_count(), test_no_graph_returns_zero_and_warns() (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.44
Nodes (8): CaptureFixture, Path, Tests for the machine-readable session state (handoff/STATE.json)., test_clear_is_idempotent(), test_get_without_state_returns_error(), test_load_state_handles_corrupt_json(), test_set_then_get_round_trips(), test_unknown_role_still_writes_with_warning()

### Community 25 - "Community 25"
Cohesion: 0.31
Nodes (7): MonkeyPatch, Path, _disable_git_in_tests(), project_root(), Shared pytest fixtures for the graphstack package., Provide an isolated, writable directory and chdir into it.      All board oper, Prevent any board command from creating real git commits during tests.

### Community 26 - "Community 26"
Cohesion: 0.33
Nodes (5): code:block1 (board/), GraphStack GNAP Board, How It Works, Task File Format, Why Git?

### Community 27 - "Community 27"
Cohesion: 0.47
Nodes (7): MonkeyPatch, Path, Tests for graphstack init (install + graph + doctor bootstrap)., test_init_propagates_install_failure(), test_init_runs_install_graph_and_doctor(), test_init_skips_graph_when_requested(), test_init_succeeds_when_doctor_fails_but_layout_ok()

### Community 28 - "Community 28"
Cohesion: 0.48
Nodes (5): MonkeyPatch, Path, Smoke test for the installer — confirms a clean install creates expected paths., test_install_creates_full_layout(), test_install_does_not_overwrite_existing_brief()

### Community 30 - "Community 30"
Cohesion: 0.14
Nodes (13): Activation Sequence, BOOTSTRAP.md Format, Bootstrapper Decision Rules, BOOTSTRAPPER Role, Handoff Between Cycles, How to Decompose a Project, Per-Cycle Brief Format, Step 1 — Identify modules (+5 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (11): Activation, Build Sequence, BUILDER Role, File Reading Rules, Graph Usage (Builder-Specific), Handoff to Reviewer, Scope Creep Detection, Shell Commands (Builder) (+3 more)

### Community 37 - "Community 37"
Cohesion: 0.24
Nodes (11): Architect (planlama), Builder (doğrudan build), code:block14 (Read .cursor/skills/architect/ARCHITECT.md and follow it exa), code:block16 (Read .cursor/skills/reviewer/REVIEWER.md and follow it exact), code:block18 (Read .cursor/skills/ship/SHIP.md and follow it exactly.), 🎭 Manuel Rol Aktivasyonu (İleri Düzey), 🎭 Manuel Rol Aktivasyonu (İleri Düzey), QA (davranış doğrulama) (+3 more)

### Community 38 - "Community 38"
Cohesion: 0.18
Nodes (10): Activation, Graph Usage (Reviewer-Specific), If Approved:, If Rejected:, Review Checklist, Reviewer Decision Rules, REVIEWER Role, Token Rules (Reviewer) (+2 more)

### Community 39 - "Community 39"
Cohesion: 0.20
Nodes (9): Activation, Architect Decision Rules, ARCHITECT Role, Graph Usage (Architect-Specific), Handoff to Builder, Receiving Back from Reviewer, Token Rules (Architect), Writing the Brief (+1 more)

### Community 40 - "Community 40"
Cohesion: 0.20
Nodes (9): Adım 1 — GraphStack'i projeye yükle, Adım 2 — Graphify'ı yükle ve grafiği oluştur, Adım 3 — Başla, 🔧 Cursor'a Kurulum (İlk Kez), 📋 Cycle + Board (Terminal), GraphStack v4.6 — Cursor Prompts & Setup Guide, 💡 İpuçları, 🚀 Sıfırdan Yeni Proje (Bootstrap Modu) (+1 more)

### Community 41 - "Community 41"
Cohesion: 0.27
Nodes (9): code:block10 (Boş bir repo için REST API yazıyorum: kullanıcılar proje olu), code:block7 (Kayıtta e-posta doğrulaması eklemek istiyorum.), code:block8 (Login endpoint çok yavaş — performansı bul ve düzelt.), code:block9 (Resume from last session.), GraphStack v4 — Cursor Prompts & Setup Guide, ⚡ Normal Kullanım — Tek Prompt, 💡 İpuçları, ⚡ Örnek hedef yazıları (klasik bloğu atlarsan bile) (+1 more)

### Community 42 - "Community 42"
Cohesion: 0.20
Nodes (9): Activation, Graph Usage (QA-Specific), QA Decision Rules, QA Role, QA Verification Process, Shell Commands (QA), Token Rules (QA), Writing the QA Report (+1 more)

### Community 43 - "Community 43"
Cohesion: 0.29
Nodes (7): Any platform (Python, no shell preference), code:bash (git clone https://github.com/MertCapkin/graphstack /tmp/grap), code:powershell (git clone https://github.com/MertCapkin/graphstack $env:TEMP), code:bash (git clone https://github.com/MertCapkin/graphstack /path/to/), macOS / Linux (bash / zsh), Step 2 — Install GraphStack into your project, Windows (PowerShell — native, no Git Bash needed)

### Community 44 - "Community 44"
Cohesion: 0.29
Nodes (7): code:bash (bash scripts/board.sh status), code:powershell (.\scripts\board.ps1 status), code:bash (python -m graphstack board status), Cross-platform (any shell with Python), macOS / Linux (bash), The GNAP Board, Windows (PowerShell)

### Community 45 - "Community 45"
Cohesion: 0.29
Nodes (7): Before every file read, ask internally:, code:block16 (Is this in Tier 1 or 2?  → Proceed), Tier 1 — Free (always do first), Tier 2 — Cheap (use freely), Tier 3 — Expensive (require justification), Tier 4 — Banned, Token Budget System

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (6): Activation, Commit Message, Graph Update (Every Cycle End — Mandatory), Pre-Ship Checklist, SHIP Role, Token Rules (Ship)

### Community 47 - "Community 47"
Cohesion: 0.33
Nodes (6): 📋 Board Komutları (Terminal), code:block17 (Read .cursor/skills/qa/QA.md and follow it exactly.), code:bash (bash scripts/board.sh status), code:powershell (.\scripts\board.ps1 status), code:bash (python -m graphstack board status), QA (davranış doğrulama)

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (6): Builder (doğrudan build), code:block11 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block12 (Önceki GraphStack oturumundan devam et.), code:block13 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block15 (Read .cursor/skills/builder/BUILDER.md and follow it exactly), 🔄 Oturum Devam Ettirme

### Community 49 - "Community 49"
Cohesion: 0.47
Nodes (6): A) Easiest — new chat only (recommended), B) Slash command `/graphstack` (explicit nudge), C) Classic explicit prompt (fallback / other tools), code:block10 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), code:block11 (Read orchestrator/ORCHESTRATOR.md and follow it exactly.), Step 4 — Start working

### Community 50 - "Community 50"
Cohesion: 0.33
Nodes (6): code:block21 ([ARCHITECT MODE]), code:block22 ([BUILDER MODE]), code:block23 ([REVIEWER MODE]), code:block24 ([QA MODE]), code:block25 ([SHIP MODE]), Output Format Per Role

### Community 51 - "Community 51"
Cohesion: 0.67
Nodes (4): Install-GraphstackPackage(), Invoke-GraphstackPython(), Test-GraphstackCli(), Test-WheelAssets()

### Community 52 - "Community 52"
Cohesion: 0.47
Nodes (5): Path, Tests for graphstack cycle commands., test_cycle_start_creates_task_and_architect_state(), test_enter_builder_claims_task(), test_enter_builder_requires_ready_brief()

### Community 53 - "Community 53"
Cohesion: 0.50
Nodes (4): Path, _latest_wheel(), PyPI wheel must ship ``.cursor`` workflow files inside ``graphstack/assets``., test_wheel_includes_cursor_assets()

### Community 58 - "Community 58"
Cohesion: 0.67
Nodes (3): code:block10 ("This change has been revised 3 times. Here are the persiste), code:block9 ([REVIEWER → BUILDER]), REVIEWER → BUILDER (rejection path)

### Community 59 - "Community 59"
Cohesion: 0.67
Nodes (3): code:markdown (## [YYYY-MM-DD HH:MM] — [ROLE] → [NEXT_ROLE]), code:bash (# On role claim:), State Persistence

## Knowledge Gaps
- **243 isolated node(s):** `User`, `Session`, `sessions`, `gate-hook.sh script`, `PYTHONPATH` (+238 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `echo()` connect `Community 6` to `Community 16`, `Community 0`, `Community 4`, `Community 1`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `run()` connect `Community 2` to `Community 16`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 16` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `echo()` (e.g. with `cmd_claim()` and `cmd_complete()`) actually correct?**
  _`echo()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `run_checks()` (e.g. with `test_graph_fresh_when_built_commit_is_ancestor_of_head()` and `test_graph_fresh_when_built_from_parent_commit()`) actually correct?**
  _`run_checks()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `main()` (e.g. with `run_doctor()` and `run_validate()`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `User`, `Session`, `sessions` to the rest of the system?**
  _342 weakly-connected nodes found - possible documentation gaps or missing edges._