# ==================================================
# core/countdown.py — Countdown Job Engine
# ==================================================
#
# This module implements the low-level countdown
# update mechanism used by timers.
#
# Responsibilities:
# - Calculate remaining time until the target moment
# - Update an existing Telegram message in place
# - Dynamically reschedule itself with adaptive intervals
# - Finalize the countdown when time is up
#
# IMPORTANT:
# - This is CORE infrastructure logic.
# - It does NOT parse user input.
# - It does NOT decide when a countdown starts.
# - It ONLY updates an existing countdown message.
#
# ==================================================

from datetime import datetime, timezone

from telegram import Bot
from telegram.ext import ContextTypes

from core.formatter import format_duration, choose_update_interval

# ==================================================
# Countdown job callback
# ==================================================
#
# This coroutine is executed by JobQueue.
# It updates a countdown message and schedules
# the next update until the timer reaches zero.
#
async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:

    # Job payload injected during scheduling
    data = context.job.data
    bot: Bot = context.bot

    chat_id = data["chat_id"]
    message_id = data["message_id"]
    target_time = data["target_time"]
    label = data.get("label", "")
    job_name = data["job_name"]

    # --------------------------------------------------
    # Remaining time calculation
    # --------------------------------------------------
    #
    # All countdowns operate in UTC to avoid
    # timezone drift and daylight saving issues.
    #
    now = datetime.now(timezone.utc)
    seconds_left = int((target_time - now).total_seconds())

    # --------------------------------------------------
    # Countdown finished
    # --------------------------------------------------
    #
    # When the timer reaches zero or below:
    # - Update the message one last time
    # - Do NOT schedule any further updates
    #
    if seconds_left <= 0:
        text = "⏰ Time is up!"
        if label:
            text += f"\n{label}"

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
            )
        except Exception:
            # Message may be deleted or uneditable
            pass

        # IMPORTANT:
        # No further scheduling — countdown ends here
        return

    # --------------------------------------------------
    # Countdown update
    # --------------------------------------------------
    #
    # Format remaining time into a human-readable string
    #
    remaining = format_duration(seconds_left)
    text = f"⏳ {remaining}"
    if label:
        text += f"\n{label}"

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except Exception:
        # Ignore edit failures (message removed, permissions, etc.)
        pass

    # --------------------------------------------------
    # Self-rescheduling
    # --------------------------------------------------
    #
    # The countdown dynamically schedules the NEXT update
    # based on the remaining time.
    #
    # This allows:
    # - frequent updates when close to zero
    # - sparse updates for long durations
    #
    context.job_queue.run_once(
        countdown_tick,
        when=choose_update_interval(seconds_left),
        name=job_name,
        data=data,
    )
