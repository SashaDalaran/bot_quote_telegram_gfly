# ==================================================
# daily/holidays/holidays_daily.py — Daily Holidays Job
# ==================================================
#
# This module defines a scheduled daily job
# that sends a list of today's holidays to
# one or more Telegram channels.
#
# Schedule:
# - Daily message at 10:01 (local timezone)
# - One-time catch-up message shortly after bot startup
#
# Responsibilities:
# - Determine the current date in the configured timezone
# - Retrieve holidays for the current date
# - Format the holidays into a single message
# - Send the message to all configured channels
# - Store the last sent date in bot_data
#
# IMPORTANT:
# - This module contains NO business logic.
# - Holiday calculation is handled by:
#     services/holidays_service.py
# - Message formatting is handled by:
#     services/holidays_format.py
#
# ==================================================

import os
from datetime import time, timezone, timedelta, datetime

from telegram.ext import Application, ContextTypes

from services.holidays_service import get_today_holidays
from services.holidays_format import format_holidays_message
from services.channel_ids import parse_chat_ids

# ==================================================
# Configuration
# ==================================================
#
# Timezone used for scheduling and date calculation.
# GMT+3 is used to match the target audience.
#

TZ = timezone(timedelta(hours=3))  # GMT+3

# --------------------------------------------------
# Target channel IDs
# --------------------------------------------------
#
# Channel ids are loaded from env HOLIDAYS_CHANNEL_ID (comma-separated allowed).
#
# Format:
#   HOLIDAYS_CHANNEL_ID=123456789,-100987654321
#
# Multiple channel IDs are supported.
#

HOLIDAYS_CHANNEL_IDS = parse_chat_ids("HOLIDAYS_CHANNEL_ID")

# ==================================================
# Job callback
# ==================================================
#
# This coroutine is executed by JobQueue.
# It sends today's holidays to all configured channels.
#
async def send_holidays_daily(context: ContextTypes.DEFAULT_TYPE):

    # Do nothing if no target channels are configured
    if not HOLIDAYS_CHANNEL_IDS:
        return

    # Determine today's date using the configured timezone
    today = datetime.now(TZ).date()

    # Retrieve holidays for today using the service layer
    holidays = get_today_holidays(today)

    # Do nothing if there are no holidays today
    if not holidays:
        return

    # Format holidays into a single Telegram message
    message = format_holidays_message(holidays)

    # Send the message to all configured channels
    for chat_id in HOLIDAYS_CHANNEL_IDS:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            disable_web_page_preview=True,
        )

    # Store the date of the last successful send
    context.bot_data["holidays_last_sent"] = today

# ==================================================
# Job registration
# ==================================================
#
# Registers scheduled jobs in the application's JobQueue.
#
def setup_holidays_daily(application: Application):

    # --------------------------------------------------
    # Main daily job
    # --------------------------------------------------
    #
    # Runs every day at 10:01 (TZ).
    # A small offset from Ban’Lu (10:00) is intentional
    # to avoid simultaneous message sending.
    #
    application.job_queue.run_daily(
        send_holidays_daily,
        time=time(hour=10, minute=1, tzinfo=TZ),
        name="holidays_daily",
    )

    # --------------------------------------------------
    # Catch-up job
    # --------------------------------------------------
    #
    # Runs ONCE shortly after bot startup.
    # Useful when the bot was restarted after
    # the scheduled daily time.
    #
    application.job_queue.run_once(
        send_holidays_daily,
        when=7,  # seconds after startup
        name="holidays_catch_up",
    )
