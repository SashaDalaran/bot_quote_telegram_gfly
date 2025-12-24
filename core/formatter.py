# core/formatter.py

def format_remaining(seconds: int) -> str:
    """Format remaining seconds into a human-friendly string."""
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:
        parts.append(f"{s}s")

    return " ".join(parts)


def choose_interval(remaining_seconds: int) -> int:
    """Pick how often we should update the countdown message."""
    r = max(0, int(remaining_seconds))

    if r <= 15:
        return 1
    if r <= 60:
        return 2
    if r <= 5 * 60:
        return 5
    if r <= 30 * 60:
        return 15
    if r <= 2 * 60 * 60:
        return 60
    return 5 * 60


# -------------------------
# Backward-compatible names
# -------------------------
def format_remaining_time(seconds: int) -> str:
    return format_remaining(seconds)


def choose_update_interval(remaining_seconds: int) -> int:
    return choose_interval(remaining_seconds)
