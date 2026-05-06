#!/bin/bash
# GraphStack v3 Installer
# Usage: bash install.sh [target-project-path]
# Default: installs into current directory

set -e

TARGET="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "🧠 GraphStack v3 Installer"
echo "==========================="
echo "Target: $(realpath "$TARGET")"
echo ""

# ── 1. Directories ───────────────────────────────────────
echo "📁 Creating directories..."
mkdir -p "$TARGET/.cursor/rules"
mkdir -p "$TARGET/.cursor/skills/architect"
mkdir -p "$TARGET/.cursor/skills/builder"
mkdir -p "$TARGET/.cursor/skills/reviewer"
mkdir -p "$TARGET/.cursor/skills/qa"
mkdir -p "$TARGET/.cursor/skills/ship"
mkdir -p "$TARGET/orchestrator"
mkdir -p "$TARGET/handoff/board/todo"
mkdir -p "$TARGET/handoff/board/doing"
mkdir -p "$TARGET/handoff/board/done"
mkdir -p "$TARGET/graphify-out"
mkdir -p "$TARGET/scripts"
mkdir -p "$TARGET/docs"     # ← was missing in v2

# ── 2. Cursor rules ──────────────────────────────────────
echo "📋 Installing Cursor rules..."
cp "$SCRIPT_DIR/.cursor/rules/graphstack.mdc" "$TARGET/.cursor/rules/graphstack.mdc"

# ── 3. Orchestrator ──────────────────────────────────────
echo "🤖 Installing orchestrator..."
cp "$SCRIPT_DIR/orchestrator/ORCHESTRATOR.md"    "$TARGET/orchestrator/ORCHESTRATOR.md"
cp "$SCRIPT_DIR/orchestrator/TOKEN_OPTIMIZER.md" "$TARGET/orchestrator/TOKEN_OPTIMIZER.md"

# ── 4. Role skills ───────────────────────────────────────
echo "🎭 Installing role skills..."
cp "$SCRIPT_DIR/skills/architect/ARCHITECT.md"     "$TARGET/.cursor/skills/architect/ARCHITECT.md"
cp "$SCRIPT_DIR/skills/builder/BUILDER.md"         "$TARGET/.cursor/skills/builder/BUILDER.md"
cp "$SCRIPT_DIR/skills/reviewer/REVIEWER.md"       "$TARGET/.cursor/skills/reviewer/REVIEWER.md"
cp "$SCRIPT_DIR/skills/qa/QA.md"                   "$TARGET/.cursor/skills/qa/QA.md"
cp "$SCRIPT_DIR/skills/ship/SHIP.md"               "$TARGET/.cursor/skills/ship/SHIP.md"

echo "🚀 Installing Bootstrapper..."
mkdir -p "$TARGET/.cursor/skills/bootstrapper"
cp "$SCRIPT_DIR/skills/bootstrapper/BOOTSTRAPPER.md" "$TARGET/.cursor/skills/bootstrapper/BOOTSTRAPPER.md"

# ── 5. GNAP board ────────────────────────────────────────
echo "📋 Installing GNAP board..."
cp "$SCRIPT_DIR/scripts/board.sh"                          "$TARGET/scripts/board.sh"
chmod +x "$TARGET/scripts/board.sh"
cp "$SCRIPT_DIR/handoff/board/README.md"                   "$TARGET/handoff/board/README.md"
cp "$SCRIPT_DIR/handoff/board/todo/example-task.json"      "$TARGET/handoff/board/todo/example-task.json"

# ── 6. Handoff templates (no overwrite) ──────────────────
if [ ! -f "$TARGET/handoff/BRIEF.md" ]; then
  echo "📝 Creating handoff templates..."
  cp "$SCRIPT_DIR/handoff/BRIEF.md"      "$TARGET/handoff/BRIEF.md"
  cp "$SCRIPT_DIR/handoff/REVIEW.md"     "$TARGET/handoff/REVIEW.md"
  cp "$SCRIPT_DIR/handoff/BOOTSTRAP.md"  "$TARGET/handoff/BOOTSTRAP.md"
else
  echo "⏭️  Handoff files already exist — skipping (not overwriting)"
fi

# STATE.md must always exist for Orchestrator to read safely
if [ ! -f "$TARGET/handoff/STATE.md" ]; then
  cat > "$TARGET/handoff/STATE.md" << 'MD'
# GraphStack Session State

> Auto-managed by Orchestrator. Append-only — never delete history.

---

<!-- Sessions appended below, newest first -->
MD
fi

# ── 7. Docs ──────────────────────────────────────────────
echo "📚 Installing docs..."
cp "$SCRIPT_DIR/docs/CURSOR_PROMPTS.md" "$TARGET/docs/CURSOR_PROMPTS.md"

# ── 8. Git hook (optional) ───────────────────────────────
if [ -d "$TARGET/.git" ]; then
  echo ""
  read -p "🔗 Install git post-commit hook for auto graph updates? (y/N): " INSTALL_HOOK
  if [[ "${INSTALL_HOOK:-}" =~ ^[Yy]$ ]]; then
    cp "$SCRIPT_DIR/scripts/post-commit" "$TARGET/.git/hooks/post-commit"
    chmod +x "$TARGET/.git/hooks/post-commit"
    echo "✅ Git hook installed."
  fi
fi

# ── 9. Graphify check ────────────────────────────────────
echo ""
if command -v graphify &> /dev/null; then
  echo "✅ graphify is installed."
else
  echo "⚠️  graphify not found. Install it with:"
  echo "   pip install graphifyy"
fi

# ── Done ─────────────────────────────────────────────────
echo ""
echo "🎉 GraphStack v3 installed!"
echo ""
echo "Next steps:"
echo "  1. Build graph:   open Cursor in your project → type: /graphify ."
echo "  2. Start working: paste the single prompt from docs/CURSOR_PROMPTS.md"
echo ""
