"""Path and configuration constants used across the package.

Paths are resolved relative to the *current working directory* (the project
root) at call time — never module import time. This keeps the package
testable in temporary directories.
"""

from __future__ import annotations

from pathlib import Path

HANDOFF_DIR = Path("handoff")
BOARD_DIR = HANDOFF_DIR / "board"
TODO_DIR = BOARD_DIR / "todo"
DOING_DIR = BOARD_DIR / "doing"
DONE_DIR = BOARD_DIR / "done"

GRAPHIFY_OUT = Path("graphify-out")
GRAPH_REPORT = GRAPHIFY_OUT / "GRAPH_REPORT.md"
GRAPH_JSON = GRAPHIFY_OUT / "graph.json"
GRAPH_HTML = GRAPHIFY_OUT / "graph.html"

STALE_GRAPH_HOURS = 24

# Required keys for GNAP board task JSON files (see handoff/board/README.md).
TASK_REQUIRED_KEYS = ("id", "title", "status", "created_at")
