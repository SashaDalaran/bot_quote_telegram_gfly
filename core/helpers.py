# ==================================================
# core/helpers.py — General Helpers
# ==================================================
#
# Small, generic helper utilities shared across the project.
#
# Layer: Core
#
# Responsibilities:
# - Provide tiny, reusable helpers that do not belong to any specific domain (quotes/holidays/timers)
# - Keep I/O behavior predictable (UTF-8, trimmed lines, safe failure modes)
#
# Boundaries:
# - Core must remain independent from Telegram / network APIs.
# - Helpers must remain generic: do NOT add business rules here.
#
# ==================================================

from __future__ import annotations

from typing import List


# ==================================================
# File helpers
# ==================================================
#
# These helpers are intentionally small and boring.
# If a helper starts growing "smart" behavior, it probably belongs in services/.
#
def load_lines(path: str) -> List[str]:
    """Load non-empty UTF-8 lines from a file.

    Why this exists:
    - Many features use simple text datasets (quotes, phrase fragments, etc.).
    - We want consistent behavior across the codebase:
      * UTF-8 decoding
      * whitespace trimmed
      * empty lines ignored
      * missing file = empty dataset (not a hard crash)

    Args:
        path:
            Relative or absolute path to a text file.

    Returns:
        A list of stripped, non-empty lines.
        Returns an empty list if the file does not exist.

    Notes:
        - Only FileNotFoundError is swallowed intentionally.
          Other exceptions (permission issues, encoding errors) are real problems
          and should surface during deployment/testing.
    """

    # --------------------------------------------------
    # Read + normalize
    # --------------------------------------------------
    try:
        with open(path, "r", encoding="utf-8") as f:
            # Strip whitespace and drop empty lines to keep callers simple.
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # Missing optional datasets should not kill the bot.
        return []
