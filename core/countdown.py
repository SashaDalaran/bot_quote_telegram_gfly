# core/countdown.py

import logging
from datetime import datetime, timezone

from telegram.error import BadRequest
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time, choose_update_interval
from core.timers_store import remove_timer

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """JobQueue callback. Edits the bot message with remaining time and reschedules itself."""
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
            logger.warning("Finalize failed: %s", e)
            try:
                await context.bot.send_message(chat_id=entry.chat_id, text=final_text)
            except Exception as e2:
                logger.warning("Finalize send fallback failed: %s", e2)
        except Exception as e:
            logger.warning("Finalize failed: %s", e)

        remove_timer(entry.chat_id, entry.job_name)
        return

    # ---- BUILD TEXT ----
    new_text = f"⏰ Time left: {format_remaining_time(remaining)}"
    if entry.message:
        new_text += f"\n{entry.message}"

    # don't spam same text
    if entry.last_text == new_text:
        delay = choose_update_interval(remaining)
        context.job_queue.run_once(countdown_tick, delay, data=entry, name=entry.job_name)
        return

    # ---- EDIT ----
    try:
        await context.bot.edit_message_text(
            chat_id=entry.chat_id,
            message_id=entry.message_id,
            text=new_text,
        )
        entry.last_text = new_text
    except BadRequest as e:
        logger.warning("Edit failed: %s", e)
        try:
            msg = await context.bot.send_message(chat_id=entry.chat_id, text=new_text)
            entry.message_id = msg.message_id
            entry.last_text = new_text
        except Exception as e2:
            logger.warning("Edit fallback send failed: %s", e2)
    except Exception as e:
        logger.warning("Edit failed: %s", e)

    # ---- RESCHEDULE ----
    delay = choose_update_interval(remaining)
    context.job_queue.run_once(countdown_tick, delay, data=entry, name=entry.job_name)
