# core/timers_store.py

from typing import Dict, List
from core.models import TimerEntry

_TIMERS: Dict[str, TimerEntry] = {}


def register_timer(entry: TimerEntry) -> None:
    _TIMERS[entry.job_name] = entry


def get_timer(job_name: str) -> TimerEntry | None:
    return _TIMERS.get(job_name)


def remove_timer(job_name: str) -> None:
    _TIMERS.pop(job_name, None)


def get_timers(chat_id: int | None = None) -> List[TimerEntry]:
    if chat_id is None:
        return list(_TIMERS.values())
    return [t for t in _TIMERS.values() if t.chat_id == chat_id]


def clear_timers(chat_id: int | None = None) -> None:
    if chat_id is None:
        _TIMERS.clear()
        return

    for key in list(_TIMERS.keys()):
        if _TIMERS[key].chat_id == chat_id:
            del _TIMERS[key]
