# ==================================================
# core/timers.py
# ==================================================

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
    # один общий стор в bot_data
    store = context.bot_data.setdefault("timers_runtime", {})
    return store


def create_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time: datetime,
    message: str,
    pin_message_id: int,
) -> str:
    """
    Создаёт таймер и запускает первый тик.
    Возвращает job_name.
    """
    target_time = _utc(target_time)
    job_name = f"timer:{chat_id}:{int(target_time.timestamp())}"

    runtime = TimerRuntime(
        job_name=job_name,
        chat_id=chat_id,
        message_id=pin_message_id,
        target_time=target_time,
        label=message or "",
    )

    store = _store(context)
    store[job_name] = runtime

    # на всякий — уберём возможный хвост от прошлого такого же имени
    try:
        for j in context.job_queue.get_jobs_by_name(job_name):
            try:
                j.schedule_removal()
            except Exception:
                pass
    except Exception:
        pass

    # первый тик почти сразу
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


def cancel_timer(context: ContextTypes.DEFAULT_TYPE, job_name: str) -> bool:
    removed_any = False

    try:
        jobs = context.job_queue.get_jobs_by_name(job_name)
    except Exception:
        jobs = []

    for j in jobs:
        try:
            j.schedule_removal()
            removed_any = True
        except Exception:
            pass

    store = _store(context)
    if job_name in store:
        del store[job_name]
        removed_any = True

    return removed_any


def cancel_all_timers(context: ContextTypes.DEFAULT_TYPE, chat_id: Optional[int] = None) -> int:
    """
    Если chat_id=None — отменит вообще все.
    Если chat_id задан — только таймеры этого чата.
    """
    store = _store(context)
    to_cancel: List[str] = []

    for name, rt in list(store.items()):
        if chat_id is None or rt.chat_id == chat_id:
            to_cancel.append(name)

    count = 0
    for name in to_cancel:
        if cancel_timer(context, name):
            count += 1
    return count


def list_timers(context: ContextTypes.DEFAULT_TYPE, chat_id: Optional[int] = None) -> List[TimerRuntime]:
    store = _store(context)
    items = list(store.values())
    if chat_id is not None:
        items = [x for x in items if x.chat_id == chat_id]
    # сортировка по времени
    items.sort(key=lambda x: x.target_time)
    return items
