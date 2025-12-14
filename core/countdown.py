# core/countdown.py

from datetime import datetime, timezone
from telegram import Bot
from telegram.ext import ContextTypes

from core.formatter import format_duration, choose_update_interval


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data
    bot: Bot = context.bot

    chat_id = data["chat_id"]
    message_id = data["message_id"]
    target_time = data["target_time"]
    label = data.get("label", "")
    job_name = data["job_name"]

    now = datetime.now(timezone.utc)
    seconds_left = int((target_time - now).total_seconds())

    # ⏰ Таймер закончился
    if seconds_left <= 0:
        text = "⏰ Время вышло!"
        if label:
            text += f"\n{label}"

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
            )
        except Exception:
            pass

        # ❗ НИЧЕГО больше не планируем
        return

    # ⏳ Обновление
    remaining = format_duration(seconds_left)
    text = f"⏳ {remaining}"
    if label:
        text += f"\n{label}"

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except Exception:
        pass

    # 🔁 Планируем СЛЕДУЮЩЕЕ обновление
    context.job_queue.run_once(
        countdown_tick,
        when=choose_update_interval(seconds_left),
        name=job_name,
        data=data,
    )
