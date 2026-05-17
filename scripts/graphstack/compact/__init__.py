"""Token-safe shell output compaction (independent implementation).

Preserves actionable detail (paths, errors, hunks). Falls back to raw output
when compaction would drop too much signal.
"""

from .registry import compact_command_output

__all__ = ["compact_command_output"]
