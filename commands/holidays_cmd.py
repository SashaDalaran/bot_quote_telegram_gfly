# commands/holidays_cmd.py

from telegram import Update
from telegram.ext import ContextTypes

from services.holidays_service import load_all_holidays
from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS


def format_holiday(h: dict) -> str:
    country = h["countries"][0] if h["countries"] else ""
    flag = COUNTRY_FLAGS.get(country, "🌍")

    category = h["categories"][0] if h["categories"] else ""
    emoji = CATEGORY_EMOJIS.get(category, "")

    date_str = h["parsed_date"].strftime("%d %B")

    lines = [
        f"{flag} *{h['name']}*",
        f"📅 {date_str}",
    ]

    if category:
        lines.insert(1, f"{emoji} {category}" if emoji else category)

    return "\n".join(lines)


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

    for h in holidays:
        if h["source"] in shown_sources:
            continue

        message.append(format_holiday(h))
        message.append("")
        shown_sources.add(h["source"])

    await update.message.reply_text(
        "\n".join(message),
        parse_mode="Markdown",
    )
