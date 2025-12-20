# core/countdown.py
import logging
from datetime import datetime, timezone

from telegram.ext import ContextTypes

from core.formatter import format_remaining_time, choose_update_interval
from core.timers_store import get_entry, remove_entry

logger = logging.getLogger(__name__)

async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    entry = context.job.data
    now = datetime.now(timezone.utc)

    remaining = int((entry.target_time - now).total_seconds())

    # ⛔ время вышло
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        remove_entry(entry.chat_id, entry.job_name)
        return

    # ⏳ обновляем текст
    new_text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if entry.message:
        new_text += f"\n{entry.message}"

    if new_text != entry.last_text:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=new_text,
            )
            entry.last_text = new_text
        except Exception as e:
            logger.warning("Edit failed: %s", e)

    # 🔁 перепланируем СЕБЯ
    delay = choose_update_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )
