#!/usr/bin/env bash
# GraphStack process gate — thin shim for Cursor / Claude Code hooks.
# Real logic lives in scripts/graphstack/gate.py.
#
# Usage: bash scripts/gate-hook.sh <cursor|claude>

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}${PYTHONPATH:+:$PYTHONPATH}"

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m graphstack gate hook "$@"
elif command -v python >/dev/null 2>&1; then
  exec python -m graphstack gate hook "$@"
elif command -v py >/dev/null 2>&1; then
  exec py -3 -m graphstack gate hook "$@"
fi

echo "graphstack gate-hook: Python not found — failing open" >&2
if [ "${1:-}" = "cursor" ]; then
  echo '{"continue": true, "permission": "allow"}'
else
  echo '{}'
fi
exit 0
