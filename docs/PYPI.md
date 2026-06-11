# PyPI — MertCapkin_GraphStack

**Live:** https://pypi.org/project/MertCapkin_GraphStack/

| | |
|---|---|
| **Install** | `pip install MertCapkin_GraphStack[graphify]` |
| **CLI** | `graphstack` (command name unchanged) |
| **Why not `graphstack`?** | Name already taken on PyPI |

## User install (recommended)

Inside **your project folder** (Cursor terminal):

```powershell
# Windows — one command
irm https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.ps1 | iex
```

```bash
# macOS / Linux — one command
curl -fsSL https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.sh | bash
```

```bash
# Or PyPI directly
pip install "MertCapkin_GraphStack[graphify]"
graphstack init . -y --install-deps
```

Then open Cursor chat and describe your task — GraphStack rules load automatically.

---

## Maintainer: publish a new version

1. Bump `version` in `pyproject.toml` and `scripts/graphstack/__init__.py`.
2. `python scripts/sync_assets.py`
3. Commit, tag (`vX.Y.Z`), push tag.
4. **Publish GitHub Release** from the tag → triggers `.github/workflows/publish.yml`.

Trusted publisher (already configured):

- Project: `MertCapkin_GraphStack`
- Owner: `MertCapkin` · Repository: `GraphStack`
- Workflow: `publish.yml` · Environment: `pypi`

GitHub environment required: https://github.com/MertCapkin/GraphStack/settings/environments → `pypi`
