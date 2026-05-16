# Token Optimizer

GraphStack's token optimization layer. These rules are enforced across ALL roles.

---

## The Core Principle

> The graph is a compression of your codebase.  
> Reading the graph = reading the codebase, at 1/10th the cost.  
> Every raw file read that the graph could have answered is waste.

---

## Session Budget Tracker

At session start, initialize mentally:

```
SESSION BUDGET
──────────────
Graph reads:    1 allowed (GRAPH_REPORT.md) — FREE
Brief reads:    1 allowed (BRIEF.md) — FREE  
Raw file reads: track each one
Re-reads:       0 allowed
Speculative:    0 allowed
```

---

## Decision Tree (Run Before Every Tool Call)

```
Before reading a file:
  ├─ Is it GRAPH_REPORT.md?
  │   ├─ Already read this session? → SKIP (use context)
  │   └─ Not yet read? → READ (Tier 1, free)
  │
  ├─ Is it in handoff/BRIEF.md's file list?
  │   └─ YES → READ (Tier 2, justified)
  │
  ├─ Can graph.json answer this question?
  │   ├─ YES → QUERY GRAPH (Tier 1, free)
  │   └─ NO → continue...
  │
  ├─ Is this file already in my context window?
  │   └─ YES → SKIP (use context — re-read is banned)
  │
  ├─ Do I need the WHOLE file or just one function?
  │   ├─ One function → READ TARGETED SECTION ONLY (Tier 2)
  │   └─ Whole file → JUSTIFY FIRST
  │       └─ Can I get away with the graph summary? → try graph first
  │
  └─ Is this a "just to be sure" read?
      └─ YES → CANCEL (speculative reads banned)
```

---

## Graph Query Patterns

These answer common questions WITHOUT reading files:

### "What does this module import?"
```
graph.json → node["src/auth/login.ts"].edges.filter(e => e.type === "imports")
```

### "Who calls this function?"
```
graph.json → nodes.filter(n => n.edges.some(e => e.target === "login" && e.type === "calls"))
```

### "What modules are in this cluster?"
```
GRAPH_REPORT.md → cluster section → find cluster containing target
```

### "What's the blast radius of changing X?"
```
graph.json → BFS from node X, depth 2, outgoing edges only
```

### "Are there tests for this?"
```
graph.json → node["src/auth/login.ts"].edges.filter(e => e.type === "tested_by")
```

### "What pattern does the codebase use for Y?"
```
GRAPH_REPORT.md → patterns section
graph.json → find 3 nodes in same cluster as Y → read ONE as example
```

---

## Parallel Read Protocol

When 2+ files must be read, NEVER read sequentially.

**Wrong (2x cost):**
```
read(src/auth/login.ts)
read(src/auth/session.ts)
```

**Right (1x cost):**
```
read([src/auth/login.ts, src/auth/session.ts])  // one tool call
```

Rule: If you know you need N files, request all N in one call.

---

## Output Compression Rules

### Never produce these:
- Restatement of user's request ("You want me to add a login feature...")
- Transition announcements over 2 lines ("Now I will switch to the Builder role and begin implementing...")
- Ellipsis thinking ("Let me think about this...")
- Excessive role headers (one short `[ROLE MODE]` tag is enough)
- Full file contents when a diff is sufficient
- Full function when a summary is sufficient

### Always prefer:
- Diffs over full files
- Summaries over full reads
- One-line status over paragraphs
- Tables over bullet lists for comparisons
- "✓" / "✗" over "passed" / "failed"

---

## Context Window Rules

### What stays in context (never re-read):
- GRAPH_REPORT.md content
- BRIEF.md content  
- Any file read this session

### What gets summarized out (to free context):
- Intermediate reasoning
- Rejected alternatives
- Verbose error messages (summarize to one line)

### When context is getting full:
```
"Context at ~80% capacity. Summarizing intermediate state to handoff/STATE.md.
 Continuing from current role."
```

---

