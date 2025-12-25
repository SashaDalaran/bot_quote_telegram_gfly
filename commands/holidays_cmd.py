# ==================================================
# commands/holidays_cmd.py — Holidays Listing Command
# ==================================================
#
# User-facing /holidays handler; prints a short list of upcoming holidays.
#
# Layer: Commands
#
# Responsibilities:
# - Validate/parse user input (minimal)
# - Delegate work to services/core
# - Send user-facing responses via Telegram API
#
# Boundaries:
# - Commands do not implement business logic; they orchestrate user interaction.
# - Keep commands thin and deterministic; move reusable logic to services/core.
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
    """Command handler: format holiday."""
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
    """Handle the /holidays command."""
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