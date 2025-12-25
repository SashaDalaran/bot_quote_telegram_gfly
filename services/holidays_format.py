# ==================================================
# services/holidays_format.py — Holidays Message Formatter
# ==================================================
#
# Formats holiday entries into Telegram-friendly text blocks.
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
import re
from typing import List, Dict

from services.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

def _normalize_key(value: str) -> str:
    """Normalize tokens to match keys in services/holidays_flags.py.

    We do NOT change holidays_flags.py; instead we normalize both the input token
    and the mapping keys into a comparable snake_case form.
    """
    if value is None:
        return ""
    s = str(value).strip()
    # Fix common Cyrillic lookalikes (e.g. 'Сhallenge' -> 'challenge')
    s = s.replace("С", "C").replace("с", "c")
    s = s.lower()
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


# Normalized lookup dicts (built from holidays_flags.py at import time)
_COUNTRY_FLAGS_NORM = {_normalize_key(k): v for k, v in COUNTRY_FLAGS.items()}
_CATEGORY_EMOJIS_NORM = {_normalize_key(k): v for k, v in CATEGORY_EMOJIS.items()}


# ==================================================
# Type aliases
# ==================================================
#
# A Holiday object is expected to be a dictionary
# with the following optional keys:
#
# - name: str
# - categories: list[str]
# - countries: list[str]
#
Holiday = Dict[str, object]

# ==================================================
# Message formatting
# ==================================================
#
# Builds a formatted Telegram message containing
# all holidays for a given day.
#
# Formatting rules:
# - The message starts with a fixed header
# - Each holiday is separated by an empty line
# - Only the FIRST country and category are displayed
# - Fallback emojis are used when data is missing
#
def format_holidays_message(holidays: List[Holiday]) -> str:

    # Message header
    """Service function: format holidays message."""
    lines = ["🎉 Today’s Holidays", ""]

    for holiday in holidays:
        name = holiday.get("name", "—")
        categories = holiday.get("categories", [])
        countries = holiday.get("countries", [])

        # --------------------------------------------------
        # Country / Flag resolution
        # --------------------------------------------------
        #
        # Only the first country is displayed.
        # If no country is provided or the key is unknown,
        # a generic global emoji is used.
        #
        if countries:
            flags = []
            for c in countries:
                key = _normalize_key(c)
                emoji = _COUNTRY_FLAGS_NORM.get(key)
                if emoji:
                    flags.append(emoji)
            flag = "".join(flags) if flags else "🌍"
        else:
            flag = "🌍"

        # Holiday name
        lines.append(f"{flag} {name}")

        # --------------------------------------------------
        # Category resolution
        # --------------------------------------------------
        #
        # Only the first category is displayed.
        # Unknown categories fall back to a generic label.
        #
        if categories:
            # show all categories (in order), each with its mapped emoji
            for category in categories:
                key = _normalize_key(category)
                emoji = _CATEGORY_EMOJIS_NORM.get(key, "🔖")
                lines.append(f"{emoji} {str(category).strip()}")

        # Empty line between holidays
        lines.append("")

    # Join all lines into a single message
    return "\n".join(lines).strip()