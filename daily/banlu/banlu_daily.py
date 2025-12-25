# daily/banlu/banlu_daily.py

import logging
import os
import asyncio
from datetime import time, timezone, timedelta, datetime, date

from telegram.ext import Application, ContextTypes
from telegram.error import NetworkError, TimedOut

from services.banlu_service import (
    get_random_banlu_quote,
    format_banlu_message,
)
from services.channel_ids import parse_chat_ids

# ==================================================
# CONFIG
# ==================================================

logger = logging.getLogger(__name__)

TZ = timezone(timedelta(hours=3))  # GMT+3
# Accept one or many chat IDs, comma-separated.
# Primary: BANLU_CHANNEL_ID
BANLU_CHANNEL_IDS = parse_chat_ids("BANLU_CHANNEL_ID")

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

async def _send_with_retry(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str) -> bool:
    """Best-effort send with short retries for transient Telegram/HTTP errors."""
    delays = (0.8, 2.0, 5.0)
    for attempt in range(len(delays) + 1):
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
            return True
        except (NetworkError, TimedOut) as e:
            logger.warning("Ban'Lu send failed (attempt %s/%s) for chat_id=%s: %s", attempt + 1, len(delays) + 1, chat_id, e)
            if attempt < len(delays):
                await asyncio.sleep(delays[attempt])
                continue
            return False
        except Exception as e:
            # Non-network errors: don't retry blindly
            logger.exception("Ban'Lu send failed (non-retry) for chat_id=%s: %s", chat_id, e)
            return False


async def send_banlu_daily(context: ContextTypes.DEFAULT_TYPE):
    # ❌ защита от дубля
    if _already_sent_today(context):
        return

    quotes = context.bot_data.get("banlu_quotes", [])
    quote = get_random_banlu_quote(quotes)

    if not quote or not BANLU_CHANNEL_IDS:
        return

    text = format_banlu_message(quote)

    any_success = False
    for chat_id in BANLU_CHANNEL_IDS:
        ok = await _send_with_retry(context, chat_id=chat_id, text=text)
        any_success = any_success or ok

    # Mark as sent only if at least one channel got it.
    if any_success:
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
