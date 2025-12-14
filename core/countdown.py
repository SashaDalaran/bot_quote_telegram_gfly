# ==================================================
# core/countdown.py
# ==================================================

from datetime import datetime, timezone, timedelta
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.formatter import choose_update_interval


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    entry = context.job.data
    bot = context.bot

    now = datetime.now(timezone.utc)
    sec_left = int((entry.target_time - now).total_seconds())

    # ===== FINISH =====
    if sec_left <= 0:
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

        return  # ⛔️ ничего больше не планируем

    # ===== COUNTDOWN MESSAGE =====
    mins, secs = divmod(sec_left, 60)
    if mins:
        time_str = f"{mins} мин. {secs} сек."
    else:
        time_str = f"{secs} сек."

    await bot.send_message(
        chat_id=entry.chat_id,
        text=f"⏳ Осталось: <b>{time_str}</b>",
        parse_mode=ParseMode.HTML,
    )

    # ===== NEXT TICK =====
    delay = choose_update_interval(sec_left)

    context.job_queue.run_once(
        countdown_tick,
        when=delay,
        data=entry,
        name=entry.job_name,
    )
