# ==================================================
# services/timer_service.py — Timer Service Compatibility Layer
# ==================================================
#
# This file intentionally exists as a "compatibility shim".
#
# Context:
# - Earlier versions of the project had timer helpers in a single `service.py`.
# - The codebase was refactored into a clean layered structure:
#
#       commands/  →  services/  →  core/
#
# - Timer orchestration now lives in `core.timers` and `core.countdown`.
# - Some command modules (or older deployments) may still import timer helpers
#   from the services layer for convenience.
#
# Layer: Services
#
# Responsibilities:
# - Provide a stable, user-friendly API for timer creation
# - Normalize inputs (especially timezone handling)
# - Delegate the actual scheduling/state management to core.timers
#
# Boundaries:
# - This module does NOT send or edit Telegram messages.
#   Commands/daily jobs own network calls and UX.
#
# ==================================================

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from telegram.ext import ContextTypes

from core.timers import create_timer


# ==================================================
# Public API
# ==================================================
#
# These wrappers are intentionally small:
# - They keep commands readable.
# - They centralize time normalization rules (UTC).
# - They prevent duplication of "target_time math" across the codebase.
#
def start_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    seconds: int,
    message: str | None = None,
    *,
    message_id: int | None = None,
    pin_message_id: int | None = None,
):
    """Start a timer that fires after N seconds.

    Typical use:
    - /timer 10m (relative countdown)

    Args:
        context:
            PTB context (provides JobQueue + bot_data).
        chat_id:
            Target chat where the timer message lives.
        seconds:
            Duration (seconds). Negative values are clamped to 0.
        message:
            Optional label stored on the timer entry (used in cancel menus).
        message_id:
            Telegram message id that will be edited by the countdown engine.
        pin_message_id:
            Optional message id used by older code paths (kept for compatibility).

    Returns:
        TimerEntry (from core.timers), which includes job_name and target_time.
    """

    # --------------------------------------------------
    # Duration → absolute target timestamp (UTC)
    # --------------------------------------------------
    #
    # The engine operates in UTC to avoid local timezone surprises.
    # We clamp negatives to 0 to keep behavior predictable.
    #
    target_time = datetime.now(timezone.utc) + timedelta(seconds=max(0, int(seconds)))

    # --------------------------------------------------
    # Delegate to the core engine
    # --------------------------------------------------
    #
    # core.timers will:
    # - create a TimerEntry
    # - register it in the in-memory store
    # - schedule the first countdown tick via JobQueue
    #
    return create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time,
        message=message,
        message_id=message_id,
        pin_message_id=pin_message_id,
    )


def start_timer_at(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    target_time_utc: datetime,
    message: str | None = None,
    *,
    message_id: int | None = None,
    pin_message_id: int | None = None,
):
    """Start a timer for an absolute UTC datetime.

    Typical use:
    - /timerdate DD.MM.YYYY HH:MM (+TZ) (absolute deadline)

    Args:
        target_time_utc:
            Target datetime. If naive, it is treated as UTC.

    Returns:
        TimerEntry (from core.timers).
    """

    # --------------------------------------------------
    # Normalize target time to timezone-aware UTC
    # --------------------------------------------------
    #
    # The engine compares datetimes; mixing naive and aware values leads
    # to runtime errors. We normalize here to keep callers safe.
    #
    if target_time_utc.tzinfo is None:
        target_time_utc = target_time_utc.replace(tzinfo=timezone.utc)
    else:
        target_time_utc = target_time_utc.astimezone(timezone.utc)

    # --------------------------------------------------
    # Delegate to the core engine
    # --------------------------------------------------
    return create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time_utc,
        message=message,
        message_id=message_id,
        pin_message_id=pin_message_id,
    )
