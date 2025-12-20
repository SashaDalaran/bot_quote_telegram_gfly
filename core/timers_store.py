# core/timers_store.py
from typing import Dict, List
from core.models import TimerEntry

# chat_id -> list[TimerEntry]
_TIMERS: Dict[int, List[TimerEntry]] = {}


def register_timer(entry: TimerEntry) -> None:
    _TIMERS.setdefault(entry.chat_id, []).append(entry)


def get_timers(chat_id: int) -> List[TimerEntry]:
    return list(_TIMERS.get(chat_id, []))


def clear_timers(chat_id: int) -> int:
    timers = _TIMERS.pop(chat_id, [])
    return len(timers)


def remove_entry(entry: TimerEntry) -> None:
    timers = _TIMERS.get(entry.chat_id)
    if not timers:
        return
    _TIMERS[entry.chat_id] = [t for t in timers if t.job_name != entry.job_name]
    if not _TIMERS[entry.chat_id]:
        _TIMERS.pop(entry.chat_id, None)


def get_entry(job_name: str) -> TimerEntry | None:
    for timers in _TIMERS.values():
        for entry in timers:
            if entry.job_name == job_name:
                return entry
    return None
