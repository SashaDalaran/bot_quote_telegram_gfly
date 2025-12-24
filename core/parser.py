# core/parser.py
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, List

_DURATION_RE = re.compile(r"(?P<value>\d+)\s*(?P<unit>[smhd])", re.IGNORECASE)

# Минимальный набор TZ. Если не указано — считаем UTC.
_TZ_OFFSETS = {
    "UTC": 0,
    "GMT": 0,
    "MSK": 3,
    "EET": 2,
    "CET": 1,
    "GET": 4,  # Georgia (Tbilisi) Time
    "TBI": 4,
}


def parse_duration(text: str) -> int:
    """
    Parse durations like:
      10s, 5m, 2h, 1d, 1h30m, 2m10s
    If only digits (e.g. "10") -> minutes (10m).
    """
    t = text.strip()
    if not t:
        raise ValueError("Empty duration")

    if t.isdigit():
        return int(t) * 60  # default: minutes

    total = 0
    matches = list(_DURATION_RE.finditer(t))
    if not matches:
        raise ValueError(f"Bad duration: {text}")

    for m in matches:
        val = int(m.group("value"))
        unit = m.group("unit").lower()
        if unit == "s":
            total += val
        elif unit == "m":
            total += val * 60
        elif unit == "h":
            total += val * 3600
        elif unit == "d":
            total += val * 86400

    if total <= 0:
        raise ValueError(f"Bad duration: {text}")

    return total


def parse_timer(args: List[str]) -> Tuple[int, Optional[str]]:
    """
    /timer <duration> [message...]
    """
    if not args:
        raise ValueError("No args")

    seconds = parse_duration(args[0])
    msg = " ".join(args[1:]).strip() if len(args) > 1 else None
    return seconds, (msg or None)


def parse_date_time(args: List[str]) -> Tuple[datetime, Optional[str]]:
    """
    /timerdate <date> <time> [TZ] [message...]
    Examples:
      /timerdate 2025-12-31 23:59 UTC Happy New Year
      /timerdate 31.12.2025 23:59 GET ...
    Returns target_time in UTC.
    """
    if len(args) < 2:
        raise ValueError("Need <date> <time>")

    date_part = args[0].strip()
    time_part = args[1].strip()

    tz_name = "UTC"
    msg_start_idx = 2
    if len(args) >= 3:
        cand = args[2].strip().upper()
        if cand in _TZ_OFFSETS:
            tz_name = cand
            msg_start_idx = 3

    msg = " ".join(args[msg_start_idx:]).strip() if len(args) > msg_start_idx else None

    # date formats
    dt_local: datetime
    for fmt in ("%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M", "%d-%m-%Y %H:%M"):
        try:
            dt_local = datetime.strptime(f"{date_part} {time_part}", fmt)
            break
        except ValueError:
            dt_local = None  # type: ignore
    if dt_local is None:
        raise ValueError("Bad date/time format")

    offset = _TZ_OFFSETS.get(tz_name, 0)
    tz = timezone(timedelta(hours=offset))
    dt_with_tz = dt_local.replace(tzinfo=tz)

    return dt_with_tz.astimezone(timezone.utc), (msg or None)


# alias (если где-то импортируют старое имя)
def parse_datetime_with_tz(args: List[str]) -> Tuple[datetime, Optional[str]]:
    return parse_date_time(args)
