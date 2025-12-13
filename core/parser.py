from datetime import datetime, timedelta, timezone
from typing import List, Tuple


def parse_duration(text: str) -> int:
    """
    Parse duration strings like:
    '5' (minutes), '10s', '1h30m', '2h', '90m', '1h15m30s'
    Returns seconds.
    """
    text = text.strip().lower()
    if not text:
        raise ValueError("Empty duration")

    # plain number = minutes
    if text.isdigit():
        minutes = int(text)
        if minutes <= 0:
            raise ValueError("Duration must be > 0")
        return minutes * 60

    total = 0
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
            total += value * 86400
        elif ch == "h":
            total += value * 3600
        elif ch == "m":
            total += value * 60
        elif ch == "s":
            total += value
        else:
            raise ValueError(f"Unknown duration unit: {ch}")

    if number:
        # leftover number with no unit -> minutes
        total += int(number) * 60

    if total <= 0:
        raise ValueError("Duration must be > 0")

    return total


def parse_datetime_with_tz(args: List[str]) -> Tuple[datetime, int, int]:
    """
    Parse absolute date/time from args:
    [DD.MM.YYYY, HH:MM, [TZ], ...message_words]

    TZ examples:
      UTC+3, GMT+1, UTC-2, GMT-0

    Returns:
      (target_utc_datetime, msg_start_index, tz_offset_hours)
    """
    if len(args) < 2:
        raise ValueError("Not enough arguments for date/time timer")

    date_str = args[0]
    time_str = args[1]

    try:
        naive = datetime.strptime(
            f"{date_str} {time_str}", "%d.%m.%Y %H:%M"
        )
    except ValueError as e:
        raise ValueError(
            "Bad date/time format, use DD.MM.YYYY HH:MM"
        ) from e

    tz_offset_hours = 0
    msg_start = 2

    if len(args) >= 3 and (
        args[2].upper().startswith("UTC")
        or args[2].upper().startswith("GMT")
    ):
        tz_token = args[2].upper()
        msg_start = 3

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

    tz = timezone(timedelta(hours=tz_offset_hours))
    aware = naive.replace(tzinfo=tz)
    target_utc = aware.astimezone(timezone.utc)

    return target_utc, msg_start, tz_offset_hours
