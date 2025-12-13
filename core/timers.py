# core/timers.py

import logging
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def cancel_all_timers(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
) -> int:
    """
    Cancels ALL timers (one-time + repeat) for this chat via JobQueue.
    """
    removed = 0

    for job in context.job_queue.jobs():
        data = job.data
        if hasattr(data, "chat_id") and data.chat_id == chat_id:
            job.schedule_removal()
            removed += 1

    logger.info("Canceled %s timers for chat %s", removed, chat_id)
    return removed
