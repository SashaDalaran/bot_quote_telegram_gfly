from typing import List


def choose_update_interval(seconds_left: int) -> int:
    """
    Smart update intervals:
      > 10m  -> 60s
      3-10m  -> 5s
      1-3m   -> 2s
      < 1m   -> 1s
    """
    if seconds_left > 10 * 60:
        return 60
    if seconds_left > 3 * 60:
        return 5
    if seconds_left > 1 * 60:
        return 2
    return 1


def format_remaining_time(seconds: int) -> str:
    """Format remaining seconds as 'Xd. Yh Zm Ws' (RU short labels)."""
    if seconds < 0:
        seconds = 0

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts: List[str] = []
    if days:
        parts.append(f"{days} дн.")
    if hours or days:
        parts.append(f"{hours} ч.")
    if minutes or hours or days:
        parts.append(f"{minutes} мин.")
    parts.append(f"{seconds} сек.")

    return " ".join(parts)


def pretty_time_short(seconds: int) -> str:
    """Short representation used in confirmations."""
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"
