#!/bin/bash
# GraphStack GNAP Board Manager
# Usage: bash scripts/board.sh <command> [args]
#
# Commands:
#   status                        — show full board status
#   claim <task-id> <role>        — move task from todo → doing
#   complete <task-id>            — move task from doing → done
#   new <task-id> "<title>"       — create a new task in todo
#   log                           — show git history of board changes

set -uo pipefail
# Note: -e intentionally omitted — arithmetic increments return exit 1 in bash

BOARD="handoff/board"
cmd="${1:-help}"
task_id="${2:-}"

# ── helpers ──────────────────────────────────────────────

json_get() {
  # json_get <file> <key>
  python3 -c "import json,sys; d=json.load(open('$1')); print(d.get('$2') or '-')" 2>/dev/null || echo "-"
}

print_task() {
  local file="$1"
  local id title status assigned
  id=$(json_get "$file" "id")
  title=$(json_get "$file" "title")
  status=$(json_get "$file" "status")
  assigned=$(json_get "$file" "assigned_to")
  printf "  %-32s %-10s %-12s %s\n" "$id" "$status" "$assigned" "$title"
}

require_task_id() {
  if [ -z "$task_id" ]; then
    echo "❌ Error: task-id required."
    echo "   Usage: bash scripts/board.sh $cmd <task-id>"
    exit 1
  fi
}

# ── commands ─────────────────────────────────────────────

case "$cmd" in

  status)
    echo ""
    echo "📋 GraphStack GNAP Board"
    echo "════════════════════════════════════════════════════════"
    printf "  %-32s %-10s %-12s %s\n" "TASK ID" "STATUS" "ASSIGNED" "TITLE"
    echo "  ──────────────────────────────────────────────────────"

    todo_count=0; doing_count=0; done_count=0

    for f in "$BOARD"/todo/*.json; do
      [ -f "$f" ] && [[ "$f" != *example-task* ]] && { print_task "$f"; ((todo_count++)) || true; }
    done
    for f in "$BOARD"/doing/*.json; do
      [ -f "$f" ] && { print_task "$f"; ((doing_count++)) || true; }
    done
    for f in "$BOARD"/done/*.json; do
      [ -f "$f" ] && { print_task "$f"; ((done_count++)) || true; }
    done

    if [ $((todo_count + doing_count + done_count)) -eq 0 ]; then
      echo "  (no tasks yet)"
    fi

    echo ""
    echo "  Todo: $todo_count  |  In Progress: $doing_count  |  Done: $done_count"
    echo ""
    ;;

  claim)
    require_task_id
    role="${3:-}"
    if [ -z "$role" ]; then
      echo "❌ Error: role required."
      echo "   Usage: bash scripts/board.sh claim <task-id> <role>"
      exit 1
    fi

    src="$BOARD/todo/$task_id.json"
    dst="$BOARD/doing/$task_id.json"

    if [ ! -f "$src" ]; then
      # Check if already doing
      if [ -f "$BOARD/doing/$task_id.json" ]; then
        echo "⚠️  Task '$task_id' is already in doing/ (claimed by $(json_get "$BOARD/doing/$task_id.json" assigned_to))"
        exit 0
      fi
      echo "❌ Task '$task_id' not found in todo/"
      echo "   Run: bash scripts/board.sh status"
      exit 1
    fi

    python3 - "$src" "$role" << 'EOF'
import json, sys
from datetime import datetime, timezone
path, role = sys.argv[1], sys.argv[2]
with open(path) as f:
    d = json.load(f)
d['status'] = 'doing'
d['assigned_to'] = role
d['started_at'] = datetime.now(timezone.utc).isoformat()
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
EOF

    mv "$src" "$dst"
    git add "$BOARD/" 2>/dev/null && git commit -m "board: $role claims $task_id" 2>/dev/null || true
    echo "✅ Task '$task_id' claimed by $role"
    ;;

  complete)
    require_task_id

    src="$BOARD/doing/$task_id.json"
    dst="$BOARD/done/$task_id.json"

    if [ ! -f "$src" ]; then
      if [ -f "$BOARD/done/$task_id.json" ]; then
        echo "⚠️  Task '$task_id' is already done."
        exit 0
      fi
      echo "❌ Task '$task_id' not found in doing/"
      echo "   Run: bash scripts/board.sh status"
      exit 1
    fi

    python3 - "$src" << 'EOF'
import json, sys
from datetime import datetime, timezone
path = sys.argv[1]
with open(path) as f:
    d = json.load(f)
d['status'] = 'done'
d['completed_at'] = datetime.now(timezone.utc).isoformat()
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
EOF

    mv "$src" "$dst"
    git add "$BOARD/" 2>/dev/null && git commit -m "board: complete $task_id" 2>/dev/null || true
    echo "✅ Task '$task_id' marked complete"
    ;;

  new)
    require_task_id
    # Collect ALL remaining args as the title (supports spaces without quotes)
    shift 2
    title="${*:-New task}"

    dst="$BOARD/todo/$task_id.json"
    if [ -f "$dst" ]; then
      echo "❌ Task '$task_id' already exists in todo/"
      exit 1
    fi

    python3 - "$dst" "$task_id" "$title" << 'EOF'
import json, sys
from datetime import datetime, timezone
path, id_, title = sys.argv[1], sys.argv[2], sys.argv[3]
task = {
    "id": id_,
    "title": title,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "created_by": "architect",
    "brief": "handoff/BRIEF.md",
    "graph_nodes": [],
    "criteria_count": 0,
    "priority": "normal",
    "status": "todo",
    "assigned_to": None,
    "started_at": None,
    "completed_at": None,
    "notes": ""
}
with open(path, 'w') as f:
    json.dump(task, f, indent=2)
EOF

    git add "$dst" 2>/dev/null && git commit -m "board: new task $task_id — $title" 2>/dev/null || true
    echo "✅ Task '$task_id' created in todo/"
    echo "   Title: $title"
    ;;

  log)
    echo ""
    echo "📜 Board History"
    git log --oneline -- "$BOARD/" 2>/dev/null || echo "(no git history yet — initialize with: git init)"
    echo ""
    ;;

  help|*)
    echo ""
    echo "GraphStack Board — Commands:"
    echo "  status                             show full board"
    echo "  new <id> <title words...>          create task (no quotes needed)"
    echo "  claim <id> <role>                  claim task (builder/reviewer/qa)"
    echo "  complete <id>                      mark done"
    echo "  log                                git history of board"
    echo ""
    echo "Examples:"
    echo "  bash scripts/board.sh new add-rate-limit Add rate limiting to login"
    echo "  bash scripts/board.sh claim add-rate-limit builder"
    echo "  bash scripts/board.sh complete add-rate-limit"
    echo ""
    ;;
esac
