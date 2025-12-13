# ==================================================
# daily/banlu/banlu_daily.py
# Telegram Daily Ban’Lu Quote (10:00)
# ==================================================

import os
from datetime import time, timezone, timedelta

from telegram.ext import Application

from services.banlu_service import (
    get_random_banlu_quote,
    format_banlu_message,
)

# ===========================
# Configuration
# ===========================
TZ = timezone(timedelta(hours=3))  # GMT+3
BANLU_CHANNEL_ID = int(os.getenv("BANLU_CHANNEL_ID", "0"))


# ===========================
# Job callback
# ===========================
async def send_banlu_daily(context):
    quotes = context.bot_data.get("banlu_quotes", [])
    quote = get_random_banlu_quote(quotes)

    if not quote:
        return

    await context.bot.send_message(
        chat_id=BANLU_CHANNEL_ID,
        text=format_banlu_message(quote),
    )


# ===========================
# Job registration
# ===========================
def setup_banlu_daily(application: Application):
    """
    Schedule Ban’Lu daily message at 10:00 GMT+3
    """
    application.job_queue.run_daily(
        send_banlu_daily,
        time=time(hour=10, minute=0, tzinfo=TZ),
        name="banlu_daily",
    )
