# Contributing to GraphStack

GraphStack is a **workflow system** backed by a small Python CLI (`scripts/graphstack/`).
Most files are instruction markdown for AI roles; the Python package provides board,
validate, gate, graph query wrappers, and cross-platform install.

---

## What GraphStack Is (and Isn't)

GraphStack combines:
- **Instruction files** an AI reads (`.cursor/skills/`, `orchestrator/`)
- **Handoff files** humans and agents share (`handoff/`)
- **Python CLI** — `pip install -e .` then `python -m graphstack …`

There is no Node build step. Python 3.8+ and pytest are required to run tests.

---

## Ways to Contribute

### 1. Improve a role instruction file

Found a better way to phrase a token rule? A clearer transition condition? A missing edge case in the Reviewer checklist?

Edit the relevant file in `.cursor/skills/` or `orchestrator/` and open a PR. Describe what behavior you changed and why.

### 2. Add a new role

If you think GraphStack is missing a role (e.g., a Security Auditor, a Performance Profiler, a Documentation Writer), propose it:

1. Open an issue describing the role's job, inputs, outputs, and when it activates
2. Get feedback before writing the file
3. Once approved: add `.cursor/skills/<rolename>/<ROLENAME>.md`, update `ORCHESTRATOR.md` with the transition rule, add a prompt to `docs/CURSOR_PROMPTS.md`, and register the new path in `scripts/graphstack/installer.py`'s `FILE_COPIES`.

### 3. Improve the board / CLI

Board logic lives in `scripts/graphstack/board.py` (Python). Shell shims (`board.sh`, `board.ps1`) delegate to it.

For new CLI commands: add a module under `scripts/graphstack/`, register in `cli.py`, copy list in `installer.py`'s `PYTHON_PACKAGE_FILES`, and add tests in `scripts/graphstack/tests/`.

### 4. Add a demo

The `demo/` folder shows GraphStack in action on a Node.js auth service. More demos welcome:
- Different language (Python, Go, Rust...)
- Different project type (CLI, data pipeline, mobile backend...)
- Different scenario (bug fix, refactor, bootstrap from scratch...)

### 5. Write a case study

Used GraphStack on a real project? Measured token savings? Wrote about it?
Open a PR adding a `docs/case-studies/<name>.md` entry (see `docs/case-studies/graphstack-self.md` for the template style) or link to your post in the README.

### 6. Cursor slash-command bootstrap snippets

Markdown files inside `.cursor/commands/` register under Cursor Composer’s **`/`** slash menu.
When you introduce a copy change, restart Cursor once locally (and mention that in README) so teammates see the refreshed entry. Keep installers + CI manifests in sync via `installer.py`'s `FILE_COPIES` and `.github/workflows/ci.yml`.

---

## Framework repo: reset `handoff/` before release commits

This repository **is** GraphStack (marker: `.graphstack-framework`). The `handoff/` folder ships as **empty templates** for projects that run `install.sh` — not as a log of our own development cycles.

Before pushing framework changes to GitHub:

1. Restore `handoff/BRIEF.md`, `handoff/REVIEW.md`, and `handoff/STATE.md` to their templates (no real task content).
2. Remove any `handoff/board/done/*.json` and `handoff/STATE.json`.
3. Run `python -m graphstack validate` — warnings `framework_*` should be zero.

Consumer projects keep their handoff history; only this source repo resets.

---

## Pull Request Guidelines

- **One PR per change.** Don't bundle unrelated edits.
- **Explain the behavior change**, not just what you edited.
- **Test the CLI** if you touch `scripts/graphstack/`: `pytest scripts/graphstack/tests -q`
- **Test the board** if you touch board commands: run `new → claim → complete → status`
- **Keep role files under 300 lines.** If yours is longer, it's doing too much.
- **No new runtime dependencies.** The `graphstack` package uses only the Python stdlib. Optional: `graphifyy` for graph commands.

---

## Opening Issues

Good issues include:
- **What you expected** the system to do
- **What it actually did** (paste the AI output if relevant)
- **Which file** you think the problem is in
- **Which AI tool** you were using (Cursor, Claude Code, etc.)

---

## Philosophy

GraphStack is opinionated about one thing: **structure beats improvisation**. Every role has a job. Every transition has a trigger. Every token spent should have a justification.

When evaluating changes, the question is: does this make the system more structured and predictable, or does it add flexibility that makes the system less reliable?

Reliability wins.

---

## License

By contributing, you agree your contributions are licensed under the MIT License.
