# ==================================================
# core/parser.py
# ==================================================
#
# Parsing helpers for timer commands.
#
# Supported formats:
#   /timer 10s message...
#   /timer 5m
#   /timer 2h tea
#   /timer 1d
#
# Units:
#   s (seconds), m (minutes), h (hours), d (days)
#
# NOTE: keep this strict on purpose: requiring a unit avoids surprises.
# ==================================================

from __future__ import annotations

from typing import List, Tuple


_UNIT_MULTIPLIERS = {
    "s": 1,
    "m": 60,
    "h": 60 * 60,
    "d": 24 * 60 * 60,
}


def parse_duration(token: str) -> int:
    """Parse a single duration token like '10s', '5m', '2h', '1d' -> seconds.

    Raises ValueError on invalid input.
    """
    token = (token or "").strip().lower()
    if not token:
        raise ValueError("Empty duration")

    unit = token[-1]
    value_str = token[:-1]

    if unit not in _UNIT_MULTIPLIERS:
        raise ValueError("Duration must end with unit: s/m/h/d")

    if not value_str.isdigit():
        raise ValueError("Duration value must be an integer")

    value = int(value_str)
    if value <= 0:
        raise ValueError("Duration must be > 0")

    return value * _UNIT_MULTIPLIERS[unit]


def parse_timer(args: List[str]) -> Tuple[int, str]:
    """Parse PTB args for /timer command: returns (seconds, message)."""
    if not args:
        raise ValueError("Usage: /timer 10s [message]")

    seconds = parse_duration(args[0])
    message = " ".join(args[1:]).strip()
    return seconds, message
