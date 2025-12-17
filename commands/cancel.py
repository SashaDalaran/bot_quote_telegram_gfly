# ==================================================
# commands/cancel.py — Timer Cancellation Commands
# ==================================================
#
# User-facing commands for cancelling timers.
#
# Commands:
# - /cancel
# - /cancelall
#
# Behavior:
# - Cancels ALL active one-time timers in the current chat
#
# Architecture:
# commands → services.timer_service → core
#
# IMPORTANT:
# - This module contains NO timer logic
# - No state is stored here
# - All timer management lives in services.timer_service
#
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from services.timer_service import cancel_all_timers


async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    /cancel — cancel all active timers in this chat.
    """
    await cancel_all_timers(update, context)


async def cancel_all_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    /cancelall — alias for /cancel.
    """
    await cancel_all_timers(update, context)
