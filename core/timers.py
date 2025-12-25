# ==================================================
# core/timers.py — Timer Runtime Management
# ==================================================
#
# Low-level timer scheduling helpers: create, cancel, list timers via JobQueue and runtime store.
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

from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.countdown import countdown_tick
from core.timers_store import add_timer

logger = logging.getLogger(__name__)


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str | None = None,
    *,
    message_id: int | None = None,
    pin_message_id: int | None = None,  # kept for backwards compatibility (in case older code still uses it)
) -> TimerEntry:
    """
    Create a timer entry and schedule the first countdown tick.

    Important:
    - message_id: the timer message ID that will be edited by the countdown engine
    - pin_message_id: optional, kept for backwards compatibility with older code paths
    """

    if target_time.tzinfo is None:
        # Normalize to UTC to avoid timezone surprises in comparisons.
        target_time = target_time.replace(tzinfo=timezone.utc)

    entry = TimerEntry(
        chat_id=chat_id,
        message_id=message_id,
        target_time=target_time,
        message=message,
        pin_message_id=pin_message_id,
        last_text=None,
    )

    add_timer(entry)

    # First tick: schedule almost immediately.
    context.job_queue.run_once(
        countdown_tick,
        when=0.5,
        data=entry,
        name=entry.job_name,
    )

    logger.info("Timer created: %s", entry.job_name)
    return entry


def remove_timer_job(
    job_queue,
    chat_id: int,
    message_id: int,
) -> None:
    """Remove timer jobs from JobQueue / APScheduler.

    PTB JobQueue uses APScheduler under the hood. On every tick we may re-schedule the job
    using `run_once(..., name=entry.job_name)`. As a result, a single logical timer can have
    0..N APScheduler jobs that share the same `name` but have different internal IDs.

    We therefore remove *all* jobs with name == entry.job_name.
    """

    try:
        # Local import to avoid circular imports.
        from core.timers_store import list_timers

        entry = next(
            (t for t in list_timers(chat_id) if t.message_id == message_id),
            None,
        )
        if not entry:
            return

        job_name = entry.job_name

        # Preferred approach: use the PTB JobQueue API.
        jobs = []
        try:
            jobs = job_queue.get_jobs_by_name(job_name)
        except Exception:
            jobs = []

        if jobs:
            for j in jobs:
                try:
                    j.schedule_removal()
                except Exception:
                    # fallback
                    try:
                        j.remove()
                    except Exception:
                        pass
            return

        # Fallback: remove directly from the underlying APScheduler instance.
        try:
            scheduler = getattr(job_queue, "scheduler", None)
            if not scheduler:
                return

            for job in scheduler.get_jobs():
                if getattr(job, "name", None) == job_name:
                    try:
                        scheduler.remove_job(job.id)
                    except Exception:
                        pass
        except Exception:
            return

    except Exception as e:
        logger.warning("remove_timer_job failed: %s", e)
