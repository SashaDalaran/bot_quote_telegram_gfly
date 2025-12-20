# core/timers.py

import uuid
from datetime import datetime
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import add_timer
from core.scheduler import countdown_tick


def create_timer(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str | None = None,
    pin_message_id: int | None = None,
) -> None:
    job_name = f"timer:{chat_id}:{uuid.uuid4().hex}"

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time,
        message=message,
        message_id=pin_message_id,
        job_name=job_name,
    )

    add_timer(chat_id, entry)

    delay = max(1, int((target_time - datetime.utcnow()).total_seconds()))

    context.job_queue.run_once(
        countdown_tick,
        delay,
        name=job_name,
        data=entry,
    )
