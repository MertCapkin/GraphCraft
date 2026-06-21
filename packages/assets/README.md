# Asset Library

Icons, sprites, fonts, audio UI cues.

## Manifest example

```yaml
id: assets:icons-minimal
style_compatibility:
  - style:minimal-dark
files:
  - path: home.svg
    tags: [navigation, 24px]
```

## Rules

- Link assets to components via design graph `uses_asset` edges
- Keep style compatibility in manifest
- Game sprites: separate atlas pipeline (future)

v0.1: scaffold — add asset sets per style pack in future cycles.
