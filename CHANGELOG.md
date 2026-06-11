# Changelog

All notable changes to GraphStack are documented here.

---

## [v4.3.0] — 2026-06-11

### Added
- **`graphstack gate`** — deterministic process enforcement: `gate check` (CI/manual), `gate hook cursor`, `gate hook claude`. Rules: deny code commits/edits when no board task is in `doing/`, or when `BRIEF.md` is still the template. Fail-open on hook errors; bypass via `GRAPHSTACK_GATE=off` or `handoff/.gate-off`.
- **`graphstack state`** — machine-readable `handoff/STATE.json` (`set` / `get` / `clear`) for hook verification and resume.
- **Hook adapters** — `.cursor/hooks.json` (Cursor 3.x, `version: 1`) and `.claude/settings.json` (Claude Code `PreToolUse` + `Stop`). Installer writes OS-specific commands (`gate-hook.ps1` on Windows, `gate-hook.sh` on Unix).
- **`scripts/gate-hook.sh` / `scripts/gate-hook.ps1`** — portable shims (resolve `py -3` / `python3` / `python` without hardcoding).
- **`.graphstack-framework` marker** — `validate` warns when the framework repo ships dirty handoff state (non-template brief, `done/` tasks, active `STATE.md` entries).
- **Pytest** — `test_gate.py` (26 tests), `test_state.py` (5 tests).

### Changed
- **ORCHESTRATOR** — token tier detail moved to `TOKEN_OPTIMIZER.md` (reference only); state persistence now includes `state set`.
- **BUILDER** — removed duplicate user confirmation at activation (Orchestrator brief confirmation is the single human gate); activation now runs `state set` and builds immediately.
- **ARCHITECT / BUILDER** — token rules condensed to pointers to `TOKEN_OPTIMIZER.md`.
- **CI** — `graphstack gate check` step; required-files manifest includes gate modules and hook shims.
- **README** — Process Gate section; Limitations updated.

### Fixed
- **Windows hook launcher** — hooks no longer hardcode `python` (often missing on Windows); shims prefer `py -3`.

---

## [v4.2.0] — 2026-05-17

### Added
- **`graphstack run`** — run shell commands with token-safe output compaction (`--raw` for full output).
- **`scripts/graphstack/compact/`** — independent compactors for `git status` / `diff` / `log`, `pytest`, and generic commands; preserves paths, hunks, and failures; falls back to raw when signal would be lost.
- **Workflow integration** — `TOKEN_OPTIMIZER.md`, `graphstack.mdc`, `ORCHESTRATOR.md`, Builder/QA skills mandate `graphstack run` for shell tools.
- **`validate` / `doctor`** — `compact_ok` check for the output-compact module.
- **Pytest** — `test_compact.py` (7 tests for compaction quality).

### Changed
- **Installer** — copies `run.py` and `scripts/graphstack/compact/` into target projects.
- **README** — Shell Output Compaction section and v4.2 highlights.

---

## [v4.1.0] — 2026-05-17

### Added
- **`pyproject.toml`** — install GraphStack with `pip install -e .`; console script `graphstack` points at `graphstack.cli:main`.
- **`graphstack validate`** — LLM-free checks for handoff layout, board task JSON, `STATE.md`, and graph commit vs `git HEAD` (`--fail-stale-graph` for CI).
- **`graphstack doctor`** — human-readable health report (same checks as validate; warnings do not fail by default).
- **`.graphifyignore`** — code-focused graph profile for the GraphStack source repo (reduces markdown noise in `graphify-out/`).
- **`docs/case-studies/graphstack-self.md`** — honest self-analysis: graph quality on a meta-repo, token savings confidence levels, validation workflow.
- **README Limitations** section — orchestrator enforcement, token estimates, graph ROI, setup steps.
- **Pytest** — 6 new tests in `test_validate.py` (29 total in suite).

### Changed
- **CI** — `pip install -e .` before tests; `graphstack validate --fail-stale-graph` step; `pyproject.toml` and `validate.py` in required-files manifest.
- **Installer** — copies `validate.py` into target projects with the Python package.

