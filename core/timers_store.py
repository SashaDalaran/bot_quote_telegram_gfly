# core/timers_store.py

from typing import Dict, List, Optional
from core.models import TimerEntry

# =========================
# In-memory storage
# =========================

_TIMERS: Dict[str, TimerEntry] = {}


# =========================
# Register / get
# =========================

def register_timer(entry: TimerEntry) -> None:
    _TIMERS[entry.job_name] = entry


def get_entry(job_name: str) -> Optional[TimerEntry]:
    return _TIMERS.get(job_name)


# =========================
# Remove (aliases)
# =========================

def remove_entry(job_name: str) -> None:
    _TIMERS.pop(job_name, None)


def remove_timer(job_name: str) -> None:
    # alias for compatibility
    remove_entry(job_name)


# =========================
# Queries
# =========================

def get_timers(chat_id: Optional[int] = None) -> List[TimerEntry]:
    """
    - get_timers() -> all timers
    - get_timers(chat_id) -> timers for chat
    """
    if chat_id is None:
        return list(_TIMERS.values())

    return [
        entry
        for entry in _TIMERS.values()
        if entry.chat_id == chat_id
    ]


def clear_timers(chat_id: Optional[int] = None) -> None:
    """
    - clear_timers() -> clear all
    - clear_timers(chat_id) -> clear only chat timers
    """
    if chat_id is None:
        _TIMERS.clear()
        return

    for job_name, entry in list(_TIMERS.items()):
        if entry.chat_id == chat_id:
            _TIMERS.pop(job_name, None)
