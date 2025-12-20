from datetime import datetime, timedelta, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers_store import register_timer
from core.countdown import countdown_tick

async def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    seconds: int,
    message: str | None,
):
    sent = await context.bot.send_message(
        chat_id=chat_id,
        text="⏳ Timer started.",
    )

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=sent.message_id,
        target_time=datetime.now(timezone.utc) + timedelta(seconds=seconds),
        message=message,
    )

    register_timer(entry)

    context.job_queue.run_once(
        countdown_tick,
        1,
        data=entry,
    )
