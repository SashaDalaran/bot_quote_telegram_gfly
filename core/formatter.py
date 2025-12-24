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
    """How often we edit the message (seconds)."""
    r = int(remaining_seconds)

    if r <= 10:
        return 1
    if r <= 60:
        return 2
    if r <= 10 * 60:
        return 5
    if r <= 60 * 60:
        return 10
    return 30


# ---- Backward-compatible aliases (на всякий случай) ----
def format_remaining(seconds: int) -> str:
    return format_remaining_time(seconds)


def choose_interval(remaining_seconds: int) -> int:
    return choose_update_interval(remaining_seconds)
