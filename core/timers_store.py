# core/timers_store.py

from typing import Dict, List, Optional
from core.models import TimerEntry

# timer_id -> TimerEntry
_TIMERS: Dict[str, TimerEntry] = {}


def register_timer(entry: TimerEntry) -> None:
    _TIMERS[entry.job_name] = entry


def get_timer(timer_id: str) -> Optional[TimerEntry]:
    return _TIMERS.get(timer_id)


def get_timers_for_chat(chat_id: int) -> List[TimerEntry]:
    return [t for t in _TIMERS.values() if t.chat_id == chat_id]


def cancel_timer(timer_id: str) -> bool:
    return _TIMERS.pop(timer_id, None) is not None


def cancel_all_timers_for_chat(chat_id: int) -> int:
    to_delete = [k for k, v in _TIMERS.items() if v.chat_id == chat_id]

    for key in to_delete:
        del _TIMERS[key]

    return len(to_delete)
