# ==================================================
# core/countdown.py
# ==================================================

from datetime import datetime, timezone
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.formatter import choose_update_interval


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    """
    Single countdown tick.
    This function RESCHEDULES ITSELF until time is up.
    """
    entry = context.job.data
    bot = context.bot

    now = datetime.now(timezone.utc)
    sec_left = int((entry.target_time - now).total_seconds())

    # ---------- TIME IS UP ----------
    if sec_left <= 0:
        await bot.send_message(
            chat_id=entry.chat_id,
            text=f"⏰ <b>Time is up!</b>\n{entry.message or ''}",
            parse_mode=ParseMode.HTML,
        )

        # auto-unpin if needed
        if entry.pin_message_id:
            try:
                await bot.unpin_chat_message(
                    chat_id=entry.chat_id,
                    message_id=entry.pin_message_id,
                )
            except Exception:
                pass

        return  # ⛔️ НЕ пересоздаём job

    # ---------- COUNTDOWN UPDATE ----------
    mins, secs = divmod(sec_left, 60)
    time_str = f"{mins} мин. {secs} сек." if mins else f"{secs} сек."

    await bot.send_message(
        chat_id=entry.chat_id,
        text=f"⏳ Осталось: <b>{time_str}</b>",
        parse_mode=ParseMode.HTML,
    )

    # ---------- RESCHEDULE SAME JOB ----------
    delay = choose_update_interval(sec_left)
    context.job.reschedule(trigger="date", run_date=now + timedelta(seconds=delay))
