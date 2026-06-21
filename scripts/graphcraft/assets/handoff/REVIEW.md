# Review Log

> Append-only. Each role adds sections below (newest at top). Never delete history.
>
> | Role | Section heading | Required for gate |
> |------|-----------------|---------------------|
> | Builder | `## Builder Notes` | No |
> | Reviewer | `## Review: …` + `### Verdict:` | **Yes** — `Verdict: Approved` to enter QA / commit |
> | Reviewer | `## Loop count:` | No (max 3 Reviewer→Builder loops) |
> | Reviewer | `## Deferred debt` | No |
> | QA | `## QA Report:` + `### Overall:` | **Yes** — PASS or PARTIAL to ship |
> | QA | `## Escalation: Architect required` | No (Orchestrator returns to Architect) |
>
> Full write instructions: `.cursor/skills/reviewer/REVIEWER.md`, `qa/QA.md`, `builder/BUILDER.md`.

---

<!-- Cycle output is appended below, newest first. -->
