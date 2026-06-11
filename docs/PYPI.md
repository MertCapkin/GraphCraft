# Publishing GraphStack to PyPI

## One-time setup (maintainer)

1. Create a [PyPI](https://pypi.org) account and project **`graphstack`** (check name availability first).
2. Enable [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) on PyPI:
   - GitHub repo: `MertCapkin/GraphStack`
   - Workflow: `publish.yml`
   - Environment name: `pypi`
3. In GitHub → Settings → Environments → **pypi** → add protection rules if desired.

## Release flow

1. Bump version in `pyproject.toml` and `scripts/graphstack/__init__.py`.
2. Update `CHANGELOG.md`.
3. Sync bundled assets:
   ```bash
   python scripts/sync_assets.py
   ```
4. Commit, tag, and push:
   ```bash
   git tag v4.5.0
   git push origin v4.5.0
   ```
5. Create a **GitHub Release** from the tag — this triggers `.github/workflows/publish.yml`.

Or run **Publish to PyPI** workflow manually (`workflow_dispatch`).

## Local dry-run (no upload)

```bash
python scripts/sync_assets.py
python -m pip install build
python -m build
python -m pip install dist/graphstack-*.whl
graphstack --version
graphstack init /tmp/test-project -y --install-deps
```

## User install (after publish)

```bash
pip install "graphstack[graphify]"
cd /path/to/your-project
graphstack init . -y --install-deps
```

Workflow markdown files ship **inside the wheel** under `graphstack/assets/` — no git clone required.
