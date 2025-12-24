# core/formatter.py
from __future__ import annotations


def format_remaining_time(seconds: int) -> str:
    """Human-friendly remaining time like '1h 02m 05s'."""
    if seconds < 0:
        seconds = 0

    s = int(seconds)
    days, s = divmod(s, 86400)
    hours, s = divmod(s, 3600)
    minutes, s = divmod(s, 60)

    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    if minutes or hours or days:
        parts.append(f"{minutes:02d}m" if (hours or days) else f"{minutes}m")
    parts.append(f"{s:02d}s" if (minutes or hours or days) else f"{s}s")

    return " ".join(parts)


def choose_update_interval(remaining_seconds: int) -> int:
    """
    How often we update the countdown message.
    """
    r = int(remaining_seconds)

    if r <= 0:
        return 1

    # < 1 minute -> every 1 second
    if r < 60:
        return 1

    # 1..10 minutes -> every 5 seconds
    if r < 10 * 60:
        return 5

    # 10..60 minutes -> every 30 seconds
    if r < 60 * 60:
        return 30

    # >= 1 hour -> every 60 seconds
    return 60



# ---- Backward-compatible aliases (на всякий случай) ----
def format_remaining(seconds: int) -> str:
    return format_remaining_time(seconds)


def choose_interval(remaining_seconds: int) -> int:
    return choose_update_interval(remaining_seconds)
