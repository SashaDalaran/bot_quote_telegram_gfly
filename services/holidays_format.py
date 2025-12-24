# ==================================================
# services/holidays_format.py — Holidays Message Formatter
# ==================================================
#
# This module is responsible for converting raw holiday
# data into a human-readable Telegram message.
#
# Responsibilities:
# - Take a list of holiday objects
# - Resolve country flags and category emojis
# - Build a clean, readable, multiline message
#
# IMPORTANT:
# - This module contains NO Telegram API code.
# - It only formats text.
# - All emojis and mappings are defined in:
#     services/holidays_flags.py
#
# ==================================================

from typing import List, Dict

from services.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

def _normalize_key(value: str) -> str:
    """Normalize mapping keys to match services/holidays_flags.py."""
    if value is None:
        return ""
    value = str(value).strip().lower()
    # Fix common Cyrillic lookalikes (e.g. 'Сhallenge' -> 'challenge')
    value = value.replace("с", "c")
    return value


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
            country_key = _normalize_key(countries[0])
            flag = COUNTRY_FLAGS.get(country_key, "🌍")
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
            category = categories[0]
            category_key = _normalize_key(category)
            emoji = CATEGORY_EMOJIS.get(category_key, "🔖")
            lines.append(f"{emoji} {category}")

        # Empty line between holidays
        lines.append("")

    # Join all lines into a single message
    return "\n".join(lines).strip()
