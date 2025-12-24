# commands/date_timer.py

from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time
from core.parser import parse_date_time
from core.timers import create_timer


async def date_timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /date_timer YYYY-MM-DD HH:MM [message]  or /date_timer HH:MM [message]"
        )
        return

    args = context.args[:]
    dt_args = []
    msg_args = []

    if len(args) >= 2 and (("-" in args[0] and ":" in args[1]) or (":" in args[0] and "-" in args[1])):
        dt_args = args[:2]
        msg_args = args[2:]
    else:
        dt_args = args[:1]
        msg_args = args[1:]

    try:
        target_time = parse_date_time(dt_args)
    except Exception:
        await update.message.reply_text(
            "Can't parse date/time. Examples: /date_timer 2025-12-31 23:59  or  /date_timer 23:15"
        )
        return

    msg = " ".join(msg_args).strip() if msg_args else None

    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())
    if remaining <= 0:
        await update.message.reply_text("This time is already in the past.")
        return

    text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if msg:
        text += f"\n{msg}"

    sent = await update.message.reply_text(text)

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=msg,
        message_id=sent.message_id,
        pin_message_id=update.message.message_id,
    )


# Backward-compatible name used in bot.py
async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await date_timer_command(update, context)
