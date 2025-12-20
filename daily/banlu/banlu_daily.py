# daily/banlu/banlu_daily.py

import os
from datetime import time, timezone, timedelta, datetime, date

from telegram.ext import Application, ContextTypes

from services.banlu_service import (
    get_random_banlu_quote,
    format_banlu_message,
)

# ==================================================
# CONFIG
# ==================================================

TZ = timezone(timedelta(hours=3))  # GMT+3
BANLU_CHANNEL_ID = int(os.getenv("BANLU_CHANNEL_ID", "0"))

LAST_SENT_KEY = "banlu_last_sent"


# ==================================================
# INTERNAL GUARD
# ==================================================

def _already_sent_today(context: ContextTypes.DEFAULT_TYPE) -> bool:
    last: date | None = context.bot_data.get(LAST_SENT_KEY)
    today = datetime.now(TZ).date()
    return last == today


def _mark_sent_today(context: ContextTypes.DEFAULT_TYPE):
    context.bot_data[LAST_SENT_KEY] = datetime.now(TZ).date()


# ==================================================
# JOB CALLBACK
# ==================================================

async def send_banlu_daily(context: ContextTypes.DEFAULT_TYPE):
    # ❌ защита от дубля
    if _already_sent_today(context):
        return

    quotes = context.bot_data.get("banlu_quotes", [])
    quote = get_random_banlu_quote(quotes)

    if not quote or not BANLU_CHANNEL_ID:
        return

    await context.bot.send_message(
        chat_id=BANLU_CHANNEL_ID,
        text=format_banlu_message(quote),
    )

    _mark_sent_today(context)


# ==================================================
# JOB REGISTRATION
# ==================================================

def setup_banlu_daily(application: Application):
    # 📅 основной ежедневный job
    application.job_queue.run_daily(
        send_banlu_daily,
        time=time(hour=10, minute=0, tzinfo=TZ),
        name="banlu_daily",
    )

    # ⏱ catch-up только если реально не отправляли
    application.job_queue.run_once(
        send_banlu_daily,
        when=5,
        name="banlu_catch_up",
    )
