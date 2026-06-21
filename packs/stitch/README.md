# Stitch Pack

Optional prototype import from [Google Stitch](https://stitch.withgoogle.com/).

## Setup

1. `design_source: stitch` or `hybrid` in graphcraft.config.yaml
2. Export Stitch project → `.stitch/`
3. `graphcraft stitch import .`

## Files

- `.stitch/DESIGN.md` — Stitch design system (official format)
- `.stitch/metadata.json` — screen map + flows
- `.stitch/designs/*.png` — visual ground truth

## Docs

- [DESIGN.md spec](https://github.com/google-labs-code/design.md)
- Stitch MCP: `@keeponfirst/kof-stitch-mcp`
