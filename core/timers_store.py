# core/timers_store.py

from typing import Dict, List
from core.models import TimerEntry

# chat_id -> list of timers
_TIMERS: Dict[int, List[TimerEntry]] = {}


def register_timer(entry: TimerEntry) -> None:
    _TIMERS.setdefault(entry.chat_id, []).append(entry)


def get_timers(chat_id: int) -> List[TimerEntry]:
    return _TIMERS.get(chat_id, [])


def pop_last_timer(chat_id: int) -> TimerEntry | None:
    timers = _TIMERS.get(chat_id)
    if not timers:
        return None
    return timers.pop()


def clear_timers(chat_id: int) -> List[TimerEntry]:
    return _TIMERS.pop(chat_id, [])
