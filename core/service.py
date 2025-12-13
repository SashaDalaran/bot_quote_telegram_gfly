import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from telegram import Update
from telegram.ext import ContextTypes

from core.models import TimerEntry, RepeatEntry
from core.parser import parse_duration, parse_datetime_with_tz
from core.formatter import (
    choose_update_interval,
    format_remaining_time,
    pretty_time_short,
)
from services.scheduler import countdown_tick, repeat_tick


logger = logging.getLogger(__name__)

# ----------------- in-memory storage -----------------

TIMERS: Dict[int, List[TimerEntry]] = {}
REPEATS: Dict[int, List[RepeatEntry]] = {}
PINNED_BY_BOT: Dict[int, List[int]] = {}


# ----------------- helpers -----------------

def remember_pin(chat_id: int, message_id: int) -> None:
    PINNED_BY_BOT.setdefault(chat_id, []).append(message_id)


def remove_timer_entry(chat_id: int, pin_message_id: int) -> None:
    if chat_id not in TIMERS:
        return
    TIMERS[chat_id] = [
        t for t in TIMERS[chat_id] if t.pin_message_id != pin_message_id
    ]
    if not TIMERS[chat_id]:
        del TIMERS[chat_id]


# ----------------- public API -----------------

async def create_timer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    quotes: List[str],
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    args = context.args
    if not args:
        await msg.reply_text("Usage: /timer <time> [message]")
        return

    chat_id = update.effective_chat.id
    now_utc = datetime.now(timezone.utc)

    try:
        # absolute datetime
        if len(args) >= 2 and "." in args[0] and ":" in args[1]:
            target_time_utc, msg_start, _ = parse_datetime_with_tz(args)
            remaining = int((target_time_utc - now_utc).total_seconds())
            if remaining <= 0:
                await msg.reply_text("Target time must be in the future.")
                return
            message = " ".join(args[msg_start:]).strip()
        else:
            duration_seconds = parse_duration(args[0])
            target_time_utc = now_utc + timedelta(seconds=duration_seconds)
            remaining = duration_seconds
            message = " ".join(args[1:]).strip()
    except ValueError as e:
        await msg.reply_text(f"Bad format: {e}")
        return

    if message:
        message = message.strip('"')

    quote = get_random_quote(quotes)

    lines = [f"⏰ Time left: {format_remaining_time(remaining)}"]
    if message:
        lines.append(message)
    if quote:
        lines.append(f"💬 {quote}")

    pin_text = "\n".join(lines)

    sent = await context.bot.send_message(chat_id=chat_id, text=pin_text)
    await context.bot.pin_chat_message(
        chat_id=chat_id,
        message_id=sent.message_id,
        disable_notification=True,
    )
    remember_pin(chat_id, sent.message_id)

    job_name = f"timer-{chat_id}-{sent.message_id}"

    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time_utc,
        pin_message_id=sent.message_id,
        message=message or None,
        quote=quote,
        job_name=job_name,
    )

    TIMERS.setdefault(chat_id, []).append(entry)

    delay = choose_update_interval(remaining)
    context.application.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=job_name,
    )

    await msg.reply_text(
        f"⏰ Timer set for {pretty_time_short(remaining)}."
    )


async def cancel_all_timers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    chat_id = update.effective_chat.id
    entries = TIMERS.get(chat_id)
    if not entries:
        await msg.reply_text("No timers to cancel.")
        return

    for entry in entries:
        jobs = context.application.job_queue.get_jobs_by_name(entry.job_name)
        for job in jobs:
            job.schedule_removal()

    TIMERS.pop(chat_id, None)
    await msg.reply_text("✅ All one-time timers cancelled.")


async def create_repeat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    args = context.args
    if not args:
        await msg.reply_text("Usage: /repeat <time> [message]")
        return

    chat_id = update.effective_chat.id

    try:
        interval = parse_duration(args[0])
    except ValueError as e:
        await msg.reply_text(f"Bad format: {e}")
        return

    message = " ".join(args[1:]).strip() or None
    job_name = f"repeat-{chat_id}-{len(REPEATS.get(chat_id, [])) + 1}"

    entry = RepeatEntry(
        chat_id=chat_id,
        interval=interval,
        message=message,
        job_name=job_name,
    )

    REPEATS.setdefault(chat_id, []).append(entry)

    context.application.job_queue.run_repeating(
        repeat_tick,
        interval=interval,
        first=interval,
        name=job_name,
        data=entry,
    )

    await msg.reply_text(
        f"🔁 Repeat timer set every {pretty_time_short(interval)}."
    )


async def cancel_all_repeats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    chat_id = update.effective_chat.id
    entries = REPEATS.get(chat_id)
    if not entries:
        await msg.reply_text("No repeat timers to cancel.")
        return

    for entry in entries:
        jobs = context.application.job_queue.get_jobs_by_name(entry.job_name)
        for job in jobs:
            job.schedule_removal()

    REPEATS.pop(chat_id, None)
    await msg.reply_text("✅ All repeat timers cancelled.")


async def list_timers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    chat_id = update.effective_chat.id
    one_time = len(TIMERS.get(chat_id, []))
    repeats = len(REPEATS.get(chat_id, []))

    await msg.reply_text(
        f"⏱ One-time timers: {one_time}\n"
        f"🔁 Repeating timers: {repeats}"
    )


async def clear_pins(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    password: str,
    expected_password: str,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    if not expected_password or password != expected_password:
        await msg.reply_text("❌ Wrong password.")
        return

    chat_id = update.effective_chat.id
    removed = 0

    for mid in PINNED_BY_BOT.get(chat_id, []):
        try:
            await context.bot.unpin_chat_message(
                chat_id=chat_id,
                message_id=mid,
            )
            removed += 1
        except Exception as e:
            logger.warning(
                "Failed to unpin message %s in chat %s: %s",
                mid,
                chat_id,
                e,
            )

    PINNED_BY_BOT[chat_id] = []
    await msg.reply_text(f"✅ Removed {removed} pins in this chat.")
