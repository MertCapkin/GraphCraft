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

<!-- Real cycle output is appended below, newest first. -->

<!--
  ──────────────────────────────────────────────────────────────────
  SECTION TEMPLATES (HTML comment — not a real review; copy when
  appending, then remove this comment wrapper from your paste).
  Gate parses the latest ## block containing Verdict: or QA Report:.
  ──────────────────────────────────────────────────────────────────

  ── BUILDER (optional, during build) ──

  ## Builder Notes — [YYYY-MM-DD]

  - [path/to/file]: [issue] — outside brief scope. Recommend follow-up cycle.


  ── REVIEWER — APPROVED ──

  ## Review: [Feature Name] — [YYYY-MM-DD] — ✅ APPROVED

  ### Verdict: Approved

  **Criteria met:** All [N] acceptance criteria verified.
  **Side effects checked:** [N] neighbor nodes inspected via graph, [M] raw reads max.
  **Tests:** Present and adequate.

  **Notes for next cycle:**
  - [Optional observations — not blocking]

  **Handoff:** Ready for QA.


  ── REVIEWER — REJECTED (increment Loop count each rejection) ──

  ## Loop count: [N]

  ## Review: [Feature Name] — [YYYY-MM-DD] — ❌ REJECTED

  ### Verdict: Rejected — Send back to Builder

  **Criteria status:** [M] of [N] met — failed: [numbers]; passed: [numbers]

  **Failed criteria:**
  - [ ] Criterion [N]: [what's wrong, what's expected]

  **Side effect risks:**
  - [file]: [risk, graph evidence]

  **Required fixes:**
  1. [Specific fix #1]
  2. [Specific fix #2]

  **Not required (defer):**
  - [Out-of-scope observations]

  **Handoff:** Return to Builder with these fixes only.


  ── REVIEWER — DEFERRED DEBT (with approval, non-blocking) ──

  ## Deferred debt — [YYYY-MM-DD]

  - [file:line]: [style/nit] — not blocking; optional follow-up task


  ── QA REPORT ──

  ## QA Report: [Feature Name] — [YYYY-MM-DD]

  ### Overall: ✅ PASS

  **Call path traced:**
  Entry: [node] → [node] → Output: [node]

  **Criteria results:**

  | Criterion | Result | Notes |
  |-----------|--------|-------|
  | Criterion 1 | ✅ PASS | [evidence] |

  **Integration points checked:**
  - [module A] ↔ [module B]: [result]

  **Boundary conditions:**
  - Empty input: [result]
  - Null/undefined: [result]

  **Flaky / concurrency candidates:**
  - [async/shared state — candidate only, not proven — or "None"]

  ### Recommendation
  Ship


  ── QA — FAIL / PARTIAL examples ──

  ### Overall: ❌ FAIL
  ### Overall: ⚠️ PARTIAL

  (Same table structure; gate accepts PASS or PARTIAL, blocks FAIL.)


  ── QA — ARCHITECT ESCALATION ──

  ## Escalation: Architect required

  **Reason:** [integration edge / scope mismatch / blast radius]
  **Evidence:** [graph path or QA trace]
  **Suggested action:** Revise brief or split cycle — do not patch blindly

  ──────────────────────────────────────────────────────────────────
-->
