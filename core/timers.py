from datetime import datetime, timedelta, timezone
from telegram.ext import ContextTypes
from telegram import Update

from core.models import TimerEntry
from core.parser import parse_duration, parse_datetime_with_tz
from core.formatter import format_remaining_time, pretty_time_short, choose_update_interval
from core.countdown import countdown_tick

TIMERS = {}

async def create_timer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    msg = update.effective_message
    args = context.args
    chat_id = update.effective_chat.id
    now = datetime.now(timezone.utc)

    if not args:
        await msg.reply_text("Usage: /timer <time> [message]")
        return

    # ---- PARSE ----
    if len(args) >= 2 and "." in args[0] and ":" in args[1]:
        target_time, msg_start, _ = parse_datetime_with_tz(args)
        remaining = int((target_time - now).total_seconds())
        text = " ".join(args[msg_start:])
    else:
        duration = parse_duration(args[0])
        target_time = now + timedelta(seconds=duration)
        remaining = duration
        text = " ".join(args[1:])

    # ---- SEND + PIN ----
    timer_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏰ Time left: {format_remaining_time(remaining)}\n{text}".strip()
    )

    await context.bot.pin_chat_message(
        chat_id=chat_id,
        message_id=timer_msg.message_id,
        disable_notification=True,
    )

    # ---- MODEL ----
    entry = TimerEntry(
        chat_id=chat_id,
        message_id=timer_msg.message_id,
        target_time=target_time,
        message=text or None,
    )

    TIMERS.setdefault(chat_id, []).append(entry)

    # ---- SCHEDULE ----
    delay = choose_update_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        name=entry.job_name,
        data=entry,
    )

    await msg.reply_text(
        f"📌 Timer started: {pretty_time_short(remaining)}"
    )
