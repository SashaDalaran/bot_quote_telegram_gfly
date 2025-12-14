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


def create_timer(context: ContextTypes.DEFAULT_TYPE, entry: TimerEntry) -> str:
    # normalize timezone
    if entry.target_time.tzinfo is None:
        entry.target_time = entry.target_time.replace(tzinfo=timezone.utc)
    else:
        entry.target_time = entry.target_time.astimezone(timezone.utc)

    seconds_left = int(
        (entry.target_time - datetime.now(timezone.utc)).total_seconds()
    )
    seconds_left = max(0, seconds_left)

    interval = choose_update_interval(seconds_left)

    context.job_queue.run_repeating(
        countdown_tick,
        interval=interval,
        first=0,
        data=entry,
        name=entry.job_name,
    )

    logger.info("Timer started: %s", entry.job_name)
    return entry.job_name


def cancel_all_timers(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> int:
    removed = 0
    for job in context.job_queue.jobs():
        if job.name and job.name.startswith(f"timer:{chat_id}:"):
            job.schedule_removal()
            removed += 1
    return removed
