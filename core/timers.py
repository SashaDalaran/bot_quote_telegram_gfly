# core/timers.py

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from telegram.ext import ContextTypes
from core.countdown import countdown_tick

logger = logging.getLogger(__name__)


@dataclass
class TimerRuntime:
    job_name: str
    chat_id: int
    message_id: int
    target_time: datetime
    label: str


def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _store(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, TimerRuntime]:
    return context.bot_data.setdefault("timers_runtime", {})


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str,
    pin_message_id: int,
) -> str:
    target_time = _utc(target_time)
    job_name = f"timer:{chat_id}:{pin_message_id}"

    runtime = TimerRuntime(
        job_name=job_name,
        chat_id=chat_id,
        message_id=pin_message_id,
        target_time=target_time,
        label=message or "",
    )

    _store(context)[job_name] = runtime

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

    return job_name


def cancel_timer(context: ContextTypes.DEFAULT_TYPE, job_name: str) -> bool:
    removed = False

    for job in context.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()
        removed = True

    if job_name in _store(context):
        del _store(context)[job_name]
        removed = True

    return removed


def list_timers(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: Optional[int] = None,
) -> List[TimerRuntime]:
    timers = list(_store(context).values())
    if chat_id:
        timers = [t for t in timers if t.chat_id == chat_id]
    timers.sort(key=lambda t: t.target_time)
    return timers
