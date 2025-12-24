# ==================================================
# core/timers.py — Timer creation helper
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
    pin_message_id: int | None = None,  # оставил для совместимости (если где-то ещё используется)
) -> TimerEntry:
    """
    Создаёт таймер и запускает первый тик countdown.

    ВАЖНО:
    - message_id: это ID сообщения таймера, которое мы будем edit'ить
    - pin_message_id: опционально, оставлен чтобы не ломать старый код
    """

    if target_time.tzinfo is None:
        # чтобы не было сюрпризов, приводим к UTC
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

    # Первый тик — почти сразу
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
    """Удаляет jobs таймера из JobQueue/APS cheduler.

    В python-telegram-bot JobQueue использует APScheduler. При каждом тике мы
    пересоздаём job через `run_once(..., name=entry.job_name)`. Поэтому у
    конкретного таймера может быть 0..N jobs с одинаковым `name` и разными `id`.

    Мы удаляем *все* jobs с name==entry.job_name.
    """

    try:
        # Локальный импорт, чтобы не поймать круговые импорты.
        from core.timers_store import list_timers

        entry = next(
            (t for t in list_timers(chat_id) if t.message_id == message_id),
            None,
        )
        if not entry:
            return

        job_name = entry.job_name

        # Предпочтительно через API PTB
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

        # Fallback: напрямую в APScheduler
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
