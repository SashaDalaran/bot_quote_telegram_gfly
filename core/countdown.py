# core/countdown.py

from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time, choose_update_interval
from core.timers_store import clear_timers


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ⏰ TIMER FINISHED
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="⏰ Time is up!",
            )
        except Exception:
            pass

        clear_timers(entry.chat_id)
        return

    # 📝 BUILD MESSAGE
    text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if entry.message:
        text += f"\n{entry.message}"

    # ✋ НЕ редактируем то же самое
    if entry.last_text != text:
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=text,
            )
            entry.last_text = text
        except Exception:
            pass

    # ⏱ ВЫБОР ИНТЕРВАЛА (КЛЮЧЕВО!)
    delay = choose_update_interval(remaining)

    # 🔁 ПЕРЕСОЗДАЁМ JOB С НОВЫМ ИНТЕРВАЛОМ
    context.job_queue.run_once(
        countdown_tick,
        delay,
        name=entry.job_name,
        data=entry,
    )
