# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone, timedelta

from telegram.error import BadRequest
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import choose_update_interval

logger = logging.getLogger(__name__)


def _format_remaining(seconds: int) -> str:
    """
    Human readable remaining time.
    """
    if seconds <= 0:
        return "⏰ Time is up!"

    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)

    if h > 0:
        return f"⏳ {h:02d}:{m:02d}:{s:02d}"
    return f"⏳ {m:02d}:{s:02d}"


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Single countdown job.
    Self-reschedules itself until finished.
    """
    entry: TimerEntry = context.job.data
    job = context.job

    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ================= FINISH =================
    if remaining <= 0:
        try:
            text = "⏰ Time is up!"
            if entry.message:
                text += f"\n\n{entry.message}"

            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.pin_message_id,
                text=text,
            )
        except BadRequest:
            pass

        # -------- UNPIN --------
        if entry.pin_message_id:
            try:
                await context.bot.unpin_chat_message(
                    chat_id=entry.chat_id,
                    message_id=entry.pin_message_id,
                )
            except Exception:
                pass

        logger.info("Timer finished: %s", job.name)
        job.schedule_removal()
        return

    # ================= UPDATE =================
    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.pin_message_id,
            text=_format_remaining(remaining),
        )
    except BadRequest:
        # message not modified / deleted
        pass

    # ================= RESCHEDULE =================
    delay = choose_update_interval(remaining)
    next_run = now + timedelta(seconds=delay)

    try:
        job.reschedule(trigger="date", run_date=next_run)
    except Exception:
        logger.exception("Failed to reschedule timer %s", job.name)
