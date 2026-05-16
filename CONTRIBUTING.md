# Contributing to GraphStack

GraphStack is intentionally simple: it's markdown files, a bash script, and a shell installer. The barrier to contribution is low by design.

---

## What GraphStack Is (and Isn't)

GraphStack is a **workflow system**, not a code library. Every file in this repo is either:
- An instruction file that an AI reads (`.md`)
- A shell script (`board.sh`, `install.sh`, `post-commit`)
- Documentation

There is no build step. No package.json. No dependencies to install to contribute.

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

### 3. Improve the board script

`scripts/board.sh` is pure bash + python3. If you find a bug or want to add a command (e.g., `board.sh reopen`, `board.sh list-done`), open a PR with:
- The change
- A manual test showing it works (paste the terminal output)

### 4. Add a demo

The `demo/` folder shows GraphStack in action on a Node.js auth service. More demos welcome:
- Different language (Python, Go, Rust...)
- Different project type (CLI, data pipeline, mobile backend...)
- Different scenario (bug fix, refactor, bootstrap from scratch...)

### 5. Write a case study

Used GraphStack on a real project? Measured token savings? Wrote about it?
Open a PR adding a `docs/case-studies/` entry or link to your post in the README.

### 6. Cursor slash-command bootstrap snippets

Markdown files inside `.cursor/commands/` register under Cursor Composer’s **`/`** slash menu.
When you introduce a copy change, restart Cursor once locally (and mention that in README) so teammates see the refreshed entry. Keep installers + CI manifests in sync via `installer.py`'s `FILE_COPIES` and `.github/workflows/ci.yml`.

---

## Pull Request Guidelines

- **One PR per change.** Don't bundle unrelated edits.
- **Explain the behavior change**, not just what you edited.
- **Test the board script** if you touch `board.sh`: run through `new → claim → complete → status` and paste the output.
- **Keep role files under 300 lines.** If yours is longer, it's doing too much.
- **No new dependencies.** GraphStack requires only bash + python3 + git. Keep it that way.

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
