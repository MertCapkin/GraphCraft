# GraphCraft v0.1.0 — Mobile platform foundation

## Added
- GraphCraft Python package (`graphcraft` CLI) as layer on GraphStack
- Design graph: tokens, components, screens, styles, stitch import
- Commands: `design update|query|validate|harmony`, `stitch import|report`
- Style pack template (`minimal-dark`)
- Mobile app/game stack packs and Cursor skills
- Aesthetic + design handoff templates
- Optional Stitch prototype import (`.stitch/`)

## v0.1.1 — Docs & overlay clarity
- README.md is GraphCraft-only; GraphStack documented as dependency (`docs/GRAPHSTACK.md`)
- Orchestrator overlay documented (`docs/FLOW.md`, `docs/ARCHITECTURE.md`)
- `graphcraft.mdc` primary greeting + design routing (GraphStack unchanged)
- GraphCraft PyPI assets no longer bundle GraphStack files

## Dependencies
- MertCapkin_GraphStack[graphify] >=4.7,<5
- PyYAML (design YAML parsing)
