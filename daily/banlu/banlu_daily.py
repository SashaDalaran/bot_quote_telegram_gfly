# ==================================================
# daily/banlu/banlu_daily.py
# Telegram Daily Ban’Lu Quote (10:00)
# ==================================================

import os
from datetime import time, timezone, timedelta, datetime
from telegram.ext import Application, ContextTypes

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
async def send_banlu_daily(context: ContextTypes.DEFAULT_TYPE):
    quotes = context.bot_data.get("banlu_quotes", [])
    quote = get_random_banlu_quote(quotes)

    if not quote or not BANLU_CHANNEL_ID:
        return

    await context.bot.send_message(
        chat_id=BANLU_CHANNEL_ID,
        text=format_banlu_message(quote),
    )

    context.bot_data["banlu_last_sent"] = datetime.now(TZ).date()

# ===========================
# Job registration
# ===========================
def setup_banlu_daily(application: Application):
    # основной ежедневный job
    application.job_queue.run_daily(
        send_banlu_daily,
        time=time(hour=10, minute=0, tzinfo=TZ),
        name="banlu_daily",
    )

    # catch-up job (ОДИН РАЗ после старта)
    application.job_queue.run_once(
        send_banlu_daily,
        when=5,  # через 5 секунд после запуска
        name="banlu_catch_up",
    )
