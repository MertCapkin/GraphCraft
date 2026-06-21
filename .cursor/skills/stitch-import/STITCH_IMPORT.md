# STITCH IMPORT Skill

Import Google Stitch prototypes into GraphCraft design graph.

## When

`graphcraft.config.yaml` → `design_source: stitch|hybrid`

## Manual steps

1. Export from Stitch: DESIGN.md + screens → `.stitch/designs/` (PNG/HTML)
2. Copy/fill `.stitch/metadata.json` from `metadata.template.json`
3. `graphcraft stitch validate .`
4. `graphcraft stitch import .`
5. `graphcraft stitch report`
6. Curator approves screens in design specs

## MCP workflow (recommended)

1. Set `stitch.project_id` in `graphcraft.config.yaml` (Google Cloud project)
2. `graphcraft stitch mcp install` → merges `.mcp.json` for `@keeponfirst/kof-stitch-mcp`
3. `graphcraft stitch mcp doctor` — verify npx + GOOGLE_CLOUD_PROJECT
4. Authenticate: `gcloud auth application-default login`
5. In Cursor: use Stitch MCP tools to fetch/export designs
6. `graphcraft stitch fetch --export-dir /path/to/export` → copies into `.stitch/`
7. `graphcraft stitch import .`

Print-only config: `graphcraft stitch mcp print`

## Rules

- `.stitch/` is read-only reference after import
- Refinements go in `design/screens/` (hybrid mode)
- Visual ground truth = PNG files