## Estimated Token Savings by Pattern

| Old Pattern | New Pattern | Savings |
|-------------|-------------|---------|
| Read 10 files to understand architecture | Read GRAPH_REPORT.md | ~85% |
| Re-read file already in context | Use existing context | 100% |
| Sequential file reads | Parallel reads | ~50% |
| Full file read for one function | Targeted section read | ~70% |
| Speculative read "just in case" | Query graph first | ~90% |
| Chat history for state | STATE.md file | ~60% per new session |

---

## Graph Update Strategy

### When to Update (Smart Triggers)

The post-commit hook enforces these rules automatically. Manually apply the same logic:

```
TRIGGER 1 — Structural change (highest priority)
  Any file added or deleted (outside graphify-out/ and handoff/)
  → Always update, immediately
  → Reason: new nodes or missing nodes break graph queries

TRIGGER 2 — Ship completed
  A cycle or feature just shipped
  → Always update after Ship role completes
  → Reason: the next Architect/Bootstrapper reads this graph

TRIGGER 3 — Staleness
  graph.json is >24 hours old
  → Update at start of next session
  → Reason: accumulated small changes may have shifted architecture

NOT A TRIGGER — Content edits only
  Modifying existing functions, fixing bugs, updating tests
  → Do NOT update graph unless 24h threshold reached
  → Reason: graph topology unchanged; existing queries still valid
```

### Why Not Update Every Commit?

Graphify runs locally (tree-sitter, no API calls) so it has no token cost. But:

1. **Time cost** — update takes 5-30 seconds on large repos
2. **Noise cost** — frequent graph commits clutter git history
3. **Diminishing returns** — a bug fix in an existing function doesn't change who imports what

**The graph represents structure, not content.** Content changes don't require a new graph.

### Manual Update Commands

```bash
# Force update now (run in Cursor or terminal)
/graphify --update

# Check graph age
ls -la graphify-out/GRAPH_REPORT.md

# See what changed since last graph update
git diff $(git log --all --oneline -- graphify-out/graph.json | head -1 | cut -d' ' -f1) -- src/
```

### Bootstrap Mode Graph Schedule

During Bootstrap cycles, the Orchestrator enforces this manually:

```
Cycle 1 → Ship → STOP → "Run /graphify . now" → wait for confirmation → Cycle 2 brief
Cycle N → Ship → STOP → "Run /graphify --update now" → wait → Cycle N+1 brief
```

Never skip this step in bootstrap mode. The next brief depends on the real graph.

---

## Project Type Suitability

GraphStack token savings scale with **codebase complexity and query frequency**.

```
High value (>60% savings):
  ✅ REST/GraphQL APIs        ✅ Data pipelines
  ✅ Monolithic web apps      ✅ Libraries/SDKs
  ✅ Game backends            ✅ CLI tools (medium+)
  ✅ Microservices            ✅ Admin panels

Medium value (30-60% savings):
  🟡 React/Vue SPAs           🟡 Mobile apps (React Native)
  🟡 Unity games (C#)         🟡 TypeScript monorepos
  🟡 Serverless functions     🟡 E-commerce backends

Low value (<30% savings):
  🔴 Static sites             🔴 Single-file scripts
  🔴 Jupyter notebooks        🔴 Rapid prototypes (<20 files)
  🔴 Godot (GDScript)         🔴 Flutter (widget-heavy)

The threshold: GraphStack pays off when your codebase exceeds ~20 files
and queries regularly cross module boundaries.
```

```
❌ Reading GRAPH_REPORT.md more than once per session
❌ Reading a file to "explore" without a specific question
❌ Asking the user a question you could answer from the graph
❌ Reading all files in a directory to find the right one
   (use graph.json node lookup instead)
❌ Producing a plan before reading the graph
❌ Re-reading a file because you forgot its contents
   (summarize key facts to STATE.md before losing context)
❌ Writing code before checking graph dependencies
❌ Reviewing code without checking graph neighbors
```
