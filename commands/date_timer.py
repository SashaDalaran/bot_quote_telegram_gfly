# ==================================================
# commands/date_timer.py
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_datetime_with_tz
from core.timers import create_timer


async def timerdate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    msg = update.effective_message
    if msg is None:
        return

    args = context.args
    if not args:
        await msg.reply_text(
            "Usage:\n/timerdate DD.MM.YYYY HH:MM +TZ text [--pin]"
        )
        return

    try:
        target_time_utc, text_start, _ = parse_datetime_with_tz(args)
        text = " ".join(args[text_start:]).replace("--pin", "").strip() or None
    except Exception as e:
        await msg.reply_text(f"❌ Bad format: {e}")
        return

    should_pin = "--pin" in args

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time_utc,
        text=text,
        pin=should_pin,
    )

    await msg.reply_text("⏳ Timer started.")
