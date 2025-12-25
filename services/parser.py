# ==================================================
# services/parser.py — Command Parsing Helpers
# ==================================================
#
# Command-level parsing utilities shared by commands (e.g., /timerdate argument parsing).
#
# Layer: Services
#
# Responsibilities:
# - Encapsulate domain logic and data access
# - Keep formatting rules consistent across commands and daily jobs
# - Provide stable functions consumed by commands/daily scripts
#
# Boundaries:
# - Services may use core utilities, but should avoid importing command modules.
# - Services should not perform Telegram network calls directly (commands/daily own messaging).
#
# ==================================================
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional

_DURATION_TOKEN_RE = re.compile(
    r"(?P<num>\d+)\s*(?P<unit>d|day|days|h|hr|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)\b",
    re.IGNORECASE,
)

@dataclass(frozen=True)
class ParsedTimer:
    seconds: int
    message: str


def parse_duration(text: str) -> int:
    """
    Parses duration strings like:
      - "10m"
      - "1h 30m"
      - "45s"
      - "2d 3h"
      - "1h30m" (works because regex finds both tokens)

    Returns: total seconds (int)

    Raises: ValueError if nothing could be parsed or result <= 0
    """
    if not text:
        raise ValueError("Empty duration")

    s = text.strip().lower()

    total = 0
    for m in _DURATION_TOKEN_RE.finditer(s):
        n = int(m.group("num"))
        unit = m.group("unit").lower()

        if unit in ("d", "day", "days"):
            total += n * 24 * 60 * 60
        elif unit in ("h", "hr", "hrs", "hour", "hours"):
            total += n * 60 * 60
        elif unit in ("m", "min", "mins", "minute", "minutes"):
            total += n * 60
        elif unit in ("s", "sec", "secs", "second", "seconds"):
            total += n

    if total <= 0:
        raise ValueError("Invalid duration format")

    return total


def parse_timer_args(full_text: str) -> ParsedTimer:
    """
    full_text example: "/timer 10m take cookies out"
    Returns ParsedTimer(seconds, message)
    """
    if not full_text:
        raise ValueError("Empty command text")

    parts = full_text.split(maxsplit=2)
    if len(parts) < 2:
        raise ValueError("Duration is missing")

    seconds = parse_duration(parts[1])
    message = parts[2].strip() if len(parts) >= 3 else ""
    return ParsedTimer(seconds=seconds, message=message)


def parse_datetime_utc(text: str, *, assume_tz=timezone.utc) -> datetime:
    """
    Parses a date/time string into an aware UTC datetime.

    Supported formats:
      - "YYYY-MM-DD HH:MM"
      - "YYYY-MM-DDTHH:MM"
      - "YYYY-MM-DD HH:MM:SS"
      - "YYYY-MM-DDTHH:MM:SS"

    If the input is naive, we assume `assume_tz` then convert to UTC.
    """
    if not text:
        raise ValueError("Empty datetime")

    s = text.strip().replace("T", " ")

    fmts = (
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y %H:%M:%S",
    )
    dt: Optional[datetime] = None
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        raise ValueError("Invalid datetime format")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=assume_tz)

    return dt.astimezone(timezone.utc)


def parse_timerdate_args(full_text: str, *, assume_tz=timezone.utc) -> Tuple[datetime, str]:
    """
    full_text example:
      "/timerdate 2025-12-31 23:59 New Year!"
    Returns (target_time_utc, message)

    NOTE: We require both date and time.
    """
    if not full_text:
        raise ValueError("Empty command text")

    # /timerdate <date> <time> [<tz>] [message...]
    # date formats supported:
    #   - YYYY-MM-DD
    #   - DD.MM.YYYY
    # tz formats supported:
    #   - +3
    #   - +03
    #   - +03:00
    #   - -5
    parts = full_text.split()
    if len(parts) < 3:
        raise ValueError("Date/time is missing")

    date_part = parts[1]
    time_part = parts[2]

    tz = assume_tz
    msg_start = 3

    # optional timezone offset token
    if len(parts) >= 4:
        m = re.fullmatch(r"([+-])(\d{1,2})(?::?(\d{2}))?", parts[3])
        if m:
            sign = -1 if m.group(1) == "-" else 1
            hours = int(m.group(2))
            minutes = int(m.group(3) or "0")
            tz = timezone(sign * timedelta(hours=hours, minutes=minutes))
            msg_start = 4

    dt_str = f"{date_part} {time_part}"
    target = parse_datetime_utc(dt_str, assume_tz=tz)

    message = " ".join(parts[msg_start:]).strip() if len(parts) > msg_start else ""
    return target, message