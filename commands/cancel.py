# ==================================================
# commands/cancel.py — Timer Cancellation Commands
# ==================================================
#
# User-facing /cancel command and callback handlers for cancelling timers (single or all).
#
# Layer: Commands
#
# Responsibilities:
# - Validate/parse user input (minimal)
# - Delegate work to services/core
# - Send user-facing responses via Telegram API
#
# Boundaries:
# - Commands do not implement business logic; they orchestrate user interaction.
# - Keep commands thin and deterministic; move reusable logic to services/core.
#
# ==================================================
import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from core.admin import is_admin
from core.formatter import format_remaining_time
from core.timers import remove_timer_job
from core.timers_store import list_timers, remove_timer

logger = logging.getLogger(__name__)


async def _unpin_if_pinned(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int | None) -> None:
    """Unpin a specific message if it is currently pinned."""
    if not message_id:
        return
    try:
        chat = await context.bot.get_chat(chat_id)
        pinned = getattr(chat, "pinned_message", None)
        if pinned and pinned.message_id == message_id:
            await context.bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)

            # Safety guard: some clients can keep showing a pinned message even after an unpin call.
            chat2 = await context.bot.get_chat(chat_id)
            pinned2 = getattr(chat2, "pinned_message", None)
            if pinned2 and pinned2.message_id == message_id:
                await context.bot.unpin_chat_message(chat_id=chat_id)
    except Exception as e:
        logger.warning("Unpin failed for chat=%s msg=%s: %s", chat_id, message_id, e)


def _short(text: str, limit: int = 26) -> str:
    """Command handler:  short."""
    text = (text or "").replace("\n", " ").strip()
    if not text:
        return ""
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _timer_label(entry) -> str:
    """Build a short, readable timer label for an inline keyboard button."""
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())
    if remaining < 0:
        remaining = 0

    msg = _short(entry.message)
    if not msg:
        msg = "no text"

    # Keep button text short (Telegram is strict about inline keyboard limits).
    # Add a small suffix for uniqueness/debugging.
    return f"❌ {format_remaining_time(remaining)} — {msg} (#{entry.message_id})"


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Admin-only
    """Handle the /cancel command."""
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ This command is available to administrators only.")
        return

    chat_id = update.effective_chat.id
    timers = list_timers(chat_id)

    if not timers:
        await update.message.reply_text("No active timers found.")
        return

    # Sort timers by nearest completion time.
    timers.sort(key=lambda t: t.target_time)

    keyboard = []
    for t in timers:
        keyboard.append(
            [InlineKeyboardButton(_timer_label(t), callback_data=f"cancel_one:{chat_id}:{t.message_id}")]
        )

    # IMPORTANT: we do not expose /cancelall as a separate command; the "cancel all" action lives inside /cancel.
    keyboard.append(
        [InlineKeyboardButton("🧹 Cancel ALL timers", callback_data=f"cancel_all:{chat_id}")]
    )

    await update.message.reply_text(
        "Choose what to cancel:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries (inline button actions) for timer cancellation."""
    query = update.callback_query
    if not query or not query.data:
        return

    # Admin-only (important: anyone in the group can tap buttons)
    if not await is_admin(update, context):
        await query.answer("⛔ Admins only", show_alert=True)
        return

    try:
        action, chat_id_str, *rest = query.data.split(":")
        chat_id = int(chat_id_str)
    except Exception:
        await query.answer("Invalid data", show_alert=True)
        return

    job_queue = context.job_queue

    if action == "cancel_one":
        if not rest:
            await query.answer("Invalid data", show_alert=True)
            return
        msg_id = int(rest[0])

        # Locate the timer entry (needed to decide whether we should unpin).
        entry = next((t for t in list_timers(chat_id) if t.message_id == msg_id), None)
        if not entry:
            await query.answer("Timer was not found anymore.")
            return

        # If this timer message was pinned, unpin it.
        await _unpin_if_pinned(context, chat_id, entry.pin_message_id or msg_id)

        remove_timer_job(job_queue, chat_id, msg_id)
        remove_timer(chat_id, msg_id)

        # Update the timer message text (if it still exists).
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text="⛔ Timer cancelled.",
            )
        except Exception as e:
            logger.warning("Edit cancelled timer message failed: %s", e)

        await query.answer("OK")
        return

    if action == "cancel_all":
        entries = list_timers(chat_id)

        # First, unpin (if the pinned message is this timer).
        for entry in entries:
            if entry.pin_message_id:
                await _unpin_if_pinned(context, chat_id, entry.pin_message_id)

        # Then remove jobs and delete the timer entry.
        for entry in entries:
            remove_timer_job(job_queue, chat_id, entry.message_id)
            remove_timer(chat_id, entry.message_id)

        await query.answer("OK")
        try:
            await query.edit_message_text("✅ All timers have been cancelled.")
        except Exception:
            # If we cannot edit the menu message, fail silently.
            pass
        return

    await query.answer("Unknown action", show_alert=True)


async def cancel_timer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel button under each timer message.

    Callback data format: cancel_timer:<message_id>

    This button is intentionally *not* admin-only: people expect the
    inline "Cancel" under the timer to just work.
    """
    query = update.callback_query
    if not query or not query.data:
        return

    try:
        _, msg_id_str = query.data.split(":", 1)
        msg_id = int(msg_id_str)
    except Exception:
        await query.answer("Invalid data", show_alert=True)
        return

    # Where the button was pressed
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        await query.answer("Failed to resolve chat", show_alert=True)
        return

    entry = next((t for t in list_timers(chat_id) if t.message_id == msg_id), None)
    if not entry:
        # The timer was already removed / expired
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.answer("Timer was not found")
        return

    # If it's pinned, unpin it first
    await _unpin_if_pinned(context, chat_id, entry.pin_message_id or msg_id)

    remove_timer_job(context.job_queue, chat_id, msg_id)
    remove_timer(chat_id, msg_id)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text="⛔ Timer cancelled.",
        )
    except Exception as e:
        logger.warning("Edit cancelled timer message failed: %s", e)

    await query.answer("OK")