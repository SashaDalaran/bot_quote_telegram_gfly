# ==================================================
# core/formatter.py
# ==================================================

def choose_update_interval(sec_left: int) -> float:
    """
    Smart countdown refresh rate.
    """
    if sec_left > 10 * 60:
        return 30
    if sec_left > 3 * 60:
        return 5
    if sec_left > 60:
        return 2
    if sec_left > 10:
        return 1
    if sec_left > 3:
        return 0.5
    return 0.25


def format_duration(seconds: int) -> str:
    """
    Format seconds into human readable duration.
    Example: 1д 2ч 3м 4с
    """
    seconds = max(0, seconds)

    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)

    parts = []
    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes:
        parts.append(f"{minutes}м")
    if sec or not parts:
        parts.append(f"{sec}с")

    return " ".join(parts)
