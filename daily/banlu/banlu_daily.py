# ==================================================
# daily/banlu/banlu_daily.py
# Telegram Daily Ban’Lu Quote (10:00)
# ==================================================

import os
from datetime import datetime, time, timezone, timedelta
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
    """
    Send daily Ban'Lu quote
    """
    if BANLU_CHANNEL_ID == 0:
        return

    today = datetime.now(TZ).date()

    # 🛡 защита от дублей
    last_sent = context.bot_data.get("banlu_last_sent")
    if last_sent == today:
        return

    quotes = context.bot_data.get("banlu_quotes", [])
    quote = get_random_banlu_quote(quotes)

    if not quote:
        return

    await context.bot.send_message(
        chat_id=BANLU_CHANNEL_ID,
        text=format_banlu_message(quote),
    )

    # ✅ фиксируем успешную отправку
    context.bot_data["banlu_last_sent"] = today


# ===========================
# Job registration
# ===========================
def setup_banlu_daily(application: Application):
    # 🕙 ежедневная отправка
    application.job_queue.run_daily(
        send_banlu_daily,
        time=time(hour=10, minute=0, tzinfo=TZ),
        name="banlu_daily",
    )

    # 🔁 catch-up при старте машины
    application.create_task(banlu_catch_up(application))


# ===========================
# Catch-up logic
# ===========================
async def banlu_catch_up(application: Application):
    """
    If bot started after daily time — send quote immediately
    """
    today = datetime.now(TZ).date()
    last_sent = application.bot_data.get("banlu_last_sent")

    if last_sent == today:
        return

    class Ctx:
        bot = application.bot
        bot_data = application.bot_data

    await send_banlu_daily(Ctx())
