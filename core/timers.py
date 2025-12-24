# ==================================================
# core/timers.py — Timer creation helper
# ==================================================

import logging
from datetime import datetime, timezone

from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.countdown import countdown_tick
from core.timers_store import add_timer

logger = logging.getLogger(__name__)


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str | None = None,
    *,
    message_id: int | None = None,
    pin_message_id: int | None = None,  # оставил для совместимости (если где-то ещё используется)
) -> TimerEntry:
    """
    Создаёт таймер и запускает первый тик countdown.

    ВАЖНО:
    - message_id: это ID сообщения таймера, которое мы будем edit'ить
    - pin_message_id: опционально, оставлен чтобы не ломать старый код
    """

    if target_time.tzinfo is None:
        # чтобы не было сюрпризов, приводим к UTC
        target_time = target_time.replace(tzinfo=timezone.utc)

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=message_id,
        target_time=target_time,
        message=message,
        pin_message_id=pin_message_id,
        last_text=None,
    )

    add_timer(entry)

    # Первый тик — почти сразу
    context.job_queue.run_once(
        countdown_tick,
        when=0.5,
        data=entry,
        name=entry.job_name,
    )

    logger.info("Timer created: %s", entry.job_name)
    return entry
