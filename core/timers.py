# ==================================================
# core/timers.py
# ==================================================

from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import format_remaining_time
from core.countdown import countdown_tick

# chat_id -> [TimerEntry]
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
        # ---------------- send message ----------------
        timer_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ Time left: {format_remaining_time(remaining)}"
            + (f"\n{text}" if text else ""),
        )

        # ---------------- optional pin ----------------
        if pin:
            await context.bot.pin_chat_message(
                chat_id=chat_id,
                message_id=timer_msg.message_id,
                disable_notification=True,
            )

        # ---------------- model ----------------
        entry = TimerEntry(
            chat_id=chat_id,
            message_id=timer_msg.message_id,
            target_time=target_time,
            message=text,
        )

        TIMERS.setdefault(chat_id, []).append(entry)

        # ❗ ПЕРВЫЙ тик ВСЕГДА через 1 секунду
        context.application.job_queue.run_once(
            countdown_tick,
            1,
            name=entry.job_name,
            data=entry,
        )

    # ❗ create_timer НЕ async → нельзя await
    context.application.create_task(_send())
