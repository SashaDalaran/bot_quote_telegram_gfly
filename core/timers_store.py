# core/timers_store.py

from typing import Dict, List
from core.models import TimerEntry

# In-memory store
_TIMERS: Dict[str, TimerEntry] = {}


# =========================
# Basic operations
# =========================

def register_timer(entry: TimerEntry) -> None:
    """
    Save / overwrite timer entry by job_name
    """
    _TIMERS[entry.job_name] = entry


def get_entry(job_name: str) -> TimerEntry | None:
    """
    Get single timer entry by job_name
    """
    return _TIMERS.get(job_name)


def remove_entry(job_name: str) -> None:
    """
    Remove timer entry
    """
    _TIMERS.pop(job_name, None)


# =========================
# Bulk helpers
# =========================

def get_timers() -> List[TimerEntry]:
    """
    Return all active timers
    """
    return list(_TIMERS.values())


def clear_timers() -> None:
    """
    Remove all timers
    """
    _TIMERS.clear()
