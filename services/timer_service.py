# ==================================================
# core/countdown.py — Countdown Job Logic
# ==================================================

import logging
from datetime import datetime, timezone

from telegram.ext import ContextTypes

from core.formatter import (
    choose_update_interval,
    format_remaining_time,
)

logger = logging.getLogger(__name__)

async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Single countdown job tick.
    Responsible ONLY for:
    - calculating remaining time
    - updating the timer message
    - rescheduling itself
    """

    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # --------------------------------------------------
    # Timer finished
    # --------------------------------------------------
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Failed to finalize timer: %s", e)
        return

    # --------------------------------------------------
    # Build new text
    # --------------------------------------------------
    new_text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if entry.message:
        new_text += f"\n{entry.message}"

    # --------------------------------------------------
    # 🔥 CRITICAL FIX — do NOT edit same text
    # --------------------------------------------------
    if entry.last_text == new_text:
        delay = choose_update_interval(remaining)
        context.application.job_queue.run_once(
            countdown_tick,
            delay,
            name=entry.job_name,
            data=entry,
        )
        return

    # --------------------------------------------------
    # Edit message
    # --------------------------------------------------
    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=new_text,
        )
        entry.last_text = new_text

    except Exception as e:
        msg = str(e).lower()

        # Telegram: message is not modified
        if "message is not modified" in msg or "400" in msg:
            logger.debug("Skipped edit (text unchanged)")
        else:
            logger.warning("Failed to update timer: %s", e)
    # --------------------------------------------------
    # Schedule next tick
    # --------------------------------------------------
    delay = choose_update_interval(remaining)
    context.application.job_queue.run_once(
        countdown_tick,
        delay,
        name=entry.job_name,
        data=entry,
    )
