# ==================================================
# core/countdown.py
# ==================================================

from datetime import datetime, timezone
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.formatter import choose_update_interval


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    entry: TimerEntry = context.job.data

    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # 🔔 FINISH
    if remaining <= 0:
        await context.bot.send_message(
            entry.chat_id,
            f"⏰ <b>Time is up!</b>\n{entry.message}",
            parse_mode="HTML",
        )

        # 📌 UNPIN
        if entry.pin_message_id:
            try:
                await context.bot.unpin_chat_message(
                    entry.chat_id,
                    entry.pin_message_id,
                )
            except Exception:
                pass

        context.job.schedule_removal()
        return

    # ⏳ RESCHEDULE
    delay = choose_update_interval(remaining)

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=context.job.name,
    )
