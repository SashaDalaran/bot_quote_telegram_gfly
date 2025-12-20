# core/timers_store.py
from typing import Dict, List
from core.models import TimerEntry

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
    if entry in timers:
        timers.remove(entry)
    if not timers:
        _TIMERS.pop(entry.chat_id, None)
