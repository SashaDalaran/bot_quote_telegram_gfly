# core/timers.py
import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import register_timer
from core.scheduler import countdown_tick

logger = logging.getLogger(__name__)


def create_timer(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    text: str | None = None,
    pin: bool = False,
) -> None:
    job = context.job_queue.run_once(
        countdown_tick,
        when=(target_time - datetime.now(timezone.utc)).total_seconds(),
    )

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=0,
        target_time=target_time,
        text=text,
        pin=pin,
    )

    job.data = entry
    register_timer(entry)
