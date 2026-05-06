# Graph Report — demo-auth-app
**Generated:** 2026-05-04  
**Nodes:** 6 | **Edges:** 11 | **Clusters:** 3

---

## Clusters

### Cluster 1: Auth Core (high cohesion)
`src/auth/login.ts` · `src/auth/session.ts`

- login.ts is the **entry point** for all authentication flows
- session.ts is called exclusively by login.ts (single consumer)
- Both depend on crypto utils

### Cluster 2: Utilities
`src/utils/crypto.ts`

- **God node** ⚠️ — called by login.ts and session.ts
- No external dependencies (leaf node)
- Any change here has blast radius = entire auth cluster

### Cluster 3: API Layer
`src/api/types.ts` · `src/api/users.ts`

- types.ts: shared interfaces, no logic
- users.ts: data access layer, called by login.ts

---

## Dependency Graph

```
login.ts
  ├── imports → utils/crypto.ts (comparePassword)
  ├── imports → auth/session.ts (createSession)
  ├── imports → api/users.ts (findUserByEmail)
  └── imports → api/types.ts (LoginResult, Credentials)

session.ts
  └── imports → utils/crypto.ts (generateToken)

users.ts
  └── imports → api/types.ts (User)
```

---

## God Nodes (High Risk)

| Node | Degree | Consumers | Risk |
|------|--------|-----------|------|
| `src/utils/crypto.ts` | 4 | login.ts, session.ts | 🔴 High — changes break auth |
| `src/api/types.ts` | 3 | login.ts, users.ts, types | 🟡 Medium — interface changes break consumers |

---

## Knowledge Gaps

- `logout()` in login.ts is a TODO — not implemented
- No rate limiting visible in graph
- No refresh token flow
- Session storage is in-memory (Map) — not persistent across restarts

---

## Call Path: Login Flow

```
User → login(credentials)
  → findUserByEmail(email)         [api/users.ts]
  → comparePassword(pw, hash)      [utils/crypto.ts]
  → createSession(userId)          [auth/session.ts]
    → generateToken()              [utils/crypto.ts]
  → return { success, token }
```

---

## Patterns Found

- **Error handling:** Returns `{ success: false, error: "CODE" }` pattern (not thrown errors)
- **Async:** All functions are async/await, no callbacks
- **Types:** Strict TypeScript interfaces in api/types.ts
- **Crypto:** Node.js built-in crypto (no bcrypt/argon2)

---

## Test Coverage

| File | Has Tests |
|------|-----------|
| src/auth/login.ts | ❌ No |
| src/auth/session.ts | ❌ No |
| src/utils/crypto.ts | ❌ No |
| src/api/users.ts | ❌ No |

**Coverage: 0%** — no test files found.
