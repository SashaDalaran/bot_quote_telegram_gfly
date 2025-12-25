# ==================================================
# core/timers_store.py — In-Memory Timer Store
# ==================================================
#
# Minimal, process-local registry for active timers.
#
# Layer: Core
#
# Why this exists:
# - The bot schedules timer jobs via PTB JobQueue.
# - To support commands like /cancel and /cancelall, we need to track
#   "which timers exist in this chat" in a simple, fast structure.
#
# Data model:
# - This module stores TimerEntry objects in an in-memory dict:
#
#       chat_id -> [TimerEntry, TimerEntry, ...]
#
# Important limitations:
# - In-memory only: data is lost on restart / redeploy.
# - Single-process only: if you ever run multiple instances, timers must be stored
#   in an external database/shared storage to stay consistent.
#
# ==================================================

from __future__ import annotations

from typing import Dict, List, Optional

from core.models import TimerEntry

# ==================================================
# Internal state (process-local)
# ==================================================
#
# Keying by chat_id makes per-chat operations O(1) and keeps cancellation logic simple.
#
_TIMERS: Dict[int, List[TimerEntry]] = {}


# ==================================================
# Public API
# ==================================================
#
# NOTE:
# - These helpers return copies where appropriate to prevent accidental mutation
#   of internal state by callers.
#
def add_timer(entry: TimerEntry) -> None:
    """Register a timer entry.

    Args:
        entry:
            TimerEntry describing an active timer job.
    """
    _TIMERS.setdefault(entry.chat_id, []).append(entry)


def get_timers(chat_id: int) -> List[TimerEntry]:
    """Return a snapshot of active timers for a given chat."""
    # Return a copy to protect internal state.
    return list(_TIMERS.get(chat_id, []))


def pop_last_timer(chat_id: int) -> Optional[TimerEntry]:
    """Pop the most recently added timer for this chat.

    Used by UX flows that treat "last timer" as the default cancel target.

    Returns:
        The removed TimerEntry if present; otherwise None.
    """
    timers = _TIMERS.get(chat_id)
    if not timers:
        return None

    entry = timers.pop()

    # If no timers remain, remove the key entirely to keep the store tidy.
    if not timers:
        _TIMERS.pop(chat_id, None)

    return entry


def remove_timer(chat_id: int, message_id: int) -> bool:
    """Remove a timer by its message_id.

    Why message_id:
    - In this bot, a timer is associated with the message that the countdown engine edits.
    - Cancelling timers by message_id matches how users "see" timers in chat.

    Returns:
        True if at least one timer was removed, False otherwise.
    """
    timers = _TIMERS.get(chat_id)
    if not timers:
        return False

    # Filter out any entries matching the message id.
    new_list = [t for t in timers if t.message_id != message_id]
    removed = len(new_list) != len(timers)

    if not removed:
        return False

    if new_list:
        _TIMERS[chat_id] = new_list
    else:
        _TIMERS.pop(chat_id, None)

    return True


def clear_timers(chat_id: int) -> int:
    """Remove all timers for a chat.

    Returns:
        Number of timers removed.
    """
    lst = _TIMERS.pop(chat_id, [])
    return len(lst)


def list_timers(chat_id: int) -> List[TimerEntry]:
    """Compatibility alias: list timers.

    Historically, different modules used `get_timers` vs `list_timers`.
    Keeping both avoids churn and prevents breakage.
    """
    return get_timers(chat_id)
