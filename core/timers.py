from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import format_remaining_time, choose_update_interval
from core.countdown import countdown_tick

# 🔴 ЕДИНСТВЕННОЕ хранилище таймеров
TIMERS: dict[int, list[TimerEntry]] = {}


def register_timer(chat_id: int, entry: TimerEntry) -> None:
    TIMERS.setdefault(chat_id, []).append(entry)


def get_timers(chat_id: int) -> list[TimerEntry]:
    return TIMERS.get(chat_id, [])


def clear_timers(chat_id: int) -> None:
    TIMERS.pop(chat_id, None)


def create_timer(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    text: str | None = None,
    pin: bool = False,
):
    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())

    if remaining <= 0:
        raise ValueError("Target time must be in the future")

    async def _send():
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ Time left: {format_remaining_time(remaining)}\n{text or ''}".strip(),
        )

        if pin:
            await context.bot.pin_chat_message(
                chat_id=chat_id,
                message_id=msg.message_id,
                disable_notification=True,
            )

        entry = TimerEntry(
            chat_id=chat_id,
            message_id=msg.message_id,
            target_time=target_time,
            message=text,
        )

        register_timer(chat_id, entry)

        delay = choose_update_interval(remaining)
        context.job_queue.run_once(
            countdown_tick,
            delay,
            name=entry.job_name,
            data=entry,
        )

    context.application.create_task(_send())
