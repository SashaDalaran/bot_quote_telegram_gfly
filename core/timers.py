# ==================================================
# core/timers.py — Timer Runtime Management
# ==================================================
#
# This module provides low-level runtime management
# for one-time countdown timers.
#
# Responsibilities:
# - Register timers in application runtime state
# - Schedule countdown jobs via JobQueue
# - Cancel scheduled timers
# - List active timers for inspection
#
# IMPORTANT:
# - This module does NOT parse user input
# - This module does NOT format messages
# - This module does NOT interact with Telegram API directly
#
# It acts as a thin coordination layer between:
# - JobQueue
# - core.countdown
# - in-memory runtime state
#
# ==================================================

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from telegram.ext import ContextTypes

from core.countdown import countdown_tick

logger = logging.getLogger(__name__)

# ==================================================
# Runtime model
# ==================================================
#
# Represents an active countdown timer stored
# in application runtime state.
#
# NOTE:
# - This model exists only in memory
# - It is lost on application restart
#
@dataclass(slots=True)
class TimerRuntime:
    """
    Active countdown timer runtime entry.

    Attributes:
        job_name (str):
            Unique JobQueue identifier.

        chat_id (int):
            Telegram chat ID where the timer runs.

        message_id (int):
            Telegram message ID being updated.

        target_time (datetime):
            Absolute moment when the timer ends (UTC).

        label (str):
            Optional user-provided description.
    """

    job_name: str
    chat_id: int
    message_id: int
    target_time: datetime
    label: str

# ==================================================
# Internal helpers
# ==================================================

def _utc(dt: datetime) -> datetime:
    """
    Normalize datetime to UTC.

    If the datetime is naive, it is assumed to be UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _store(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, TimerRuntime]:
    """
    Retrieve (or initialize) the in-memory timer store.

    Stored under:
        context.bot_data["timers_runtime"]
    """
    return context.bot_data.setdefault("timers_runtime", {})

# ==================================================
# Public API
# ==================================================

def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str,
    pin_message_id: int,
) -> str:
    """
    Create and schedule a new countdown timer.

    Steps:
    - Normalize target time to UTC
    - Create runtime model
    - Store runtime entry in bot_data
    - Schedule initial countdown job

    Returns:
        str: JobQueue job name
    """

    target_time = _utc(target_time)
    job_name = f"timer:{chat_id}:{pin_message_id}"

    runtime = TimerRuntime(
        job_name=job_name,
        chat_id=chat_id,
        message_id=pin_message_id,
        target_time=target_time,
        label=message or "",
    )

    # Store runtime entry
    _store(context)[job_name] = runtime

    # Schedule the first countdown tick immediately
    context.job_queue.run_once(
        countdown_tick,
        when=0.1,
        name=job_name,
        data={
            "chat_id": chat_id,
            "message_id": pin_message_id,
            "target_time": target_time,
            "label": runtime.label,
            "job_name": job_name,
        },
    )

    logger.info("Timer created: %s", job_name)
    return job_name


def cancel_timer(
    context: ContextTypes.DEFAULT_TYPE,
    job_name: str,
) -> bool:
    """
    Cancel a countdown timer by job name.

    Cancels:
    - All JobQueue jobs with this name
    - Corresponding runtime entry

    Returns:
        bool: True if anything was removed
    """

    removed = False

    # Remove scheduled jobs
    for job in context.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()
        removed = True

    # Remove runtime entry
    if job_name in _store(context):
        del _store(context)[job_name]
        removed = True

    return removed


def list_timers(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: Optional[int] = None,
) -> List[TimerRuntime]:
    """
    List active countdown timers.

    Args:
        chat_id (Optional[int]):
            If provided, only timers for this chat are returned.

    Returns:
        List[TimerRuntime]: Sorted list of active timers
    """

    timers = list(_store(context).values())

    if chat_id is not None:
        timers = [t for t in timers if t.chat_id == chat_id]

    timers.sort(key=lambda t: t.target_time)
    return timers
