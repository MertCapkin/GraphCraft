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

See `board/todo/example-task.json` for the schema.
