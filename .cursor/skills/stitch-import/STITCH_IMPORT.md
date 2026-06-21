# STITCH IMPORT Skill

Import Google Stitch prototypes into GraphCraft design graph.

## When

`graphcraft.config.yaml` → `design_source: stitch|hybrid`

## One-command pull (recommended)

Uses official `@google/stitch-sdk` via Node (`npx`).

1. Get a Stitch API key from Google Stitch / AI Studio
2. Set environment variable:

```powershell
$env:STITCH_API_KEY = "your-key"
```

3. Set Stitch project id in `graphcraft.config.yaml`:

```yaml
stitch:
  enabled: true
  project_id: "4044680601076201931"   # numeric Stitch project id
```

4. Preflight:

```powershell
graphcraft stitch doctor .
```

5. Pull + import into design graph:

```powershell
graphcraft stitch pull . --force
```

Options: `--project-id`, `--html`, `--no-import`, `--skip-doctor`

OAuth alternative: `STITCH_ACCESS_TOKEN` + `GOOGLE_CLOUD_PROJECT` (no API key).

## Manual export workflow

1. Export from Stitch: DESIGN.md + screens → `.stitch/designs/` (PNG/HTML)
2. `graphcraft stitch fetch --export-dir /path/to/export`
3. `graphcraft stitch import .`

## MCP workflow (Cursor agent)

1. `graphcraft stitch mcp install` → `.mcp.json` for `@keeponfirst/kof-stitch-mcp`
2. `graphcraft stitch mcp doctor`
3. In Cursor: use Stitch MCP tools, then `graphcraft stitch fetch` or `pull`

Print-only MCP config: `graphcraft stitch mcp print`

## Rules

- `.stitch/` is read-only reference after import
- Refinements go in `design/screens/` (hybrid mode)
- Visual ground truth = PNG files
