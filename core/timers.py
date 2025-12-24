# core/timers.py

import logging
from datetime import datetime, timezone
from uuid import uuid4

from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import add_timer
from core.countdown import countdown_tick

logger = logging.getLogger(__name__)


async def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str | None,
    message_id: int,
) -> TimerEntry:
    """
    message_id MUST be bot's own message (the one we will edit).
    """

    # normalize timezone
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)

    job_name = f"timer:{chat_id}:{uuid4().hex}"

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time.astimezone(timezone.utc),
        message=message,
        message_id=message_id,
        job_name=job_name,
        last_text=None,
    )

    add_timer(entry)

    # start ticking quickly; tick will reschedule itself
    context.job_queue.run_once(
        countdown_tick,
        1,
        data=entry,
        name=job_name,
    )

    return entry
