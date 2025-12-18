# ==================================================
# core/timers.py — low-level timer scheduler
# ==================================================

from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import (
    format_remaining_time,
    choose_update_interval,
)
from core.countdown import countdown_tick

TIMERS: dict[int, list[TimerEntry]] = {}


def create_timer(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    text: str | None = None,
    pin: bool = False,
) -> None:
    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())

    if remaining <= 0:
        raise ValueError("Target time must be in the future")

    async def _send():
        timer_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ Time left: {format_remaining_time(remaining)}"
            + (f"\n{text}" if text else ""),
        )

        if pin:
            await context.bot.pin_chat_message(
                chat_id=chat_id,
                message_id=timer_msg.message_id,
                disable_notification=True,
            )

        entry = TimerEntry(
            chat_id=chat_id,
            message_id=timer_msg.message_id,
            target_time=target_time,
            message=text,
            pin=pin,
        )

        TIMERS.setdefault(chat_id, []).append(entry)

        delay = choose_update_interval(remaining)
        context.job_queue.run_once(
            countdown_tick,
            delay,
            name=
