# core/timers.py

import uuid
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import add_timer, pop_last_timer, get_timers, clear_timers


def _to_utc(dt: datetime) -> datetime:
    """Normalize datetime to timezone-aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def create_timer(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str | None = None,
    pin_message_id: int | None = None,
) -> None:
    if pin_message_id is None:
        raise ValueError("pin_message_id is required (we edit that message later)")

    job_name = f"timer:{chat_id}:{uuid.uuid4().hex}"

    target_utc = _to_utc(target_time)

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=pin_message_id,
        target_time=target_utc,
        job_name=job_name,
        message=message,
        text=message,
        last_text=None,
    )

    add_timer(chat_id, entry)

    now = datetime.now(timezone.utc)
    delay = max(1, int((target_utc - now).total_seconds()))

    # ❗ импорт внутри функции — чтобы не было circular import
    from core.scheduler import countdown_tick

    context.job_queue.run_once(
        countdown_tick,
        delay,
        name=job_name,
        data=entry,
    )


def cancel_last_timer(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> bool:
    entry = pop_last_timer(chat_id)
    if not entry:
        return False

    for job in context.job_queue.get_jobs_by_name(entry.job_name):
        job.schedule_removal()
    return True


def cancel_all_timers(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> int:
    entries = get_timers(chat_id)
    count = 0

    for entry in entries:
        for job in context.job_queue.get_jobs_by_name(entry.job_name):
            job.schedule_removal()
        count += 1

    clear_timers(chat_id)
    return count
