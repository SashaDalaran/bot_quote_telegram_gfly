# core/timers_store.py

from typing import Dict, List
from core.models import TimerEntry

TIMERS: Dict[int, List[TimerEntry]] = {}


def register_timer(chat_id: int, entry: TimerEntry) -> None:
    TIMERS.setdefault(chat_id, []).append(entry)


def get_timers(chat_id: int) -> List[TimerEntry]:
    return TIMERS.get(chat_id, [])


def clear_timers(chat_id: int) -> None:
    TIMERS.pop(chat_id, None)
