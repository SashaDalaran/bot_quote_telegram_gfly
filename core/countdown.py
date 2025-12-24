# core/countdown.py

import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.formatter import format_remaining, choose_interval
from core.timers_store import remove_timer

logger = logging.getLogger(__name__)


def _cancel_kb(job_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_timer:{job_name}")]]
    )


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data

    # если кто-то пометил как cancelled
    if getattr(entry, "cancelled", False):
        return

    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ---- FINISH ----
    if remaining <= 0:
        try:
            text = "⏰ Time is up!"
            if getattr(entry, "text", ""):
                text += f"\n{entry.text}"
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=text,
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        # убрать из стора
        try:
            remove_timer(entry.chat_id, entry.job_name)
        except Exception:
            pass

        return

    # ---- BUILD TEXT ----
    new_text = f"⏰ Time left: {format_remaining(remaining)}"
    if getattr(entry, "text", ""):
        new_text += f"\n{entry.text}"

    # не редактируем то же самое (иначе Telegram 'message is not modified')
    if getattr(entry, "last_text", None) == new_text:
        delay = choose_interval(remaining)
        context.job_queue.run_once(countdown_tick, delay, data=entry, name=entry.job_name)
        return

    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=new_text,
            reply_markup=_cancel_kb(entry.job_name),
        )
        entry.last_text = new_text
    except Exception as e:
        logger.warning("Edit failed: %s", e)

    delay = choose_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,  # ✅ ВАЖНО: имя не меняем
    )
