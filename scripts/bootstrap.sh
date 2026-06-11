#!/usr/bin/env bash
# GraphStack one-line bootstrap for Cursor terminal (macOS / Linux)
#
# Usage (in your project folder):
#   curl -fsSL https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.sh | bash
#
# Or:  bash scripts/bootstrap.sh

set -euo pipefail

resolve_python() {
  if command -v py >/dev/null 2>&1; then
    echo "py -3"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return
  fi
  echo "GraphStack bootstrap: Python 3.8+ required." >&2
  exit 127
}

PY=$(resolve_python)

echo ""
echo "GraphStack bootstrap"
echo "===================="
echo ""

$PY -m pip install --upgrade pip --quiet 2>/dev/null || true

assets_ok() {
  $PY -c "from graphstack.installer import install_source_root; p=install_source_root()/'.cursor'/'rules'/'graphstack.mdc'; import sys; sys.exit(0 if p.is_file() else 1)"
}

if $PY -m graphstack --version >/dev/null 2>&1 && assets_ok && [ -f .cursor/rules/graphstack.mdc ]; then
  echo "GraphStack is already set up in this project."
  echo "  Health: $PY -m graphstack doctor"
  exit 0
fi

echo "Step 1/2: Installing MertCapkin_GraphStack + graphify from PyPI..."
if ! $PY -m pip install --upgrade "MertCapkin_GraphStack[graphify]"; then
  echo "PyPI install failed — trying GitHub source..." >&2
  $PY -m pip install --upgrade "MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git"
fi
if ! assets_ok; then
  echo "PyPI wheel missing .cursor assets — force reinstall..." >&2
  $PY -m pip install --upgrade --force-reinstall "MertCapkin_GraphStack[graphify]" || \
    $PY -m pip install --upgrade --force-reinstall "MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git"
fi
if ! assets_ok; then
  echo "GraphStack bootstrap: installed package missing Cursor workflow files." >&2
  exit 1
fi
echo "  Installed: $($PY -m graphstack --version)"

echo ""
echo "Step 2/2: Initializing GraphStack in this project..."
$PY -m graphstack init . -y --install-deps
init_rc=$?
if [ ! -f .cursor/rules/graphstack.mdc ]; then
  echo "Bootstrap failed: .cursor/rules/graphstack.mdc was not created." >&2
  exit 1
fi
if [ "$init_rc" -ne 0 ]; then
  echo "Init reported issues (exit $init_rc) but core files are present." >&2
  echo "Run: $PY -m graphstack doctor" >&2
fi
echo "GraphStack bootstrap complete."
exit 0
