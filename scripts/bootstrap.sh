#!/usr/bin/env bash
# GraphStack one-line bootstrap for Cursor terminal (macOS / Linux)
#
# Usage (in your project folder):
#   curl -fsSL https://raw.githubusercontent.com/MertCapkin/GraphStack/main/scripts/bootstrap.sh | bash
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

echo "Step 1/2: Installing MertCapkin_GraphStack + graphify from PyPI..."
if ! $PY -m pip install --upgrade "MertCapkin_GraphStack[graphify]"; then
  echo "PyPI install failed — trying GitHub source..." >&2
  $PY -m pip install --upgrade "MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git"
fi

echo ""
echo "Step 2/2: Initializing GraphStack in this project..."
exec $PY -m graphstack init . -y --install-deps
