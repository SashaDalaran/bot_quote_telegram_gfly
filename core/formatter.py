# core/formatter.py
from __future__ import annotations


def format_remaining(seconds: int) -> str:
    """
    Human-friendly remaining time.
    Examples:
      9 -> "9s"
      70 -> "1m 10s"
      3700 -> "1h 1m 40s"
      90000 -> "1d 1h 0m 0s"
    """
    if seconds < 0:
        seconds = 0

    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)

    parts = []
    if d:
        parts.append(f"{d}d")
    if h or d:
        parts.append(f"{h}h")
    if m or h or d:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def choose_update_interval(seconds: int) -> int:
    """
    Adaptive refresh interval to avoid too-frequent edits for long timers.
    """
    if seconds > 6 * 3600:
        return 120
    if seconds > 3600:
        return 60
    if seconds > 15 * 60:
        return 15
    if seconds > 60:
        return 5
    return 1


# Back-compat alias (older code may import choose_interval)
choose_interval = choose_update_interval