### Fixed
- **Graph staleness check** — `validate --fail-stale-graph` accepts `HEAD~1` when the graph was built before a dedicated graph-artifacts commit (common release workflow).
- **CI validate job** — `actions/checkout` uses `fetch-depth: 2`; validate steps use `python -m graphstack`; CI runs `graphify update .` before `--fail-stale-graph` (graph built on an older commit than HEAD no longer fails shallow clones).

---

## [v4.0.0] — 2026-05-16

GraphStack v4 is the **cross-platform release**. Windows runs natively in PowerShell (no Git Bash needed), macOS runs without `coreutils`, and the entire workflow logic lives in a single Python package. The `skills/` directory was unified with the post-install `.cursor/skills/` layout so the source repo and an installed project look identical.

### Added
- **Python core package** — `scripts/graphstack/` (single source of truth):
  - `cli.py` dispatcher (`python -m graphstack <board|install|hook>`)
  - `board.py` — full GNAP lifecycle (status / new / claim / complete / log)
  - `installer.py` — non-destructive installer with `--non-interactive` flag
  - `hook.py` — smart graph-update post-commit logic
  - `platform_utils.py` — Python detection, encoding-safe `echo`, git wrappers
  - `constants.py` — single place for board / graphify-out paths
- **PowerShell shims**: `install.ps1`, `scripts/board.ps1`, `scripts/post-commit.ps1` — Windows-native, no Git Bash dependency.
- **Pytest suite** — 23 tests covering board lifecycle, installer layout, hook logic, platform detection, encoding fallbacks. Runs on all three OSes via CI matrix.
- **Tri-OS CI matrix** — `.github/workflows/ci.yml` now validates on Ubuntu + macOS + Windows in parallel. Bash syntax is checked once on Linux; Python module + native shim smoke tests run on every OS.
- **Markdown lint job** — broken relative-link detection across all `.md` files.
- **`requirements.txt`** — pins `graphifyy>=0.7,<0.9` so an upstream breaking release does not silently break GraphStack.
- **`.gitkeep` files** — `handoff/board/doing/` and `handoff/board/done/` are now tracked so cloned repos start with a complete directory structure.
- **OS dropdown + Python/Graphify version fields** in `bug_report.yml` for faster triage.

### Changed
- **Single-layout source repo** — `skills/` was moved to `.cursor/skills/`. The source repo now mirrors the installed layout exactly. Cursor working on the GraphStack source itself sees the same paths an end user would.
- **Bash scripts → thin shims** — `install.sh`, `scripts/board.sh`, `scripts/post-commit` are now 5–15 line delegators that locate Python and exec the package. All real logic lives in Python.
- **Role files use cross-platform commands** — `bash scripts/board.sh ...` was replaced with `python -m graphstack board ...` in `ARCHITECT.md`, `BUILDER.md`, `REVIEWER.md`, `QA.md`, `SHIP.md`, `BOOTSTRAPPER.md`, `ORCHESTRATOR.md`, and `DEMO_WALKTHROUGH.md`.
- **`ORCHESTRATOR.md` path references** — internal references like `skills/bootstrapper/BOOTSTRAPPER.md` were corrected to `.cursor/skills/bootstrapper/BOOTSTRAPPER.md` (and equivalents for builder / ship). Architect, builder, reviewer, QA, and ship references are now all explicit.
- **`STATE.md` template** — the example session block is now wrapped in an HTML comment so the orchestrator no longer mistakes it for a real session entry.
- **Graphify command syntax** — three places that used `/graphify . --update` were standardised to `/graphify --update`.
- **README + CURSOR_PROMPTS** — three install paths documented (bash / PowerShell / cross-platform Python). Windows section no longer references Git Bash as a prerequisite.

### Fixed
- **macOS `realpath` portability** — installer no longer depends on GNU coreutils. `pathlib.Path.resolve()` works on a stock macOS install.
- **Windows Microsoft Store stub** — PowerShell shims detect the WindowsApps redirect stub and fall back to `py -3` automatically.
- **First-commit hook crash** — post-commit hook now guards against missing `HEAD~1` on a fresh repo instead of failing the commit.
- **cp1254 / Turkish locale crashes** — stdout is reconfigured to UTF-8 with replacement; box-drawing characters in the board status header are plain ASCII.
- **Bash `((count++))` exit-code workaround** — replaced with proper Python integer counters in board status.
- **JSON Unicode round-trip** — board task files now serialize with `ensure_ascii=False`, so Turkish / non-Latin titles are preserved verbatim.

