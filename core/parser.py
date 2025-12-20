import re

_TIME_RE = re.compile(r"^(\d+)([smhd])$", re.IGNORECASE)

_MULTIPLIERS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
}

def parse_timer(args: list[str]) -> tuple[int, str | None]:
    """
    /timer 10s tea
    /timer 5m
    /timer 1h work
    """

    if not args:
        return 0, None

    match = _TIME_RE.match(args[0])
    if not match:
        return 0, None

    value = int(match.group(1))
    unit = match.group(2).lower()

    seconds = value * _MULTIPLIERS[unit]
    text = " ".join(args[1:]) if len(args) > 1 else None

    return seconds, text
