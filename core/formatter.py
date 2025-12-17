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


def choose_update_interval(remaining: int) -> int:
    """
    Decide how often to update timer message.
    """
    if remaining > 6 * 3600:
        return 300        # every 5 min
    if remaining > 3600:
        return 120        # every 2 min
    if remaining > 600:
        return 60         # every 1 min
    if remaining > 120:
        return 30
    if remaining > 30:
        return 10
    return 5
