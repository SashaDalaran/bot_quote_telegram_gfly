# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone

from telegram.error import BadRequest
from telegram.ext import ContextTypes

from core.formatter import format_remaining, choose_update_interval

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    data = job.data

    chat_id = data["chat_id"]
    message_id = data["message_id"]
    target_time = data["target_time"]
    label = data.get("label", "")
    job_name = data["job_name"]

    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())

    # ⛔ ВРЕМЯ ВЫШЛО
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⏰ Время вышло!\n{label}".strip(),
            )
        except BadRequest:
            pass

        job.schedule_removal()
        return

    # ⏳ Обновляем текст
    text = f"⏳ {format_remaining(remaining)}"
    if label:
        text += f"\n{label}"

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except BadRequest:
        logger.warning("Failed to edit message for %s", job_name)

    # ⏱ Следующий тик — УМНЫЙ интервал
    interval = choose_update_interval(remaining)

    context.job_queue.run_once(
        countdown_tick,
        when=interval,
        name=job_name,
        data=data,
    )
