# core/timers.py
import uuid
from datetime import datetime
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import register_timer
from core.countdown import countdown_tick

def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    target_time: datetime,
    text: str | None = None,
) -> None:
    job_name = f"timer:{chat_id}:{uuid.uuid4().hex}"

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=message_id,
        target_time=target_time,
        job_name=job_name,
        text=text,
    )

    register_timer(entry)

    context.job_queue.run_repeating(
        countdown_tick,
        interval=1,
        first=0,
        data=entry,
        name=job_name,
    )
