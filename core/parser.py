# core/parser.py

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
import re


# -----------------------------
# /timer 10s message
# -----------------------------

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


# -----------------------------
# /timerdate 2025-12-21 18:00 Europe/Moscow message
# -----------------------------

_TZ_OFFSETS = {
    "UTC": 0,
    "MSK": 3,
    "MOSCOW": 3,
    "TBILISI": 4,
}


def parse_datetime_with_tz(args: List[str]) -> Tuple[datetime, Optional[str]]:
    """
    Examples:
    /timerdate 2025-12-21 18:00 MSK text
    /timerdate 2025-12-21 18:00 UTC
    """

    if len(args) < 2:
        raise ValueError("Not enough arguments")

    date_part = args[0]
    time_part = args[1]

    tz_name = "UTC"
    message_start = 2

    if len(args) >= 3 and args[2].upper() in _TZ_OFFSETS:
        tz_name = args[2].upper()
        message_start = 3

    message = " ".join(args[message_start:]) if len(args) > message_start else None

    dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")

    offset = _TZ_OFFSETS.get(tz_name, 0)
    tz = timezone(timedelta(hours=offset))

    return dt.replace(tzinfo=tz), message
