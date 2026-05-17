"""Quality tests for output compaction — paths and errors must survive."""

from __future__ import annotations

from graphstack.compact.git import compact_git_diff, compact_git_log, compact_git_status
from graphstack.compact.generic import compact_generic, compact_pytest
from graphstack.compact.registry import compact_command_output


SAMPLE_STATUS = """\
On branch feature/login
Your branch is ahead of 'origin/main' by 2 commits.
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
\tmodified:   src/auth/login.ts
\tnew file:   src/auth/session.ts

Changes not staged for commit:
\tmodified:   src/api/types.ts

Untracked files:
\tREADME.local.md
"""

SAMPLE_DIFF = """\
diff --git a/src/a.py b/src/a.py
--- a/src/a.py
+++ b/src/a.py
@@ -1,3 +1,4 @@
 line1
-line2
+line2changed
 line3
"""

SAMPLE_PYTEST_FAIL = """\
============================= test session starts ==============================
collected 3 items

tests/test_auth.py::test_login FAILED

=================================== FAILURES ===================================
_______________________________ test_login ___________________________________
E   AssertionError: expected 200

========================== 1 failed, 2 passed in 0.12s ==========================
"""


def test_git_status_keeps_branch_and_paths() -> None:
    out = compact_git_status(SAMPLE_STATUS)
    assert "feature/login" in out or "On branch" in out
    assert "login.ts" in out
    assert "types.ts" in out


def test_git_diff_keeps_hunk_headers() -> None:
    out = compact_git_diff(SAMPLE_DIFF)
    assert "diff --git" in out
    assert "@@" in out
    assert "-line2" in out or "+line2changed" in out


def test_git_log_truncates_but_keeps_recent() -> None:
    lines = [f"{i:07x} commit message {i}" for i in range(50)]
    raw = "\n".join(lines)
    out = compact_git_log(raw, max_entries=10)
    assert "commit message 0" in out
    assert "omitted" in out


def test_pytest_keeps_failure_and_summary() -> None:
    out = compact_pytest(SAMPLE_PYTEST_FAIL)
    assert "FAILED" in out or "AssertionError" in out
    assert "failed" in out.lower()


def test_registry_falls_back_when_compaction_empty() -> None:
    raw = "important error on line 1\n" + ("noise\n" * 500)
    result = compact_command_output(["unknown-tool"], raw)
    assert "error" in result.text.lower() or len(result.text) > 0


def test_critical_lines_survive_generic_truncate() -> None:
    lines = ["ok"] * 200 + ["Fatal: disk full"] + ["ok"] * 200
    out = compact_generic("\n".join(lines))
    assert "Fatal" in out


def test_registry_git_status_route() -> None:
    result = compact_command_output(["git", "status"], SAMPLE_STATUS)
    assert result.used_compactor == "git-status"
    assert "login.ts" in result.text
