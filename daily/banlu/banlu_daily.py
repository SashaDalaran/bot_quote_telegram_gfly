# ==================================================
# daily/banlu/banlu_daily.py — Daily Ban’Lu Quote Job
# ==================================================
#
# This module defines a scheduled daily job
# that sends a Ban’Lu quote to a Telegram channel.
#
# Schedule:
# - Daily message at 10:00 (local timezone)
# - One-time catch-up message shortly after bot startup
#
# Responsibilities:
# - Select a random Ban’Lu quote
# - Format the message
# - Send it to a configured Telegram channel
# - Store the last sent date in bot_data
#
# IMPORTANT:
# - This module contains NO business logic.
# - Quote selection and formatting are handled
#   by services/banlu_service.py
#
# ==================================================

import os
from datetime import time, timezone, timedelta, datetime

from telegram.ext import Application, ContextTypes

from services.banlu_service import (
    get_random_banlu_quote,
    format_banlu_message,
)

# ==================================================
# Configuration
# ==================================================
#
# Timezone used for scheduling the daily job.
# GMT+3 is used to match the target audience.
#
# BANLU_CHANNEL_ID:
# - Telegram channel ID where messages are sent
# - Must be provided via environment variables
#

TZ = timezone(timedelta(hours=3))  # GMT+3
BANLU_CHANNEL_ID = int(os.getenv("BANLU_CHANNEL_ID", "0"))

# ==================================================
# Job callback
# ==================================================
#
# This coroutine is executed by JobQueue.
# It sends one Ban’Lu quote to the configured channel.
#
async def send_banlu_daily(context: ContextTypes.DEFAULT_TYPE):
    # Retrieve preloaded Ban’Lu quotes from bot_data
    quotes = context.bot_data.get("banlu_quotes", [])

    # Select a random quote using the service layer
    quote = get_random_banlu_quote(quotes)

    # Safety check:
    # - Do nothing if quotes list is empty
    # - Do nothing if channel ID is not configured
    if not quote or not BANLU_CHANNEL_ID:
        return

    # Send formatted message to the Telegram channel
    await context.bot.send_message(
        chat_id=BANLU_CHANNEL_ID,
        text=format_banlu_message(quote),
    )

    # Store the date of the last successful send
    context.bot_data["banlu_last_sent"] = datetime.now(TZ).date()

# ==================================================
# Job registration
# ==================================================
#
# Registers scheduled jobs in the application's JobQueue.
#
def setup_banlu_daily(application: Application):

    # --------------------------------------------------
    # Main daily job
    # --------------------------------------------------
    #
    # Runs every day at 10:00 (TZ)
    #
    application.job_queue.run_daily(
        send_banlu_daily,
        time=time(hour=10, minute=0, tzinfo=TZ),
        name="banlu_daily",
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
        send_banlu_daily,
        when=5,  # seconds after startup
        name="banlu_catch_up",
    )
