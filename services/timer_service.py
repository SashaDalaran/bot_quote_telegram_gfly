# ==================================================
# services/timer_service.py — Timer Application Service
# ==================================================

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from telegram import Update
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.parser import parse_duration, parse_datetime_with_tz
from core.formatter import (
    choose_update_interval,
    format_remaining_time,
    pretty_time_short,
)

from core.countdown import countdown_tick
from services.quotes_service import get_random_quote

logger = logging.getLogger(__name__)

# ==================================================
# In-memory state (process-local)
# ==================================================

TIMERS: Dict[int, List[TimerEntry]] = {}
REPEATS: Dict[int, List[RepeatEntry]] = {}
PINNED_BY_BOT: Dict[int, List[int]] = {}

# ==================================================
# Internal helpers
# ==================================================

def _remember_pin(chat_id: int, message_id: int) -> None:
    PINNED_BY_BOT.setdefault(chat_id, []).append(message_id)

# ==================================================
# Public API — One-time timers
# ==================================================

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

    # --------------------------------------------------
    # Parse target time
    # --------------------------------------------------
    try:
        if len(args) >= 2 and "." in args[0] and ":" in args[1]:
            target_time_utc, msg_start, _ = parse_datetime_with_tz(args)
            remaining = int((target_time_utc - now_utc).total_seconds())
            if remaining <= 0:
                await msg.reply_text("Target time must be in the future.")
                return
            message = " ".join(args[msg_start:]).strip()
        else:
            duration = parse_duration(args[0])
            target_time_utc = now_utc + timedelta(seconds=duration)
            remaining = duration
            message = " ".join(args[1:]).strip()

    except ValueError as e:
        await msg.reply_text(f"Bad format: {e}")
        return

    message = message.strip('"') if message else None
    quote = get_random_quote(quotes)

    # --------------------------------------------------
    # Build timer text (THIS MESSAGE WILL BE PINNED + EDITED)
    # --------------------------------------------------
    lines = [f"⏰ Time left: {format_remaining_time(remaining)}"]

    if message:
        lines.append(message)
    if quote:
        lines.append(f"💬 {quote}")

    timer_text = "\n".join(lines)

    timer_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=timer_text,
    )

    # --------------------------------------------------
    # Pin message
    # --------------------------------------------------
    await context.bot.pin_chat_message(
        chat_id=chat_id,
        message_id=timer_msg.message_id,
        disable_notification=True,
    )

    _remember_pin(chat_id, timer_msg.message_id)

    # --------------------------------------------------
    # Create model & schedule job
    # --------------------------------------------------
    entry = TimerEntry(
        chat_id=chat_id,
        message_id=timer_msg.message_id,
        target_time=target_time_utc,
        message=message,
        pin="--pin" in context.args,  # ← ВАЖНО
    )


    TIMERS.setdefault(chat_id, []).append(entry)

    delay = choose_update_interval(remaining)

    context.application.job_queue.run_once(
        countdown_tick,
        delay,
        name=entry.job_name,
        data=entry,
    )

    await msg.reply_text(
        f"📌 Timer started: {pretty_time_short(remaining)}"
    )

# ==================================================
# Public API — Cancel timers
# ==================================================

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
        for job in context.application.job_queue.get_jobs_by_name(entry.job_name):
            job.schedule_removal()

    TIMERS.pop(chat_id, None)
    await msg.reply_text("✅ All one-time timers cancelled.")

# ==================================================
# Public API — Repeating timers (оставляем как есть)
# ==================================================

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

    entry = RepeatEntry(
        chat_id=chat_id,
        interval=interval,
        message=message,
    )

    REPEATS.setdefault(chat_id, []).append(entry)

    context.application.job_queue.run_repeating(
        repeat_tick,
        interval=interval,
        first=interval,
        name=entry.job_name,
        data=entry,
    )

    await msg.reply_text(
        f"🔁 Repeat timer set every {pretty_time_short(interval)}."
    )

# ==================================================
# Public API — Cleanup
# ==================================================

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
            await context.bot.unpin_chat_message(chat_id, mid)
            removed += 1
        except Exception as e:
            logger.warning("Failed to unpin %s: %s", mid, e)

    PINNED_BY_BOT[chat_id] = []
    await msg.reply_text(f"✅ Removed {removed} pins.")
