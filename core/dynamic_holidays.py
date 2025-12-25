# ==================================================
# core/dynamic_holidays.py — Dynamic Holiday Calculations
# ==================================================
#
# Pure functions for holidays that cannot be represented as fixed calendar dates (e.g., Easter-based holidays).
#
# Layer: Core
#
# Responsibilities:
# - Provide reusable, testable logic and infrastructure helpers
# - Avoid direct Telegram API usage (except JobQueue callback signatures where required)
# - Expose stable APIs consumed by services and commands
#
# Boundaries:
# - Core must remain independent from user interaction details.
# - Core should not import commands (top layer) to avoid circular dependencies.
#
# ==================================================
from datetime import datetime, timedelta, date

# ==================================================
# Western (Catholic) Easter calculation
# ==================================================
#
# Calculates the date of Western (Catholic) Easter
# using the standard Gregorian computus algorithm.
#
# This implementation is deterministic and accurate
# for all modern Gregorian calendar years.
#
def _easter_western(year: int) -> date:
    """
    Calculate the date of Western (Catholic) Easter
    using the Gregorian computus.

    Returns:
        datetime.date: Easter Sunday for the given year
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451

    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1

    return date(year, month, day)

# ==================================================
# Orthodox Easter calculation (approximation)
# ==================================================
#
# Orthodox Easter is traditionally calculated
# using the Julian calendar.
#
# For bot-level accuracy, we approximate Orthodox
# Easter by adding a 13-day offset to Western Easter.
#
# This approximation is sufficient for:
# - holiday notifications
# - calendar-style usage
#
def _easter_orthodox(year: int) -> date:
    """
    Approximate Orthodox Easter by applying
    the Julian-to-Gregorian calendar offset.

    Returns:
        datetime.date: Approximate Orthodox Easter date
    """
    western = _easter_western(year)
    return western + timedelta(days=13)

# ==================================================
# Public API: Dynamic holidays
# ==================================================
#
# Returns dynamically calculated holidays in a
# normalized dictionary format.
#
# Current dynamic holidays:
# - Catholic Easter
# - Orthodox Easter
#
# If the calculated dates for the current year
# are already in the past, the function automatically
# shifts calculations to the next year.
#
def get_dynamic_holidays() -> list[dict]:
    """
    Return upcoming dynamic holidays.

    Each holiday dictionary contains:
    - full_date: YYYY-MM-DD
    - date: MM-DD
    - name: Human-readable holiday name
    - countries: Region / religion identifiers
    - categories: Holiday categories
    """

    today = datetime.now().date()
    year = today.year

    catholic = _easter_western(year)
    orthodox = _easter_orthodox(year)

    # If both holidays already passed this year,
    # calculate them for the next year
    if max(catholic, orthodox) < today:
        year += 1
        catholic = _easter_western(year)
        orthodox = _easter_orthodox(year)

    return [
        {
            "full_date": catholic.strftime("%Y-%m-%d"),
            "date": catholic.strftime("%m-%d"),
            "name": "Catholic Easter",
            "countries": ["catholic"],
            "categories": ["Religious"],
        },
        {
            "full_date": orthodox.strftime("%Y-%m-%d"),
            "date": orthodox.strftime("%m-%d"),
            "name": "Orthodox Easter",
            "countries": ["orthodox"],
            "categories": ["Religious"],
        },
    ]