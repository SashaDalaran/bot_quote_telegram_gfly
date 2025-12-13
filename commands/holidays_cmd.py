# ==================================================
# commands/holidays.py — Telegram /holidays command
# ==================================================

import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from core.dynamic_holidays import get_dynamic_holidays
from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

HOLIDAYS_PATH = "data/holidays"


# ===========================
# Load all holidays (static + dynamic)
# ===========================
def load_all_holidays():
    today = datetime.now().date()
    holidays = []

    # -------- static JSON holidays --------
    for filename in sorted(os.listdir(HOLIDAYS_PATH)):
        if not filename.endswith(".json"):
            continue

        with open(
            os.path.join(HOLIDAYS_PATH, filename),
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        for entry in data:
            mmdd = entry["date"]
            parsed_date = datetime.strptime(
                f"{today.year}-{mmdd}", "%Y-%m-%d"
            ).date()

            if parsed_date < today:
                parsed_date = parsed_date.replace(year=today.year + 1)

            categories = entry.get("category") or entry.get("categories") or []
            if isinstance(categories, str):
                categories = [categories]

            holidays.append(
                {
                    "name": entry["name"],
                    "date": mmdd,
                    "parsed_date": parsed_date,
                    "countries": entry.get("countries", []),
                    "categories": categories,
                    "source": filename,
                }
            )

    # -------- dynamic holidays --------
    for d in get_dynamic_holidays():
        full_date = datetime.strptime(d["full_date"], "%Y-%m-%d").date()

        holidays.append(
            {
                "name": d["name"],
                "date": d["date"],
                "parsed_date": full_date,
                "countries": d.get("countries", []),
                "categories": d.get("categories", []),
                "source": "dynamic",
            }
        )

    holidays.sort(key=lambda h: h["parsed_date"])
    return holidays


# ===========================
# Build message line
# ===========================
def format_holiday(h):
    country = h["countries"][0] if h["countries"] else ""
    flag = COUNTRY_FLAGS.get(country, "🌍")

    category = h["categories"][0] if h["categories"] else ""
    emoji = CATEGORY_EMOJIS.get(category, "")

    date_str = h["parsed_date"].strftime("%d %B")

    parts = [
        f"{flag} **{h['name']}**",
        f"📅 {date_str}",
    ]

    if category:
        parts.insert(1, f"{emoji} {category}" if emoji else category)

    return "\n".join(parts)


# ===========================
# Command: /holidays
# ===========================
async def holidays_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        holidays = load_all_holidays()
    except FileNotFoundError:
        await update.message.reply_text(
            "❌ Holidays data folder not found"
        )
        return

    if not holidays:
        await update.message.reply_text(
            "❌ No holidays found"
        )
        return

    message_lines = ["📅 **Upcoming Holidays**\n"]

    shown_sources = set()

    for h in holidays:
        if h["source"] in shown_sources:
            continue

        message_lines.append(format_holiday(h))
        message_lines.append("")  # blank line
        shown_sources.add(h["source"])

    await update.message.reply_text(
        "\n".join(message_lines),
        parse_mode="Markdown",
    )
