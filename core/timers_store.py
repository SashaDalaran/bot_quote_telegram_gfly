# core/timers_store.py
from __future__ import annotations

from typing import Dict, List, Optional
from core.models import TimerEntry

# chat_id -> [TimerEntry, ...]
_TIMERS: Dict[int, List[TimerEntry]] = {}


def add_timer(entry: TimerEntry) -> None:
    _TIMERS.setdefault(entry.chat_id, []).append(entry)


def get_timers(chat_id: int) -> List[TimerEntry]:
    return list(_TIMERS.get(chat_id, []))


def pop_last_timer(chat_id: int) -> Optional[TimerEntry]:
    lst = _TIMERS.get(chat_id)
    if not lst:
        return None
    entry = lst.pop()
    if not lst:
        _TIMERS.pop(chat_id, None)
    return entry


def remove_timer(chat_id: int, message_id: int | None) -> bool:
    lst = _TIMERS.get(chat_id)
    if not lst:
        return False

    new_lst = [t for t in lst if getattr(t, "message_id", None) != message_id]
    removed = len(new_lst) != len(lst)

    if new_lst:
        _TIMERS[chat_id] = new_lst
    else:
        _TIMERS.pop(chat_id, None)

    return removed


def clear_timers(chat_id: int) -> int:
    lst = _TIMERS.pop(chat_id, [])
    return len(lst)


def list_timers(chat_id: int) -> List[TimerEntry]:
    return get_timers(chat_id)
