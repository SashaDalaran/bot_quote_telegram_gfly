# core/timers.py

import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import format_remaining, choose_interval
from core.countdown import countdown_tick
from core.timers_store import add_timer

logger = logging.getLogger(__name__)


def _cancel_kb(job_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_timer:{job_name}")]]
    )


async def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    text: str = "",
    pin_message_id: int | None = None,  # оставил для совместимости (можешь не использовать)
) -> TimerEntry:
    """
    Создаёт сообщение таймера и запускает обновления через JobQueue.
    Совместимо с: await create_timer(...)
    """

    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())
    if remaining < 0:
        remaining = 0

    # 1) Отправляем сообщение (чтобы получить message_id)
    initial_text = f"⏰ Time left: {format_remaining(remaining)}"
    if text:
        initial_text += f"\n{text}"

    sent = await context.bot.send_message(chat_id=chat_id, text=initial_text)

    # 2) Делаем стабильное имя job (и для логов, и для cancel)
    job_name = f"timer:{chat_id}:{sent.message_id}"

    # 3) Вешаем кнопку cancel (через edit — так гарантированно прикрепим клаву)
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=sent.message_id,
            text=initial_text,
            reply_markup=_cancel_kb(job_name),
        )
    except Exception as e:
        logger.warning("Failed to attach cancel keyboard: %s", e)

    # 4) Entry (модель у тебя: chat_id, message_id, target_time, job_name, text)
    entry = TimerEntry(
        chat_id=chat_id,
        message_id=sent.message_id,
        target_time=target_time,
        job_name=job_name,
        text=text or "",
    )

    # доп. поля можно навесить динамически (модель менять не надо)
    entry.last_text = initial_text
    entry.cancelled = False
    entry.pin_message_id = pin_message_id

    add_timer(entry)

    # 5) Планируем первый тик
    delay = choose_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=job_name,
    )

    return entry
