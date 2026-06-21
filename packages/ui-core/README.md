# UI Core Library

Shared UI primitives consumed by mobile app/game implementations.

## Structure (expand per cycle)

```
ui-core/
├── tokens/          # re-export from design-system
├── rn/
├── flutter/
├── swiftui/
├── compose/
└── unity/
```

## Rules

- No hardcoded colors — use semantic tokens
- Each component maps to design graph `component:*` id
- Register new components in `design-system/components/*.yaml`

v0.1: scaffold only — implement stack modules in future cycles.
