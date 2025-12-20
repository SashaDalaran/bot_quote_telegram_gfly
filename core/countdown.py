import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.formatter import format_remaining, choose_interval

logger = logging.getLogger(__name__)

async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ---- FINISH ----
    if remaining <= 0:
        try:
            text = "⏰ Time is up!"
            if entry.message:
                text += f"\n{entry.message}"

            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=text,
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)
        return

    # ---- UPDATE ----
    new_text = f"⏳ Time left: {format_remaining(remaining)}"
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

    delay = choose_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
    )