### Migration from v3.0.0
- Existing `handoff/board/*.json` task files are forward-compatible — schema is unchanged.
- `bash scripts/board.sh ...` shim still works; only its body changed.
- If you have local edits in the old `skills/` directory, replay them against `.cursor/skills/`. Everything else is non-breaking.

---

## [v3.0.0] — 2026-05-06

### Added
- **Bootstrap Mode** — `skills/bootstrapper/BOOTSTRAPPER.md`: new role that turns a raw idea or PRD into a structured multi-cycle build plan. Enables GraphStack to be used from day zero on a new project.
- **`handoff/BOOTSTRAP.md`** — persistent cross-cycle memory: module map, dependency order, tech stack decisions, cross-cutting concerns, cycle log.
- **GNAP Board** — `handoff/board/` + `scripts/board.sh`: git-native task coordination with `todo/` → `doing/` → `done/` lifecycle. Every transition creates a git commit for full audit trail.
- **Orchestrator** — `orchestrator/ORCHESTRATOR.md`: central state machine that manages all role transitions automatically. Users write one prompt; Orchestrator drives the full lifecycle.
- **Token Optimizer** — `orchestrator/TOKEN_OPTIMIZER.md`: explicit 4-tier token budget system enforced across all roles. Includes graph query patterns, parallel read protocol, output compression rules.
- **Session State** — `handoff/STATE.md`: persistent session state enables resuming across Cursor restarts with zero re-reading.
- **Smart Graph Update** — `scripts/post-commit`: graph updates only on structural changes (files added/deleted), Ship commits, or 24h staleness. Eliminates unnecessary updates on content-only edits.
- **Cycle-end Graph Update** — Ship role now always assesses and runs graph update at end of each cycle. Bootstrapper gets fresh graph before writing each new brief.
- **GitHub files** — `LICENSE` (MIT), `.gitignore`, `CONTRIBUTING.md`, `CHANGELOG.md`, `.github/workflows/`.

### Changed
- **Reviewer activation**: no longer blocks waiting for user to specify files. In Orchestrator mode, reads brief's "In Scope" list directly.
- **QA activation**: no longer waits for user confirmation before tracing. Announces plan and proceeds.
- **Builder activation**: handles 0/1/2+ matching board tasks explicitly instead of ambiguous "find matching task" instruction.
- **Install script**: now creates `docs/` directory (was missing, causing `cp` failure), always creates `STATE.md`, copies `BOOTSTRAP.md` template.
- **Orchestrator activation**: 3-mode detection (Normal / Bootstrap / New Project) with explicit fallbacks on every file read.

### Fixed
- `board.sh`: `set -euo pipefail` + `((count++))` arithmetic exit-code crash. Changed to `set -uo pipefail`.
- `board.sh new`: titles with spaces were truncated to first word. Fixed with `shift 2; title="${*}"`.
- `board.sh new`: global `role="${3}"` conflicted with per-command argument parsing. Removed global role variable.
- `.cursor/rules/graphstack.mdc`: was labeled v2, now correctly labeled v3.
- `CURSOR_PROMPTS.md`: was v1-style (manual role prompts only). Rewritten as Orchestrator-first with single-prompt workflow.

---

## [v2.0.0] — 2026-05-05

### Added
- Orchestrator (initial version) with automatic role transitions
- Token optimization layer with 4-tier budget system
- STATE.md session persistence
- Demo project (Node.js auth service with walkthrough)

### Changed
- All roles updated to work in both Orchestrator and manual modes

---

## [v1.0.0] — 2026-05-04

### Added
- Initial release: Architect, Builder, Reviewer, QA, Ship roles
- Graphify integration (graph-first reads)
- Cursor `.mdc` always-active rules
- `install.sh` single-command setup
