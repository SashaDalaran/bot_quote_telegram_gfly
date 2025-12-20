def format_remaining(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    return f"{m}m {s}s"

def choose_interval(seconds: int) -> int:
    if seconds > 3600:
        return 60
    if seconds > 300:
        return 15
    if seconds > 60:
        return 5
    return 1
