# services/timer_service.py
#
# Thin wrappers around core.timers.create_timer.
# Kept for backward compatibility (some older code may import these helpers).
#
# NOTE:
# - core.timers exposes create_timer(context, chat_id, target_time, ...)
# - There is no create_timer_at in core.timers in this repo.
#
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from telegram.ext import ContextTypes

from core.timers import create_timer


def start_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    seconds: int,
    message: str | None = None,
    *,
    message_id: int | None = None,
    pin_message_id: int | None = None,
):
    """Start a timer that fires after N seconds."""
    target_time = datetime.now(timezone.utc) + timedelta(seconds=max(0, int(seconds)))
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
    """Start a timer for an absolute UTC datetime."""
    # Ensure timezone-aware UTC datetime for safety
    if target_time_utc.tzinfo is None:
        target_time_utc = target_time_utc.replace(tzinfo=timezone.utc)
    else:
        target_time_utc = target_time_utc.astimezone(timezone.utc)

    return create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time_utc,
        message=message,
        message_id=message_id,
        pin_message_id=pin_message_id,
    )
