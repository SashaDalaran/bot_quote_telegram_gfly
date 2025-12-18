# ==================================================
# core/countdown.py — Adaptive Countdown Logic
# ==================================================

import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time

logger = logging.getLogger(__name__)


def next_delay(remaining: int) -> int:
    """
    <= 1 minute      -> every 1 second
    1–10 minutes     -> every 5 seconds
    10–60 minutes    -> every 15 seconds
    >= 1 hour        -> every 60 seconds
    """
    if remaining <= 60:
        return 1
    if remaining <= 10 * 60:
        return 5
    if remaining <= 60 * 60:
        return 15
    return 60


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ================= FINISH =================
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)
        return

    # ================= TEXT =================
    new_text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if entry.message:
        new_text += f"\n{entry.message}"

    delay = next_delay(remaining)

    # ================= SKIP SAME TEXT =================
    # ❗ экономим апдейты, но НЕ в последние 60 секунд
    if remaining > 60 and entry.last_text == new_text:
        context.application.job_queue.run_once(
            countdown_tick,
            delay,
            name=entry.job_name,
            data=entry,
        )
        return

    # ================= UPDATE =================
    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=new_text,
        )
        entry.last_text = new_text
    except Exception as e:
        logger.warning("Update failed: %s", e)

    # ================= NEXT =================
    context.application.job_queue.run_once(
        countdown_tick,
        delay,
        name=entry.job_name,
        data=entry,
    )
