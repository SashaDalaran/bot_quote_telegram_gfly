# services/timer_service.py
from __future__ import annotations

from datetime import datetime
from telegram.ext import ContextTypes

from core.timers import create_timer, create_timer_at


async def start_timer(context: ContextTypes.DEFAULT_TYPE, chat_id: int, seconds: int, message: str = "", *, pin: bool = False):
    return await create_timer(context, chat_id, seconds, message, pin=pin)


async def start_timer_at(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target_time_utc: datetime, message: str = "", *, pin: bool = False):
    return await create_timer_at(context, chat_id, target_time_utc, message, pin=pin)
