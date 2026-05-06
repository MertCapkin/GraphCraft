# Bootstrap Plan: [Project Name]

**Date:** YYYY-MM-DD
**Status:** Draft | Active | Complete
**Cycles completed:** 0 / [N]

---

## Project Summary

> 2-3 sentences: what it is, who uses it, core value.

---

## Tech Stack

- **Language:**
- **Runtime:**
- **Framework:**
- **Database:**
- **Testing:**
- **Key libraries:**

---

## Module Map

```
[Project Name]
├── [module-1]   → [what it does]
├── [module-2]   → [what it does]  (depends on 1)
├── [module-3]   → [what it does]  (depends on 1, 2)
└── [module-4]   → [what it does]  (depends on 1, 2, 3)
```

---

## Cycle Sequence

| Cycle | Module | Key files (estimated) | Depends on | Graph action | Status |
|-------|--------|-----------------------|------------|--------------|--------|
| 1 | | | — | `/graphify .` | ⬜ pending |
| 2 | | | cycle 1 | `/graphify --update` | ⬜ pending |
| 3 | | | cycles 1-2 | `/graphify --update` | ⬜ pending |

> Update Status: ⬜ pending → 🔄 in progress → ✅ complete

---

## Cross-Cutting Concerns

> Decided once, followed everywhere. Builder reads this every cycle.

- **Error handling:**
- **Logging:**
- **Config:**
- **Testing:**
- **Auth:**
- **Code style:**

---

## Known Risks

-

---

## Cycle Log

> Bootstrapper appends here after each cycle completes.

<!-- Cycle 1 — [date] — [brief summary of what was built] -->
