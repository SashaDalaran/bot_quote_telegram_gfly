# ==================================================
# commands/cancel.py — Timer Cancellation Commands
# ==================================================
#
# This module defines user-facing commands for
# cancelling active countdown timers.
#
# Commands:
# - /cancel       → cancel a specific timer (interactive or by index)
# - /cancelall    → cancel all active timers in the chat
#
# Responsibilities:
# - Retrieve active timers for the current chat
# - Delegate cancellation to core.timers
# - Provide clear, user-friendly feedback
#
# IMPORTANT:
# - This module contains NO timer logic
# - All timer state management lives in core.timers
#
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import list_timers, cancel_timer

# ==================================================
# /cancelall — cancel all timers
# ==================================================
#
# Cancels all active timers in the current chat.
#
async def cancel_all_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    chat_id = update.effective_chat.id
    message = update.effective_message

    timers = list_timers(context, chat_id)

    if not timers:
        await message.reply_text("❌ No active timers")
        return

    for timer in timers:
        cancel_timer(context, timer.job_name)

    await message.reply_text("🧹 All timers have been cancelled")

# ==================================================
# /cancel — cancel a specific timer
# ==================================================
#
# Behavior:
# - If an index is provided → cancel that timer
# - If no arguments are provided → show interactive list
#
# Example:
# - /cancel 2
#
async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    chat_id = update.effective_chat.id
    message = update.effective_message

    timers = list_timers(context, chat_id)

    if not timers:
        await message.reply_text("❌ No active timers")
        return

    # --------------------------------------------------
    # Cancel by index
    # --------------------------------------------------
    if context.args:
        try:
            index = int(context.args[0]) - 1
        except ValueError:
            await message.reply_text("❌ Invalid timer number")
            return

        if 0 <= index < len(timers):
            cancel_timer(context, timers[index].job_name)
            await message.reply_text("✅ Timer cancelled")
        else:
            await message.reply_text("❌ Invalid timer number")
        return

    # --------------------------------------------------
    # Interactive selection
    # --------------------------------------------------
    #
    # Show a numbered list of active timers.
    #
    text = "⛔ Which timer do you want to cancel?\n\n"

    for i, timer in enumerate(timers, start=1):
        label = timer.label or "no description"
        text += f"{i} — {label}\n"

    await message.reply_text(text)
