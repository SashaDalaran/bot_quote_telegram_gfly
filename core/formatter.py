from datetime import timedelta

# ==================================================
# Time formatting helpers
# ==================================================

def format_remaining_time(seconds: int) -> str:
    """
    Convert seconds to human readable format.
    Example: 3661 -> "1h 1m 1s"
    """
    if seconds <= 0:
        return "0s"

    parts = []

    td = timedelta(seconds=seconds)
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def pretty_time_short(seconds: int) -> str:
    """
    Short readable duration.
    Example: 3661 -> "1h 1m"
    """
    if seconds <= 0:
        return "0s"

    td = timedelta(seconds=seconds)
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m"
    return f"{seconds}s"


# core/formatter.py

def choose_update_interval(remaining_seconds: int) -> int:
    """
    How often we should update the countdown message.

    Goal:
    - <= 60s: every 1s (smooth countdown)
    - <= 5m: every 5s
    - <= 30m: every 10s
    - <= 2h: every 30s
    - else: every 60s
    """
    r = max(0, int(remaining_seconds))

    if r <= 60:
        return 1
    if r <= 5 * 60:
        return 5
    if r <= 30 * 60:
        return 10
    if r <= 2 * 60 * 60:
        return 30
    return 60

