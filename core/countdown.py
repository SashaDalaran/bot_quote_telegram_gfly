# core/countdown.py
import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.timers_store import remove_entry
from core.formatter import format_remaining_time

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    if remaining <= 0:
        try:
            await context.bot.send_message(
                chat_id=entry.chat_id,
                text="⏰ Time is up!" + (f"\n{entry.text}" if entry.text else ""),
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        remove_entry(entry)
        return

    # одноразовый таймер — больше не обновляем
