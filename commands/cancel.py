# ==================================================
# cancel.py — Cancel timer callbacks (/cancel + buttons)
# ==================================================

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.timers_store import pop_last_timer, get_timers, clear_timers

logger = logging.getLogger(__name__)


def _extract_job_name(data: str) -> str | None:
    """
    Supported callback_data formats:
      - cancel_timer:<job_name>
      - cancel_one|<job_name>
      - cancel_all|<anything>   (job_name not needed)
    """
    if not data:
        return None

    if data.startswith("cancel_timer:"):
        return data.split("cancel_timer:", 1)[1].strip() or None

    if data.startswith("cancel_one|"):
        return data.split("cancel_one|", 1)[1].strip() or None

    return None


def _remove_jobs_by_name(context: ContextTypes.DEFAULT_TYPE, job_name: str) -> int:
    """
    Removes jobs in PTB JobQueue by exact name.
    Returns count removed.
    """
    if not job_name:
        return 0

    job_queue = context.application.job_queue
    jobs = job_queue.get_jobs_by_name(job_name) or []
    for j in jobs:
        j.schedule_removal()
    return len(jobs)


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles inline button cancels.
    """
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data or ""

    chat_id = query.message.chat_id if query.message else None
    if chat_id is None:
        return

    # ---------- Cancel ALL ----------
    if data.startswith("cancel_all|") or data == "cancel_all":
        timers = get_timers(chat_id)

        removed_total = 0
        for entry in timers:
            job_name = getattr(entry, "job_name", None) or getattr(entry, "name", None)
            if job_name:
                removed_total += _remove_jobs_by_name(context, job_name)

        clear_timers(chat_id)

        try:
            await query.edit_message_text(f"❌ Cancelled all timers ({removed_total}).")
        except Exception as e:
            logger.warning("Failed to edit message after cancel_all: %s", e)
        return

    # ---------- Cancel ONE (by explicit job_name) ----------
    job_name = _extract_job_name(data)

    # If we didn't get a job name from button (edge-case), fallback to "last timer"
    if not job_name:
        entry = pop_last_timer(chat_id)
        if not entry:
            try:
                await query.edit_message_text("⚠️ No active timers to cancel.")
            except Exception:
                pass
            return
        job_name = getattr(entry, "job_name", None) or getattr(entry, "name", None)

    removed = _remove_jobs_by_name(context, job_name)

    # Also try to remove this timer from store if it's still there (without breaking anything)
    # We don't require timers_store changes: just filter the list in-place if possible.
    try:
        timers = get_timers(chat_id)
        new_list = []
        for t in timers:
            t_name = getattr(t, "job_name", None) or getattr(t, "name", None)
            if t_name != job_name:
                new_list.append(t)
        # rebuild store by clearing then re-registering remaining
        # (keeps behaviour stable even if you cancel a non-last timer)
        clear_timers(chat_id)
        for t in new_list:
            # timers_store.register_timer exists in твоём коде
            from core.timers_store import register_timer
            register_timer(chat_id, t)
    except Exception as e:
        logger.debug("Store cleanup skipped: %s", e)

    try:
        if removed > 0:
            await query.edit_message_text("❌ Timer cancelled.")
        else:
            await query.edit_message_text("⚠️ Timer not found (maybe already finished).")
    except Exception as e:
        logger.warning("Failed to edit message after cancel_one: %s", e)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Optional: /cancel command. Shows buttons: cancel last / cancel all.
    """
    chat_id = update.effective_chat.id
    timers = get_timers(chat_id)

    if not timers:
        await update.message.reply_text("⚠️ No active timers.")
        return

    last = timers[-1]
    job_name = getattr(last, "job_name", None) or getattr(last, "name", None) or ""

    kb = [
        [InlineKeyboardButton("❌ Cancel last", callback_data=f"cancel_timer:{job_name}")],
        [InlineKeyboardButton("🧹 Cancel all", callback_data=f"cancel_all|{chat_id}")],
    ]
    await update.message.reply_text(
        "Choose what to cancel:",
        reply_markup=InlineKeyboardMarkup(kb),
    )
