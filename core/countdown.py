# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone

from telegram import constants
from telegram.ext import ContextTypes

from core.formatter import choose_update_interval
from core.timers import cancel_timer

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data

    chat_id = data["chat_id"]
    message_id = data["message_id"]
    target_time = data["target_time"]
    label = data.get("label", "")
    job_name = data["job_name"]

    now = datetime.now(timezone.utc)
    sec_left = int((target_time - now).total_seconds())

    # ⏰ ВРЕМЯ ВЫШЛО
    if sec_left <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⏰ Время вышло!\n{label}",
            )
        except Exception:
            pass

        cancel_timer(context, job_name)
        return

    # ⏳ формат времени
    days, rem = divmod(sec_left, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    time_str = []
    if days:
        time_str.append(f"{days}д")
    if hours:
        time_str.append(f"{hours}ч")
    if minutes:
        time_str.append(f"{minutes}м")
    time_str.append(f"{seconds}с")

    text = f"⏳ {' '.join(time_str)}"
    if label:
        text += f"\n{label}"

    # ✏️ обновляем сообщение
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=constants.ParseMode.HTML,
        )
    except Exception:
        pass

    # 🧠 УМНЫЙ ИНТЕРВАЛ
    next_tick = choose_update_interval(sec_left)

    # ❗ ВАЖНО: НЕ создавать новый job — используем run_once
    context.job_queue.run_once(
        countdown_tick,
        when=next_tick,
        name=job_name,
        data=data,
    )
