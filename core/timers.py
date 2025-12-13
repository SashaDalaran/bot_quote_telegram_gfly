from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import choose_update_interval
from core.scheduler import countdown_tick


async def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str,
    pin_message_id: int,
) -> str:
    """
    Create one-time countdown timer.
    """

    # safety: force UTC
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)
    else:
        target_time = target_time.astimezone(timezone.utc)

    job_name = f"timer:{chat_id}:{int(target_time.timestamp())}"

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time,
        pin_message_id=pin_message_id,
        message=message,
        job_name=job_name,
    )

    delay = choose_update_interval(
        int((target_time - datetime.now(timezone.utc)).total_seconds())
    )

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=job_name,
    )

    return job_name
