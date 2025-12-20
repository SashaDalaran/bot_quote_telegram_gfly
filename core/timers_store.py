# core/timers_store.py
from typing import Dict, List
from core.models import TimerEntry

_TIMERS: Dict[int, List[TimerEntry]] = {}


def register_timer(entry: TimerEntry) -> None:
    _TIMERS.setdefault(entry.chat_id, []).append(entry)


def get_timers(chat_id: int) -> List[TimerEntry]:
    return list(_TIMERS.get(chat_id, []))


def remove_timer(chat_id: int, entry_id: str) -> None:
    timers = _TIMERS.get(chat_id, [])
    _TIMERS[chat_id] = [t for t in timers if t.id != entry_id]

    if not _TIMERS[chat_id]:
        _TIMERS.pop(chat_id, None)


def clear_timers(chat_id: int) -> None:
    _TIMERS.pop(chat_id, None)
