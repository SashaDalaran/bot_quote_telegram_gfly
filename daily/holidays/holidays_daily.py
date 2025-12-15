# ==================================================
# daily/holidays/holidays_daily.py
# Telegram Daily Holidays (10:01)
# ==================================================

import os
from datetime import time, timezone, timedelta, datetime
from telegram.ext import Application, ContextTypes

from services.holidays_service import get_today_holidays
from services.holidays_format import format_holidays_message

# ===========================
# Configuration
# ===========================
TZ = timezone(timedelta(hours=3))  # GMT+3

HOLIDAYS_CHANNEL_IDS = [
    int(cid)
    for cid in os.getenv("HOLIDAYS_CHANNEL_IDS", "").split(",")
    if cid.strip().isdigit()
]

# ===========================
# Job callback
# ===========================
async def send_holidays_daily(context: ContextTypes.DEFAULT_TYPE):
    if not HOLIDAYS_CHANNEL_IDS:
        return

    today = datetime.now(TZ).date()
    holidays = get_today_holidays(today)

    if not holidays:
        return

    message = format_holidays_message(holidays)

    for chat_id in HOLIDAYS_CHANNEL_IDS:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            disable_web_page_preview=True,
        )

    context.bot_data["holidays_last_sent"] = today

# ===========================
# Job registration
# ===========================
def setup_holidays_daily(application: Application):
    application.job_queue.run_daily(
        send_holidays_daily,
        time=time(hour=10, minute=1, tzinfo=TZ),
        name="holidays_daily",
    )

    # catch-up
    application.job_queue.run_once(
        send_holidays_daily,
        when=7,
        name="holidays_catch_up",
    )
