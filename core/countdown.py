# ==================================================
# core/countdown.py
# ==================================================

from datetime import datetime, timezone
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.formatter import choose_update_interval


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    entry = context.job.data
    bot = context.bot

    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ===== TIMER FINISHED =====
    if remaining <= 0:
        await bot.send_message(
            chat_id=entry.chat_id,
            text=f"⏰ <b>Time is up!</b>\n{entry.message or ''}",
            parse_mode=ParseMode.HTML,
        )

        if entry.pin_message_id:
            try:
                await bot.unpin_chat_message(
                    chat_id=entry.chat_id,
                    message_id=entry.pin_message_id,
                )
            except Exception:
                pass

        return  # ⛔️ НЕ СОЗДАЁМ НОВЫЙ JOB

    # ===== COUNTDOWN MESSAGE =====
    mins, secs = divmod(remaining, 60)
    if mins:
        text = f"⏳ Осталось: <b>{mins} мин {secs} сек</b>"
    else:
        text = f"⏳ Осталось: <b>{secs} сек</b>"

    await bot.send_message(
        chat_id=entry.chat_id,
        text=text,
        parse_mode=ParseMode.HTML,
    )

    # ===== NEXT TICK =====
    delay = choose_update_interval(remaining)

    context.job_queue.run_once(
        countdown_tick,
        when=delay,
        data=entry,
        name=entry.job_name,
    )
