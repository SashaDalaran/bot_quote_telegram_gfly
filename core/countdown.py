# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import choose_update_interval

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    entry: TimerEntry = job.data

    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    bot = context.bot

    # ===== TIMER FINISHED =====
    if remaining <= 0:
        text = "⏰ <b>Time is up!</b>"
        if entry.message:
            text += f"\n{entry.message}"

        try:
            await bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning("Final edit failed: %s", e)

        if entry.pin_message_id:
            try:
                await bot.unpin_chat_message(
                    chat_id=entry.chat_id,
                    message_id=entry.pin_message_id,
                )
            except Exception as e:
                logger.warning("Unpin failed: %s", e)

        return  # ❗ job уже удалён автоматически

    # ===== UPDATE MESSAGE =====
    text = f"⏳ <b>Осталось:</b> {remaining} сек."
    if entry.message:
        text += f"\n{entry.message}"

    try:
        await bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=text,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Edit failed: %s", e)

    # ===== SCHEDULE NEXT TICK (NEW JOB) =====
    delay = choose_update_interval(remaining)

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )
