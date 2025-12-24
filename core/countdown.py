# ==================================================
# core/countdown.py
# ==================================================

from __future__ import annotations

import logging
from datetime import datetime, timezone

from telegram.error import BadRequest
from telegram.ext import ContextTypes

from core.formatter import format_remaining, choose_interval
from core.timers_store import remove_timer

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    entry = context.job.data
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())

    # ---- FINISH ----
    if remaining <= 0:
        final_text = "⏰ Time is up!"
        if entry.message:
            final_text += f"\n{entry.message}"

        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text=final_text,
            )
        except BadRequest as e:
            # Common cases: message is not editable / deleted / not found.
            logger.warning("Finalize edit failed (%s). Sending a new message.", e)
            try:
                await context.bot.send_message(chat_id=entry.chat_id, text=final_text)
            except Exception as e2:
                logger.warning("Finalize send failed: %s", e2)
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        remove_timer(entry.chat_id, entry.job_name)
        return

    # ---- BUILD TEXT ----
    new_text = f"⏰ Time left: {format_remaining(remaining)}"
    if entry.message:
        new_text += f"\n{entry.message}"

    # ---- DO NOT EDIT SAME TEXT ----
    if entry.last_text == new_text:
        delay = choose_interval(remaining)
        context.job_queue.run_once(countdown_tick, delay, data=entry, name=entry.job_name)
        return

    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=new_text,
        )
        entry.last_text = new_text
    except BadRequest as e:
        # If the countdown message was deleted or can't be edited, fall back to sending updates is spammy,
        # so we just stop the timer and notify once.
        logger.warning("Edit failed (%s). Stopping timer.", e)
        try:
            await context.bot.send_message(chat_id=entry.chat_id, text="⚠️ Timer stopped: I can't edit the countdown message.")
        except Exception:
            pass
        remove_timer(entry.chat_id, entry.job_name)
        return
    except Exception as e:
        logger.warning("Edit failed: %s", e)

    # ---- RESCHEDULE ----
    delay = choose_interval(remaining)
    context.job_queue.run_once(countdown_tick, delay, data=entry, name=entry.job_name)
