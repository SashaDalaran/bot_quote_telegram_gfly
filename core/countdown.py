# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone

from telegram.error import BadRequest
from telegram.ext import ContextTypes

from core.formatter import choose_update_interval, format_remaining_time

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None:
        return

    entry = job.data
    now_utc = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now_utc).total_seconds())

    # ===== FINAL =====
    if remaining <= 0:
        logger.info("Timer %s finished", entry.job_name)

        # Update pinned message (if exists)
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="⏰ <b>Time is up!</b>",
                parse_mode="HTML",
            )
        except BadRequest:
            pass

        # Send final notification
        try:
            await context.bot.send_message(
                chat_id=entry.chat_id,
                text=entry.message or "⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Failed to send final message: %s", e)

        # Auto-unpin
        if entry.pin_message_id:
            try:
                await context.bot.unpin_chat_message(
                    chat_id=entry.chat_id,
                    message_id=entry.pin_message_id,
                )
            except Exception as e:
                logger.warning("Failed to unpin message: %s", e)

        return

    # ===== TICK =====
    text_lines = [
        "⏳ <b>Timer</b>",
        f"Remaining: {format_remaining_time(remaining)}",
    ]

    if entry.message:
        text_lines.append(entry.message)

    text = "\n".join(text_lines)

    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except BadRequest as e:
        if "message is not modified" not in str(e).lower():
            logger.warning("Edit failed: %s", e)

    delay = choose_update_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )
