# ==================================================
# core/timers.py
# ==================================================

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import choose_interval
from core.countdown import countdown_tick
from core.timers_store import add_timer, clear_timers, get_timers

logger = logging.getLogger(__name__)


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        # Interpret naive datetime as UTC to keep behavior predictable on server.
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str,
    message_id: int,
) -> TimerEntry:
    """Create a timer and schedule countdown updates.

    message_id MUST be a bot-owned message id (i.e. a message sent by the bot),
    because we will edit it during the countdown.
    """
    target_time = _to_utc(target_time)

    job_name = f"timer:{chat_id}:{uuid.uuid4().hex}"

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time,
        message=message,
        job_name=job_name,
        message_id=message_id,
        last_text="",  # will be set by command handler to avoid a pointless first edit
    )

    add_timer(entry)

    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # Start ticking soon (not only at the very end).
    delay = choose_interval(max(remaining, 1))
    context.job_queue.run_once(countdown_tick, delay, data=entry, name=job_name)

    logger.info("Timer created: %s (remaining=%ss, first_delay=%ss)", job_name, remaining, delay)
    return entry


def cancel_all_timers(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> int:
    """Cancel and remove all timers for chat_id. Returns how many were removed."""
    entries = get_timers(chat_id)
    if not entries:
        return 0

    jobs = context.job_queue.jobs()
    removed = 0

    for entry in list(entries):
        job = next((j for j in jobs if j.name == entry.job_name), None)
        if job:
            job.schedule_removal()
        removed += 1

    clear_timers(chat_id)
    logger.info("Canceled %s timers for chat_id=%s", removed, chat_id)
    return removed
