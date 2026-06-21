# UI Core Library

Shared UI primitives mapped to the GraphCraft design graph.

## Stacks

| Stack | Path | Status |
|-------|------|--------|
| React Native | [rn/](rn/) | v0.5+ |
| Flutter | [flutter/](flutter/) | v0.6+ |
| Unity UGUI | [unity/](unity/) | v0.6+ |
| Godot 4 | [godot/](godot/) | v0.6+ |

## CLI

```bash
graphcraft ui tokens emit rn|flutter|unity|godot
graphcraft ui validate all
```

## Rules

- No hardcoded colors — use stack token file (emit from `design-system/tokens.json`)
- Each component: `@graphcraft component:<id>` marker in source
- Each screen: `@graphcraft implements screen:<id>`
- Register components in `design-system/components/*.yaml`
