# core/countdown.py

import logging
import math
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time, choose_update_interval
from core.timers_store import get_entry, remove_entry

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data

    # ✅ CEIL чтобы не "съедать" секунды и не прыгать
    now = datetime.now(timezone.utc)
    remaining = math.ceil((entry.target_time - now).total_seconds())

    # ---- FINISH ----
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        # подчистим запись таймера (если храните)
        try:
            remove_entry(entry.job_name)
        except Exception:
            pass

        return

    # ---- BUILD TEXT ----
    new_text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if getattr(entry, "message", None):
        new_text += f"\n{entry.message}"

    # ---- UPDATE MESSAGE ----
    try:
        # не спамим edit если текст не менялся
        if getattr(entry, "last_text", None) != new_text:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=new_text,
            )
            entry.last_text = new_text
    except Exception as e:
        logger.warning("Edit failed (maybe message not modified / too old / etc): %s", e)

    # ---- RESCHEDULE ----
    delay = choose_update_interval(remaining)

    # safety: никогда не планируем больше чем осталось, и минимум 1 сек
    delay = max(1, min(delay, remaining))

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )
