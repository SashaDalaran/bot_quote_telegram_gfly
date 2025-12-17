# ==================================================
# core/parser.py — User Input Parsing Utilities
# ==================================================
#
# This module contains helper functions responsible
# for parsing user-provided input into structured data.
#
# Responsibilities:
# - Parse duration strings into seconds
# - Parse absolute date/time with optional timezone
#
# IMPORTANT:
# - This module contains NO Telegram-specific code
# - It only validates and converts raw input
# - All returned datetimes are normalized to UTC
#
# ==================================================

from datetime import datetime, timedelta, timezone
from typing import List, Tuple

# ==================================================
# Duration parsing
# ==================================================
#
# Parses human-readable duration strings into seconds.
#
# Supported formats:
# - "5"          → 5 minutes
# - "10s"        → 10 seconds
# - "90m"        → 90 minutes
# - "2h"         → 2 hours
# - "1h30m"      → 1 hour 30 minutes
# - "1h15m30s"   → 1 hour 15 minutes 30 seconds
#
# Rules:
# - Plain numbers are interpreted as minutes
# - Units:
#     d → days
#     h → hours
#     m → minutes
#     s → seconds
#
# Returns:
# - Total duration in seconds
#
def parse_duration(text: str) -> int:
    text = text.strip().lower()
    if not text:
        raise ValueError("Empty duration")

    # --------------------------------------------------
    # Plain number → minutes
    # --------------------------------------------------
    if text.isdigit():
        minutes = int(text)
        if minutes <= 0:
            raise ValueError("Duration must be > 0")
        return minutes * 60

    total_seconds = 0
    number = ""

    for ch in text:
        if ch.isdigit():
            number += ch
            continue

        if not number:
            raise ValueError("Bad duration format")

        value = int(number)
        number = ""

        if ch == "d":
            total_seconds += value * 86400
        elif ch == "h":
            total_seconds += value * 3600
        elif ch == "m":
            total_seconds += value * 60
        elif ch == "s":
            total_seconds += value
        else:
            raise ValueError(f"Unknown duration unit: {ch}")

    # Leftover number without unit → minutes
    if number:
        total_seconds += int(number) * 60

    if total_seconds <= 0:
        raise ValueError("Duration must be > 0")

    return total_seconds

# ==================================================
# Absolute date/time parsing
# ==================================================
#
# Parses an absolute date/time from argument list.
#
# Expected argument format:
#   [DD.MM.YYYY, HH:MM, [TZ], ...message_words]
#
# Timezone examples:
# - UTC+3
# - GMT+1
# - UTC-2
# - GMT-0
#
# Returns:
# - target_utc_datetime (datetime)
# - msg_start_index (int) → index where message text starts
# - tz_offset_hours (int) → parsed timezone offset
#
def parse_datetime_with_tz(args: List[str]) -> Tuple[datetime, int, int]:
    if len(args) < 2:
        raise ValueError("Not enough arguments for date/time timer")

    date_str = args[0]
    time_str = args[1]

    # --------------------------------------------------
    # Parse date and time
    # --------------------------------------------------
    try:
        naive = datetime.strptime(
            f"{date_str} {time_str}", "%d.%m.%Y %H:%M"
        )
    except ValueError as e:
        raise ValueError(
            "Bad date/time format, use DD.MM.YYYY HH:MM"
        ) from e

    tz_offset_hours = 0
    msg_start_index = 2

    # --------------------------------------------------
    # Optional timezone parsing
    # --------------------------------------------------
    if len(args) >= 3 and (
        args[2].upper().startswith("UTC")
        or args[2].upper().startswith("GMT")
    ):
        tz_token = args[2].upper()
        msg_start_index = 3

        offset_part = (
            tz_token.replace("UTC", "")
            .replace("GMT", "")
            .strip()
            or "+0"
        )

        sign = 1
        if offset_part.startswith("+"):
            offset_part = offset_part[1:]
        elif offset_part.startswith("-"):
            sign = -1
            offset_part = offset_part[1:]

        try:
            value = int(offset_part)
        except ValueError as e:
            raise ValueError(
                "Bad timezone format, use UTC+3 / GMT+1"
            ) from e

        tz_offset_hours = sign * value

    # --------------------------------------------------
    # Normalize to UTC
    # --------------------------------------------------
    tz = timezone(timedelta(hours=tz_offset_hours))
    aware = naive.replace(tzinfo=tz)
    target_utc = aware.astimezone(timezone.utc)

    return target_utc, msg_start_index, tz_offset_hours
