# core/timers_store.py

from typing import Dict, List, Optional

# chat_id -> list[TimerEntry]
_TIMERS: Dict[int, List] = {}


def add_timer(chat_id: int, entry) -> None:
    _TIMERS.setdefault(chat_id, []).append(entry)


def get_timers(chat_id: int) -> List:
    return list(_TIMERS.get(chat_id, []))


def get_entry(job_name: str):
    for timers in _TIMERS.values():
        for entry in timers:
            if entry.job_name == job_name:
                return entry
    return None


def remove_timer(job_name: str) -> None:
    for chat_id, timers in list(_TIMERS.items()):
        _TIMERS[chat_id] = [
            entry for entry in timers if entry.job_name != job_name
        ]

        if not _TIMERS[chat_id]:
            del _TIMERS[chat_id]


def clear_timers(chat_id: int) -> None:
    _TIMERS.pop(chat_id, None)
