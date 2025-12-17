# ==================================================
# commands/date_timer.py — Absolute Date Timer Command
# ==================================================
#
# This module defines a command for creating
# a countdown timer using an absolute date and time.
#
# Command:
# - /timerdate DD.MM.YYYY HH:MM [message]
#
# Example:
# - /timerdate 31.12.2025 23:59 Happy New Year!
#
# Responsibilities:
# - Parse absolute date/time from user input
# - Create a timer via core.timers
#
# IMPORTANT:
# - The provided date/time is interpreted as UTC
# - No validation logic lives here beyond parsing
#
# ==================================================

from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer

# ==================================================
# /timerdate command
# ==================================================
#
# Creates a countdown timer using an absolute
# date and time provided by the user.
#
async def timerdate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    chat_id = update.effective_chat.id

    # --------------------------------------------------
    # Parse absolute datetime (UTC)
    # --------------------------------------------------
    #
    # Expected format:
    #   DD.MM.YYYY HH:MM
    #
    dt = datetime.strptime(
        " ".join(context.args[:2]),
        "%d.%m.%Y %H:%M",
    ).replace(tzinfo=timezone.utc)

    # Optional timer label
    label = " ".join(context.args[2:])

    # Acknowledge timer creation
    msg = await update.message.reply_text("⏳ Timer set")

    # Delegate actual timer creation to core
    create_timer(
        context,
        chat_id,
        dt,
        label,
        msg.message_id,
    )
