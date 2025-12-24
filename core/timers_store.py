# core/timers_store.py

from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, List, Optional

from core.models import TimerEntry

# chat_id -> list[TimerEntry]
_TIMERS: DefaultDict[int, List[TimerEntry]] = defaultdict(list)


def add_timer(entry: TimerEntry) -> None:
    _TIMERS[entry.chat_id].append(entry)


def get_timers(chat_id: int) -> List[TimerEntry]:
    return list(_TIMERS.get(chat_id, []))


def pop_last_timer(chat_id: int) -> Optional[TimerEntry]:
    """Remove and return last timer for chat."""
    timers = _TIMERS.get(chat_id)
    if not timers:
        return None
    entry = timers.pop()
    if not timers:
        _TIMERS.pop(chat_id, None)
    return entry


def remove_timer(chat_id: int, job_name: str) -> Optional[TimerEntry]:
    """Remove timer by job_name and return it."""
    timers = _TIMERS.get(chat_id)
    if not timers:
        return None

    for i, entry in enumerate(timers):
        if entry.job_name == job_name:
            removed = timers.pop(i)
            if not timers:
                _TIMERS.pop(chat_id, None)
            return removed

    return None


def clear_timers(chat_id: int) -> List[TimerEntry]:
    """Remove and return all timers for chat."""
    timers = _TIMERS.pop(chat_id, [])
    return list(timers)
