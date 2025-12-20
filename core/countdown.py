# core/countdown.py

import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time, choose_update_interval
from core.timers_store import get_timer, remove_timer

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ⛔ Время вышло
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        remove_timer(entry.job_name)
        return

    # ⏳ Обновляем сообщение
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

    # 🔁 Перепланируем себя
    delay = choose_update_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        name=entry.job_name,
        data=entry,
    )
