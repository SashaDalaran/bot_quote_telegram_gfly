# ==================================================
# core/timers.py
# ==================================================

import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import choose_update_interval
from core.scheduler import countdown_tick

logger = logging.getLogger(__name__)


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str,
    pin_message_id: int,
) -> str:
    """
    Create one-time countdown timer.
    """

    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)
    else:
        target_time = target_time.astimezone(timezone.utc)

    job_name = f"timer:{chat_id}:{int(target_time.timestamp())}"

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time,
        pin_message_id=pin_message_id,
        message=message,
        job_name=job_name,
    )

    remaining = int((target_time - datetime.now(timezone.utc)).total_seconds())
    delay = choose_update_interval(remaining)

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=job_name,
    )

    logger.info("Timer created: %s", job_name)
    return job_name


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