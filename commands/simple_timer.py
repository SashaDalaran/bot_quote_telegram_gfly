# ==================================================
# commands/simple_timer.py — Simple Countdown Timer
# ==================================================
#
# This module defines a minimal user-facing command
# for creating a simple countdown timer.
#
# Command:
# - /timer <duration>
#
# Examples:
# - /timer 30s
# - /timer 5m
# - /timer 1h
# - /timer 1h30m
#
# Responsibilities:
# - Parse duration from user input
# - Convert it into an absolute UTC timestamp
# - Delegate timer creation to timer application service
#
# IMPORTANT:
# - This command supports ONLY relative durations
# - Absolute date timers are handled by date_timer.py
#
# ==================================================

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from services.timer_service import create_timer
from core.parser import parse_duration

# ==================================================
# /timer command
# ==================================================
#
# Creates a simple countdown timer based on
# a relative duration provided by the user.
#
async def timer_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    chat_id = update.effective_chat.id

    # --------------------------------------------------
    # Validate input
    # --------------------------------------------------
    #
    # Expected:
    #   /timer <duration>
    #
    if not context.args:
        await update.message.reply_text(
            "❌ Format: /timer 30s | 5m | 1h | 1h30m"
        )
        return

    # --------------------------------------------------
    # Parse duration
    # --------------------------------------------------
    try:
        seconds = parse_duration(context.args[0])
    except ValueError as e:
        await update.message.reply_text(f"❌ {e}")
        return

    # --------------------------------------------------
    # Calculate target time (UTC)
    # --------------------------------------------------
    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    # --------------------------------------------------
    # Create timer
    # --------------------------------------------------
    #
    # The initial message is sent immediately and
    # then updated by the countdown engine.
    #
    msg = await update.message.reply_text("⏳ Timer started...")

    create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time,
        message="",
        pin_message_id=msg.message_id,
    )
