#!/usr/bin/env bash
# GraphStack v4 Installer — thin shim that delegates to the Python core.
# Real logic lives in scripts/graphstack/installer.py.
#
# Usage: bash install.sh [target-project-path] [-y|--non-interactive]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/scripts${PYTHONPATH:+:$PYTHONPATH}"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "❌ GraphStack: Python 3.8+ is required but was not found on PATH." >&2
  echo "   Install Python and re-run this script." >&2
  exit 127
fi

exec "$PY" -m graphstack install "$@"
