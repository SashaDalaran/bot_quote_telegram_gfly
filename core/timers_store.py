# core/timers_store.py
from collections import defaultdict
from typing import List, Optional

from core.models import TimerEntry

# chat_id -> List[TimerEntry]
_TIMERS: dict[int, List[TimerEntry]] = defaultdict(list)


def add_entry(entry: TimerEntry) -> None:
    _TIMERS[entry.chat_id].append(entry)


def get_entry(chat_id: int, job_name: str) -> Optional[TimerEntry]:
    for entry in _TIMERS.get(chat_id, []):
        if entry.job_name == job_name:
            return entry
    return None


def get_timers(chat_id: int) -> List[TimerEntry]:
    return list(_TIMERS.get(chat_id, []))


def remove_entry(chat_id: int, job_name: str) -> None:
    _TIMERS[chat_id] = [
        e for e in _TIMERS.get(chat_id, [])
        if e.job_name != job_name
    ]

    if not _TIMERS[chat_id]:
        _TIMERS.pop(chat_id, None)


def clear_timers(chat_id: int) -> None:
    _TIMERS.pop(chat_id, None)
