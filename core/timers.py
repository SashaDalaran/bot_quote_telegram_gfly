# core/timers.py
import logging
from datetime import datetime
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import register_timer
from core.countdown import countdown_tick

logger = logging.getLogger(__name__)


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    text: str | None = None,
):
    job_name = f"timer_{chat_id}_{int(target_time.timestamp())}"

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time,
        message=text,
        job_name=job_name,
    )

    register_timer(entry)

    context.job_queue.run_once(
        countdown_tick,
        when=1,
        data=entry,
        name=job_name,
    )
