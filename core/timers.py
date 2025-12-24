# core/timers.py

import logging
from datetime import datetime, timezone
from uuid import uuid4

from telegram.ext import ContextTypes

from core.countdown import countdown_tick
from core.formatter import choose_update_interval
from core.models import TimerEntry
from core.timers_store import add_timer, remove_timer

logger = logging.getLogger(__name__)


def _cancel_job(context: ContextTypes.DEFAULT_TYPE, job_name: str) -> None:
    """Remove JobQueue job(s) by name if exist."""
    try:
        jobs = context.job_queue.get_jobs_by_name(job_name)
        for j in jobs:
            j.schedule_removal()
    except Exception as e:
        logger.warning("Cancel job failed (%s): %s", job_name, e)


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str | None,
    message_id: int,
    pin_message_id: int | None = None,
) -> TimerEntry:
    """
    Create a timer and schedule countdown updates.
    message_id MUST be the bot's message id (the one we will edit).
    """
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)

    job_name = f"timer:{chat_id}:{uuid4().hex}"

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=message_id,
        target_time=target_time,
        job_name=job_name,
        message=message or None,
        pin_message_id=pin_message_id,
        last_text=None,
    )

    add_timer(entry)

    remaining = int((target_time - datetime.now(timezone.utc)).total_seconds())
    delay = choose_update_interval(remaining)

    context.job_queue.run_once(countdown_tick, delay, data=entry, name=job_name)

    return entry


def cancel_timer(context: ContextTypes.DEFAULT_TYPE, chat_id: int, job_name: str) -> bool:
    """Cancel a specific timer by job_name."""
    _cancel_job(context, job_name)
    removed = remove_timer(chat_id, job_name)
    return removed is not None
