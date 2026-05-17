# GraphStack GNAP Board

Git-native task coordination. No server. No database. Just files.

```
board/
  todo/    ← Architect creates tasks here
  doing/   ← Role "claims" a task by moving it here
  done/    ← Completed tasks land here
```

## How It Works

1. Architect writes `handoff/BRIEF.md` as usual
2. Architect also creates `board/todo/<task-id>.json`
3. Builder moves the file to `board/doing/` when starting
4. On completion, moves to `board/done/`
5. Git history = full audit trail of who did what, when

## Why Git?

- Cursor kapatsan bile board persist eder
- Ekip arkadaşın `git pull` yapınca board'u görür
- `git log board/` = tam denetim izi
- Sunucu yok, veritabanı yok, kurulum yok

## Task File Format

Create `board/todo/<task-id>.json` (filename must match `id`):

```json
{
  "id": "add-rate-limiting",
  "title": "Add rate limiting to login endpoint",
  "created_at": "2026-05-04T10:00:00Z",
  "created_by": "architect",
  "brief": "handoff/BRIEF.md",
  "graph_nodes": [],
  "criteria_count": 0,
  "priority": "normal",
  "status": "todo",
  "assigned_to": null,
  "started_at": null,
  "completed_at": null,
  "notes": ""
}
```

Or use the CLI:

```bash
python -m graphstack board new <task-id> "Task title here"
```

Required fields: `id`, `title`, `status`, `created_at`.
