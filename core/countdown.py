# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone

from telegram.ext import ContextTypes

from core.formatter import choose_update_interval
from core.models import TimerEntry

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    entry: TimerEntry = context.job.data

    now = datetime.now(timezone.utc)
    seconds_left = int((entry.target_time - now).total_seconds())

    # ================= TIME IS UP =================
    if seconds_left <= 0:
        text = "⏰ <b>Time is up!</b>"
        if entry.message:
            text += f"\n{entry.message}"

        await context.bot.send_message(
            chat_id=entry.chat_id,
            text=text,
            parse_mode="HTML",
        )

        # ---------- auto unpin ----------
        if entry.pin_message_id:
            try:
                await context.bot.unpin_chat_message(
                    chat_id=entry.chat_id,
                    message_id=entry.pin_message_id,
                )
            except Exception as e:
                logger.warning("Unpin failed: %s", e)

        return

    # ================= UPDATE MESSAGE =================
    minutes, seconds = divmod(seconds_left, 60)
    time_str = f"{minutes}:{seconds:02d}" if minutes else f"{seconds}s"

    text = f"⏳ <b>{time_str}</b>"
    if entry.message:
        text += f"\n{entry.message}"

    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=text,
            parse_mode="HTML",
        )
    except Exception:
        pass

    # ================= NEXT TICK =================
    delay = choose_update_interval(seconds_left)

    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )
