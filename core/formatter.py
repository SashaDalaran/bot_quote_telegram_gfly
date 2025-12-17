# ==================================================
# core/formatter.py — Time Formatting & Update Strategy
# ==================================================
#
# This module contains helper utilities related to
# time formatting and adaptive update intervals.
#
# Responsibilities:
# - Convert a duration in seconds into a human-readable string
# - Decide how frequently countdown messages should be updated
#
# IMPORTANT:
# - This module contains NO Telegram-specific code
# - It is pure utility logic used by core countdown/timers
#
# ==================================================

from datetime import timedelta

# ==================================================
# Duration formatting
# ==================================================
#
# Converts a duration in seconds into a compact,
# human-readable string.
#
# Format:
# - days    → "д"
# - hours   → "ч"
# - minutes → "м"
# - seconds → "с"
#
# Example outputs:
# - 45        → "45с"
# - 125       → "2м 5с"
# - 3725      → "1ч 2м 5с"
# - 90061     → "1д 1ч 1м 1с"
#
def format_duration(seconds: int) -> str:

    # Safety guard: negative durations are treated as zero
    if seconds < 0:
        seconds = 0

    delta = timedelta(seconds=seconds)

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    parts: list[str] = []

    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes:
        parts.append(f"{minutes}м")

    # Seconds are always displayed
    parts.append(f"{secs}с")

    return " ".join(parts)

# ==================================================
# Adaptive update interval strategy
# ==================================================
#
# Determines how often a countdown message should
# be updated based on remaining time.
#
# UX strategy:
# - Very short timers → high precision (every second)
# - Medium timers     → balanced updates
# - Long timers       → minimal noise
#
def choose_update_interval(seconds_left: int) -> int:

    # Final minute: update every second
    if seconds_left <= 60:
        return 1

    # Up to 5 minutes: frequent but not noisy
    if seconds_left <= 5 * 60:
        return 5

    # Up to 1 hour: occasional updates
    if seconds_left <= 60 * 60:
        return 30

    # Long timers: keep updates minimal
    return 60
