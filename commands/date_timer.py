# ==================================================
# commands/date_timer.py
# ==================================================

from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_str = context.args[0]
        time_str = context.args[1]
        tz_str = context.args[2]
        message = " ".join(context.args[3:]).replace("--pin", "").strip()
        pin = "--pin" in context.args
    except Exception:
        await update.message.reply_text(
            "Формат:\n/timerdate DD.MM.YYYY HH:MM +TZ текст [--pin]"
        )
        return

    dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
    tz_hours = int(tz_str)
    target_time = dt.replace(
        tzinfo=timezone.utc
    ) - timedelta(hours=tz_hours)

    msg = await update.message.reply_text(
        "⏳ <b>Осталось:</b> ...",
        parse_mode="HTML",
    )

    if pin:
        await msg.pin()

    create_timer(
        context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message_id=msg.message_id,
        message=message or None,
        pin_message_id=msg.message_id if pin else None,
    )
