# ==================================================
# services/timer_service.py
# ==================================================

from __future__ import annotations

import logging

from telegram.error import BadRequest
from telegram.ext import ContextTypes

from core.timers_store import get_timers, clear_timers, remove_timer

logger = logging.getLogger(__name__)


async def cancel_all_timers_service(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> int:
    """Cancel all timers in chat. Returns how many were canceled."""
    timers = list(get_timers(chat_id))
    if not timers:
        return 0

    jobs = context.job_queue.jobs()

    canceled = 0
    for entry in timers:
        job = next((j for j in jobs if j.name == entry.job_name), None)
        if job:
            job.schedule_removal()

        # Try to edit the countdown message to show it's canceled. If we can't edit it, ignore.
        try:
            await context.bot.edit_message_text(
                chat_id=entry.chat_id,
                message_id=entry.message_id,
                text="🛑 Timer canceled.",
            )
        except BadRequest:
            pass
        except Exception as e:
            logger.warning("Cancel edit failed: %s", e)

        remove_timer(entry.chat_id, entry.job_name)
        canceled += 1

    clear_timers(chat_id)
    return canceled
