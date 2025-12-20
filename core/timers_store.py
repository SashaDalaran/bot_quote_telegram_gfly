# ==================================================
# core/timers_store.py
# In-memory storage for active timers
# ==================================================

from collections import defaultdict
from typing import Dict, List, Optional

from core.models import TimerEntry


# chat_id -> list of TimerEntry
_TIMERS: Dict[int, List[TimerEntry]] = defaultdict(list)


# --------------------------------------------------
# Add timer
# --------------------------------------------------
def add_entry(entry: TimerEntry) -> None:
    _TIMERS[entry.chat_id].append(entry)


# --------------------------------------------------
# Get all timers for chat
# --------------------------------------------------
def get_timers(chat_id: int) -> List[TimerEntry]:
    return list(_TIMERS.get(chat_id, []))


# --------------------------------------------------
# Get one timer by job_name
# --------------------------------------------------
def get_entry(chat_id: int, job_name: str) -> Optional[TimerEntry]:
    for entry in _TIMERS.get(chat_id, []):
        if entry.job_name == job_name:
            return entry
    return None


# --------------------------------------------------
# Remove one timer
# --------------------------------------------------
def remove_entry(chat_id: int, job_name: str) -> None:
    if chat_id not in _TIMERS:
        return

    _TIMERS[chat_id] = [
        entry for entry in _TIMERS[chat_id]
        if entry.job_name != job_name
    ]

    if not _TIMERS[chat_id]:
        _TIMERS.pop(chat_id, None)


# --------------------------------------------------
# Clear all timers for chat
# --------------------------------------------------
def clear_timers(chat_id: int) -> None:
    _TIMERS.pop(chat_id, None)
