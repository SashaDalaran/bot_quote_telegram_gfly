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
    """
    Alias for backward compatibility
    """
    remove_entry(job_name)


# =========================
# Bulk helpers
# =========================

def get_timers() -> List[TimerEntry]:
    return list(_TIMERS.values())


def clear_timers() -> None:
    _TIMERS.clear()
