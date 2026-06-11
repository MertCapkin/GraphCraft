# Publishing GraphStack to PyPI

## Package name

PyPI distribution: **`MertCapkin_GraphStack`** (the name `graphstack` is taken on PyPI).

- `pip install MertCapkin_GraphStack[graphify]`
- CLI command after install: **`graphstack`** (unchanged)

Pending publisher on PyPI must use project name **`MertCapkin_GraphStack`** — must match `pyproject.toml` `name`.

## One-time setup (maintainer)

1. PyPI account → **Publishing** → pending publisher:
   - Pending project name: `MertCapkin_GraphStack`
   - Owner: `MertCapkin`
   - Repository name: `GraphStack`
   - Workflow: `publish.yml`
   - Environment: `pypi`
2. GitHub → Settings → Environments → create **`pypi`**
3. Trusted Publishing linked to `MertCapkin/GraphStack`

## Release flow

1. Bump version in `pyproject.toml` and `scripts/graphstack/__init__.py`.
2. `python scripts/sync_assets.py`
3. Commit, tag, push, **Publish GitHub Release** (triggers `publish.yml`).

## User install (after publish)

```bash
pip install "MertCapkin_GraphStack[graphify]"
cd /path/to/your-project
graphstack init . -y --install-deps
```

Or one-liner bootstrap (Cursor terminal):

```powershell
irm https://raw.githubusercontent.com/MertCapkin/GraphStack/main/scripts/bootstrap.ps1 | iex
```
