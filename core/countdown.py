# ==================================================
# core/countdown.py — Countdown Tick Engine
# ==================================================
#
# JobQueue tick callbacks that update timer messages until completion or cancellation.
#
# Layer: Core
#
# Responsibilities:
# - Provide reusable, testable logic and infrastructure helpers
# - Avoid direct Telegram API usage (except JobQueue callback signatures where required)
# - Expose stable APIs consumed by services and commands
#
# Boundaries:
# - Core must remain independent from user interaction details.
# - Core should not import commands (top layer) to avoid circular dependencies.
#
# ==================================================
import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.formatter import format_remaining, choose_interval
from core.timers_store import remove_timer

logger = logging.getLogger(__name__)


def _cancel_kb(message_id: int) -> InlineKeyboardMarkup:
    """Core utility:  cancel kb."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_timer:{message_id}")]]
    )


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Core utility: countdown tick."""
    entry = context.job.data

    # Backwards compatibility: older payloads used `text` instead of `message`.
    entry_text = getattr(entry, "message", None)
    if entry_text is None:
        entry_text = getattr(entry, "text", "")

    # If the timer was marked as cancelled elsewhere, stop the job.
    if getattr(entry, "cancelled", False):
        return

    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ---- FINISH ----
    if remaining <= 0:
        # If this timer message was pinned, unpin it on completion
        pin_id = getattr(entry, "pin_message_id", None)
        if pin_id:
            try:
                await context.bot.unpin_chat_message(chat_id=entry.chat_id, message_id=pin_id)
            except Exception as e:
                logger.warning("Unpin on finish failed: %s", e)

        try:
            text = "⏰ Time is up!"
            if entry_text:
                text += f"\n{entry_text}"
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=text,
            )
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        # Remove from the in-memory store.
        try:
            remove_timer(entry.chat_id, entry.message_id)
        except Exception:
            pass

        return

    # ---- BUILD TEXT ----
    new_text = f"⏰ Time left: {format_remaining(remaining)}"
    if entry_text:
        new_text += f"\n{entry_text}"

    # Avoid re-sending the exact same text (Telegram returns 'message is not modified').
    if getattr(entry, "last_text", None) == new_text:
        delay = choose_interval(remaining)
        context.job_queue.run_once(countdown_tick, delay, data=entry, name=entry.job_name)
        return

    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=new_text,
            reply_markup=_cancel_kb(entry.message_id),
        )
        entry.last_text = new_text
    except Exception as e:
        msg = str(e).lower()
        logger.warning("Edit failed: %s", e)
        if "message to edit not found" in msg:
            # The message was deleted / unexpected ID: stop the timer to avoid an infinite loop.
            try:
                remove_timer(entry.chat_id, entry.message_id)
            except Exception:
                pass
            return

    delay = choose_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,  # IMPORTANT: keep the job name stable
    )