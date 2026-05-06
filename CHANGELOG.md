# Changelog

All notable changes to GraphStack are documented here.

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
