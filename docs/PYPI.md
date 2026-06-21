# PyPI — MertCapkin_GraphCraft

**Target:** https://pypi.org/project/MertCapkin_GraphCraft/

| | |
|---|---|
| **Install** | `pip install "MertCapkin_GraphCraft[graphstack]"` |
| **CLI** | `graphcraft` |
| **Dependency** | `MertCapkin_GraphStack[graphify]` (PyPI, separate package) |

GraphCraft wheel ships **overlay only** (design layer). GraphStack is **not** bundled — it installs from PyPI via the `[graphstack]` extra.

---

## User install

Inside **your mobile app/game project folder**:

```powershell
pip install "MertCapkin_GraphCraft[graphstack]"
graphcraft init . -y --install-deps
graphcraft design update .
graphcraft doctor .
```

Until PyPI is live, install from GitHub:

```powershell
pip install "MertCapkin_GraphCraft[graphstack] @ git+https://github.com/MertCapkin/GraphCraft.git@v0.1.1"
```

GraphStack dependency still resolves from PyPI automatically.

---

## Maintainer: publish a new version

1. Bump `version` in `pyproject.toml` and `scripts/graphcraft/__init__.py`.
2. Update `CHANGELOG_GRAPHCRAFT.md`.
3. `python scripts/sync_graphcraft_assets.py`
4. Commit, tag (`vX.Y.Z`), push tag.
5. **Publish GitHub Release** from the tag → triggers `.github/workflows/publish.yml`.

### PyPI trusted publisher (one-time setup)

On [pypi.org](https://pypi.org):

1. Create project `MertCapkin_GraphCraft`
2. Publishing → Add trusted publisher:
   - Owner: `MertCapkin`
   - Repository: `GraphCraft`
   - Workflow: `publish.yml`
   - Environment: `pypi`

On GitHub → Settings → Environments → `pypi` (optional protection rules).

### Local dry run

```bash
python scripts/sync_graphcraft_assets.py
python -m pip install build
python -m build
python -m twine check dist/*
```

Do **not** upload manually if trusted publishing is configured — use GitHub Release.

---

## GraphStack dependency (separate)

GraphStack remains on PyPI as `MertCapkin_GraphStack`: https://pypi.org/project/MertCapkin_GraphStack/

See [GRAPHSTACK.md](GRAPHSTACK.md).
