import re
from datetime import timedelta

def parse_duration(text: str) -> timedelta | None:
    """
    Parses strings like:
    10m, 5h, 2d, 1h30m
    """
    pattern = re.compile(r"(\d+)([smhd])")
    matches = pattern.findall(text.lower())

    if not matches:
        return None

    total = timedelta()
    for value, unit in matches:
        value = int(value)
        if unit == "s":
            total += timedelta(seconds=value)
        elif unit == "m":
            total += timedelta(minutes=value)
        elif unit == "h":
            total += timedelta(hours=value)
        elif unit == "d":
            total += timedelta(days=value)

    return total
