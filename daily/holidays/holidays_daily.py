# ==================================================
# daily/holidays/holidays_daily.py
# Telegram Daily Holidays (10:01)
# ==================================================

import os
from datetime import datetime, time, timezone, timedelta
from telegram.ext import Application

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
async def send_holidays_daily(context):
    """
    Send today's holidays to configured channels
    """
    today = datetime.now(TZ).date()

    # 🛡 защита от дублей
    last_sent = context.bot_data.get("holidays_last_sent")
    if last_sent == today:
        return

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

    # ✅ фиксируем успешную отправку
    context.bot_data["holidays_last_sent"] = today


# ===========================
# Job registration
# ===========================
def setup_holidays_daily(application: Application):
    # 🕙 ежедневная отправка
    application.job_queue.run_daily(
        send_holidays_daily,
        time=time(hour=10, minute=1, tzinfo=TZ),
        name="holidays_daily",
    )

    # 🔁 catch-up при старте машины
    application.create_task(holidays_catch_up(application))


# ===========================
# Catch-up logic
# ===========================
async def holidays_catch_up(application: Application):
    """
    If bot started after daily time — send holidays immediately
    """
    today = datetime.now(TZ).date()
    last_sent = application.bot_data.get("holidays_last_sent")

    if last_sent == today:
        return

    class Ctx:
        bot = application.bot
        bot_data = application.bot_data

    await send_holidays_daily(Ctx())
