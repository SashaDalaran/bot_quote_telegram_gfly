# core/formatter.py

from datetime import timedelta


def format_duration(seconds: int) -> str:
    if seconds < 0:
        seconds = 0

    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes:
        parts.append(f"{minutes}м")
    parts.append(f"{secs}с")

    return " ".join(parts)


def choose_update_interval(seconds_left: int) -> int:
    if seconds_left > 86400:
        return 3600      # 1 час
    if seconds_left > 3600:
        return 300       # 5 минут
    if seconds_left > 300:
        return 60        # 1 минута
    return 5             # 5 секунд
