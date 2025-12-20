# core/countdown.py
import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.timers_store import remove_entry

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    if remaining <= 0:
        try:
            await context.bot.send_message(
                chat_id=entry.chat_id,
                text=f"⏰ Time is up!\n{entry.message or ''}",
            )
        except Exception as e:
            logger.warning("Failed to send timer message: %s", e)

        remove_entry(entry)
        return

    # НЕ ДЕЛАЕМ апдейты каждую секунду — просто ждём
    context.job_queue.run_once(
        countdown_tick,
        when=min(remaining, 5),
        data=entry,
        name=entry.job_name,
    )
