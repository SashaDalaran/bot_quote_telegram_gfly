# core/parser.py

from __future__ import annotations

import re
from typing import Optional, Tuple

_UNIT_SECONDS = {
    "s": 1,
    "sec": 1,
    "secs": 1,
    "second": 1,
    "seconds": 1,
    "m": 60,
    "min": 60,
    "mins": 60,
    "minute": 60,
    "minutes": 60,
    "h": 3600,
    "hr": 3600,
    "hrs": 3600,
    "hour": 3600,
    "hours": 3600,
    "d": 86400,
    "day": 86400,
    "days": 86400,
}


def _parse_duration_token(token: str) -> Optional[int]:
    """
    Supports:
      10s, 5m, 2h, 1d
      1h30m, 2m10s (combined)
    """
    token = token.strip().lower()
    if not token:
        return None

    # combined like 1h30m10s
    parts = re.findall(r"(\d+)\s*([a-z]+)", token)
    if not parts:
        # maybe just number => minutes by default
        if token.isdigit():
            return int(token) * 60
        return None

    total = 0
    for n_str, unit in parts:
        if unit not in _UNIT_SECONDS:
            return None
        total += int(n_str) * _UNIT_SECONDS[unit]

    return total if total > 0 else None


def parse_duration(raw: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Input: "10s tea" or "1h30m do something"
    Returns: (seconds, message)
    """
    raw = (raw or "").strip()
    if not raw:
        return None, None

    parts = raw.split()
    seconds = _parse_duration_token(parts[0])
    if seconds is None:
        return None, None

    message = " ".join(parts[1:]).strip() if len(parts) > 1 else None
    if message == "":
        message = None

    return seconds, message
