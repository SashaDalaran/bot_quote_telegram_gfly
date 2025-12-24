# core/timers.py
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import add_timer, get_timers, pop_last_timer, clear_timers
from core.countdown import countdown_tick
from core.formatter import choose_update_interval


def _make_job_name(chat_id: int, message_id: int) -> str:
    return f"timer:{chat_id}:{message_id}:{uuid.uuid4().hex[:8]}"


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message_id: int,
    message: Optional[str] = None,
) -> TimerEntry:
    if target_time.tzinfo is None:
        # treat naive as UTC
        target_time = target_time.replace(tzinfo=timezone.utc)

    job_name = _make_job_name(chat_id, message_id)

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=message_id,
        target_time=target_time.astimezone(timezone.utc),
        message=message,
        job_name=job_name,
        last_text=None,
    )

    add_timer(entry)

    remaining = int((entry.target_time - datetime.now(timezone.utc)).total_seconds())
    delay = choose_update_interval(max(remaining, 1))

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=job_name,
    )

    return entry


def cancel_last_timer(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> Optional[TimerEntry]:
    entry = pop_last_timer(chat_id)
    if not entry:
        return None

    if entry.job_name:
        for job in context.job_queue.get_jobs_by_name(entry.job_name):
            job.schedule_removal()

    return entry


def cancel_all_timers(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> int:
    timers = get_timers(chat_id)

    for entry in timers:
        if entry.job_name:
            for job in context.job_queue.get_jobs_by_name(entry.job_name):
                job.schedule_removal()

    return clear_timers(chat_id)
