# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone

from telegram.ext import ContextTypes

from core.formatter import format_duration
from core.models import TimerEntry

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    entry: TimerEntry = job.data

    now = datetime.now(timezone.utc)
    seconds_left = int((entry.target_time - now).total_seconds())

    # ================= TIME IS UP =================
    if seconds_left <= 0:
        text = "⏰ <b>Time is up!</b>"
        if entry.message:
            text += f"\n{entry.message}"

        await context.bot.send_message(
            chat_id=entry.chat_id,
            text=text,
            parse_mode="HTML",
        )

        if entry.pin_message_id:
            try:
                await context.bot.unpin_chat_message(
                    chat_id=entry.chat_id,
                    message_id=entry.pin_message_id,
                )
            except Exception:
                pass

        job.schedule_removal()
        return

    # ================= FORMAT =================
    time_str = format_duration(seconds_left)

    text = f"⏳ <b>{time_str}</b>"
    if entry.message:
        text += f"\n{entry.message}"

    # ================= UPDATE =================
    if text != getattr(entry, "last_text", None):
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=text,
                parse_mode="HTML",
            )
            entry.last_text = text
        except Exception as e:
            logger.debug("Edit skipped: %s", e)
