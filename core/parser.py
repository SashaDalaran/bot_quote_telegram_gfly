# core/parser.py

from typing import List, Optional, Tuple


def parse_timer(args: List[str]) -> Tuple[int, Optional[str]]:
    if not args:
        raise ValueError("No timer value provided")

    time_part = args[0]
    message = " ".join(args[1:]) if len(args) > 1 else None

    unit = time_part[-1]
    value = time_part[:-1]

    if not value.isdigit():
        raise ValueError("Invalid timer value")

    seconds = int(value)

    if unit == "s":
        return seconds, message
    if unit == "m":
        return seconds * 60, message
    if unit == "h":
        return seconds * 3600, message

    raise ValueError("Invalid time unit")
