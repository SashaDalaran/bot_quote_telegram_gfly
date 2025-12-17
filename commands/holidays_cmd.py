# ==================================================
# commands/holidays_cmd.py — Holidays Listing Command
# ==================================================
#
# This module defines the user-facing command
# for displaying upcoming holidays.
#
# Command:
# - /holidays → shows a short list of upcoming holidays
#
# Responsibilities:
# - Retrieve holiday data from the service layer
# - Format each holiday into a readable message block
# - Send a single combined message to the user
#
# IMPORTANT:
# - This module contains NO holiday calculation logic
# - It relies entirely on services.holidays_service
# - Formatting here is lightweight and command-specific
#
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from services.holidays_service import load_all_holidays
from services.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

# ==================================================
# Single holiday formatter (command-level)
# ==================================================
#
# Converts a single holiday dictionary into
# a short Markdown-formatted message block.
#
# Display rules:
# - Only the first country flag is shown
# - Only the first category is shown
# - Date is displayed in "DD Month" format
#
def format_holiday(holiday: dict) -> str:

    # --------------------------------------------------
    # Country / flag resolution
    # --------------------------------------------------
    country = holiday["countries"][0] if holiday["countries"] else ""
    flag = COUNTRY_FLAGS.get(country, "🌍")

    # --------------------------------------------------
    # Category / emoji resolution
    # --------------------------------------------------
    category = holiday["categories"][0] if holiday["categories"] else ""
    emoji = CATEGORY_EMOJIS.get(category, "")

    # --------------------------------------------------
    # Date formatting
    # --------------------------------------------------
    date_str = holiday["parsed_date"].strftime("%d %B")

    lines = [
        f"{flag} *{holiday['name']}*",
        f"📅 {date_str}",
    ]

    # Insert category line only if present
    if category:
        lines.insert(
            1,
            f"{emoji} {category}" if emoji else category,
        )

    return "\n".join(lines)

# ==================================================
# /holidays command
# ==================================================
#
# Displays a list of upcoming holidays.
#
# Behavior:
# - Holidays are loaded from all sources (static + dynamic)
# - Only one holiday per source is shown
#   (to avoid overwhelming the user)
#
async def holidays_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    holidays = load_all_holidays()

    if not holidays:
        await update.message.reply_text("❌ No holidays found")
        return

    message = ["📅 *Upcoming Holidays*\n"]

    shown_sources = set()

    for holiday in holidays:
        # --------------------------------------------------
        # Source deduplication
        # --------------------------------------------------
        #
        # Each JSON file or dynamic generator is treated
        # as a separate source.
        #
        # Only the first holiday from each source
        # is displayed in this command.
        #
        if holiday["source"] in shown_sources:
            continue

        message.append(format_holiday(holiday))
        message.append("")
        shown_sources.add(holiday["source"])

    await update.message.reply_text(
        "\n".join(message),
        parse_mode="Markdown",
    )
