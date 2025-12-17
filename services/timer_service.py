# ==================================================
# services/timer_service.py — Timer Application Service
# ==================================================
#
# This module implements the application-level logic
# for one-time and repeating timers.
#
# Responsibilities:
# - Parse user input (duration or absolute datetime)
# - Create and store timer models
# - Schedule JobQueue tasks
# - Manage in-memory timer state
# - Handle cancel / list / cleanup operations
#
# IMPORTANT:
# - This is NOT a core module
# - This is NOT a pure domain service
# - This file orchestrates:
#     core + services + Telegram API
#
# ==================================================

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from telegram import Update
from telegram.ext import ContextTypes

from core.models import TimerEntry, RepeatEntry
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
#
# NOTE:
# - This state lives only as long as the process runs
# - It is sufficient for Fly.io single-instance bots
# - If persistence is needed, this layer can be replaced
#

TIMERS: Dict[int, List[TimerEntry]] = {}
REPEATS: Dict[int, List[RepeatEntry]] = {}
PINNED_BY_BOT: Dict[int, List[int]] = {}

# ==================================================
# Internal helpers
# ==================================================

def _remember_pin(chat_id: int, message_id: int) -> None:
    """Track messages pinned by the bot itself."""
    PINNED_BY_BOT.setdefault(chat_id, []).append(message_id)


def _remove_timer_entry(chat_id: int, pin_message_id: int) -> None:
    """Remove a timer entry associated with a pinned message."""
    if chat_id not in TIMERS:
        return

    TIMERS[chat_id] = [
        t for t in TIMERS[chat_id]
        if t.pin_message_id != pin_message_id
    ]

    if not TIMERS[chat_id]:
        del TIMERS[chat_id]

# ==================================================
# Public API — One-time timers
# ==================================================

async def create_timer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    quotes: List[str],
) -> None:
    """
    Create a one-time countdown timer.

    Supported input formats:
    - /timer 10m message
    - /timer 25 message
    - /timer 31.12.2025 23:59 UTC+3 message
    """

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
        # Absolute datetime format
        if len(args) >= 2 and "." in args[0] and ":" in args[1]:
            target_time_utc, msg_start, _ = parse_datetime_with_tz(args)
            remaining = int((target_time_utc - now_utc).total_seconds())
            if remaining <= 0:
                await msg.reply_text("Target time must be in the future.")
                return
            message = " ".join(args[msg_start:]).strip()

        # Relative duration format
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
    # Build pinned message
    # --------------------------------------------------
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

    _remember_pin(chat_id, sent.message_id)

    # --------------------------------------------------
    # Create model & schedule job
    # --------------------------------------------------
    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time_utc,
        message_id=sent.message_id,
        message=message,
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
        f"⏰ Timer set for {pretty_time_short(remaining)}."
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
# Public API — Repeating timers
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
        for job in context.application.job_queue.get_jobs_by_name(entry.job_name):
            job.schedule_removal()

    REPEATS.pop(chat_id, None)
    await msg.reply_text("✅ All repeat timers cancelled.")

# ==================================================
# Public API — Introspection & cleanup
# ==================================================

async def list_timers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    chat_id = update.effective_chat.id

    await msg.reply_text(
        f"⏱ One-time timers: {len(TIMERS.get(chat_id, []))}\n"
        f"🔁 Repeating timers: {len(REPEATS.get(chat_id, []))}"
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
            await context.bot.unpin_chat_message(chat_id, mid)
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
