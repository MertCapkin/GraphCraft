#!/usr/bin/env bash
# GraphStack GNAP board — thin shim that delegates to the Python core.
# Real logic lives in scripts/graphstack/board.py.
#
# Usage: bash scripts/board.sh <command> [args]
#   commands: status | new | claim | complete | log | help

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}${PYTHONPATH:+:$PYTHONPATH}"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "❌ GraphStack: Python not found. Install Python 3.8+ and retry." >&2
  exit 127
fi

exec "$PY" -m graphstack board "$@"
