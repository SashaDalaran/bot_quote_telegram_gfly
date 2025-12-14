from datetime import datetime, timezone

from core.formatter import format_duration
from core.timers import cancel_timer


async def countdown_tick(
    context,
    *,
    chat_id: int,
    message_id: int,
    target_time: datetime,
    label: str,
    job_name: str,
):
    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())

    # ⛔️ ТАЙМЕР ЗАКОНЧИЛСЯ
    if remaining <= 0:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"⏰ {label}\nВремя вышло!"
        )

        # анпин ОБЯЗАТЕЛЬНО
        try:
            await context.bot.unpin_chat_message(chat_id, message_id)
        except Exception:
            pass

        cancel_timer(context, job_name)
        return

    # ⏳ обычное обновление
    text = f"⏳ {format_duration(remaining)}\n{label}"

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text
    )
