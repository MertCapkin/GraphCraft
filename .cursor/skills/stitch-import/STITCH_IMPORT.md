# STITCH IMPORT Skill

Import Google Stitch prototypes into GraphCraft design graph.

## When

`graphcraft.config.yaml` → `design_source: stitch|hybrid`

## Steps

1. Export from Stitch: DESIGN.md + screens → `.stitch/designs/` (PNG/HTML)
2. Copy/fill `.stitch/metadata.json` from `metadata.template.json`
3. `python -m graphcraft stitch import .`
4. `python -m graphcraft stitch report`
5. Curator approves screens in design specs

## MCP (optional)

Configure `@keeponfirst/kof-stitch-mcp` for automated fetch.

## Rules

- `.stitch/` is read-only reference after import
- Refinements go in `design/screens/` (hybrid mode)
- Visual ground truth = PNG files
