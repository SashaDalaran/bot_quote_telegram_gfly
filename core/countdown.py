# core/countdown.py
from __future__ import annotations

import logging
from datetime import datetime, timezone

from telegram.ext import ContextTypes

from core.formatter import format_remaining_time, choose_update_interval
from core.timers_store import remove_timer

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ---- FINISH ----
    if remaining <= 0:
        text = "⏰ Time is up!"
        if getattr(entry, "message", None):
            text += f"\n{entry.message}"

        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=text,
            )
        except Exception as e:
            logger.warning("Finalize edit failed: %s", e)
            try:
                await context.bot.send_message(chat_id=entry.chat_id, text=text)
            except Exception as e2:
                logger.warning("Finalize send failed: %s", e2)

        if getattr(entry, "job_name", None):
            remove_timer(entry.chat_id, entry.job_name)

        return

    # ---- BUILD TEXT ----
    new_text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if getattr(entry, "message", None):
        new_text += f"\n{entry.message}"

    # ---- EDIT (only if changed) ----
    if getattr(entry, "last_text", None) != new_text:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=new_text,
            )
            entry.last_text = new_text
        except Exception as e:
            logger.warning("Edit failed: %s", e)

    # ---- NEXT TICK ----
    delay = choose_update_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=getattr(entry, "job_name", None),
    )
