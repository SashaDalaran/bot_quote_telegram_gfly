# core/timers_store.py

from typing import Dict, List
from core.models import TimerEntry

_TIMERS: Dict[int, List[TimerEntry]] = {}


def register_timer(entry: TimerEntry) -> None:
    _TIMERS.setdefault(entry.chat_id, []).append(entry)


def pop_last_timer(chat_id: int) -> TimerEntry | None:
    if chat_id not in _TIMERS or not _TIMERS[chat_id]:
        return None
    return _TIMERS[chat_id].pop()


def get_timers(chat_id: int) -> List[TimerEntry]:
    return list(_TIMERS.get(chat_id, []))


def clear_timers(chat_id: int) -> None:
    _TIMERS.pop(chat_id, None)
