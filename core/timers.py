# ==================================================
# core/timers.py
# ==================================================

import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import choose_update_interval
from core.countdown import countdown_tick

logger = logging.getLogger(__name__)


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    chat_id: int,
    target_time: datetime,
    message_id: int,
    message: str | None,
    pin_message_id: int | None,
) -> str:
    """
    Create one countdown timer job.
    """

    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)
    else:
        target_time = target_time.astimezone(timezone.utc)

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time,
        message_id=message_id,
        message=message,
        pin_message_id=pin_message_id,
    )

    remaining = int((target_time - datetime.now(timezone.utc)).total_seconds())
    delay = choose_update_interval(remaining)

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )

    logger.info("Timer created: %s", entry.job_name)
    return entry.job_name


def cancel_all_timers(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> int:
    """
    Cancel all timers for chat.
    """
    removed = 0
    for job in context.job_queue.jobs():
        if job.name and job.name.startswith(f"timer:{chat_id}:"):
            job.schedule_removal()
            removed += 1

    logger.info("Cancelled %s timers for chat %s", removed, chat_id)
    return removed
