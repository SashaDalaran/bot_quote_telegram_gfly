import logging
from datetime import datetime, timezone
from typing import Dict, List

from telegram.ext import ContextTypes

from timers.models import TimerEntry, RepeatEntry
from timers.formatter import (
    choose_update_interval,
    format_remaining_time,
    pretty_time_short,
)

logger = logging.getLogger(__name__)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None:
        return

    entry: TimerEntry = job.data
    chat_id = entry.chat_id
    pin_id = entry.pin_message_id

    now_utc = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now_utc).total_seconds())

    if remaining <= 0:
        # Final update and notify
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=pin_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Failed to edit final countdown message: %s", e)

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Failed to send final timer message: %s", e)

        return

    # Build updated text
    lines: List[str] = [
        f"⏰ Time left: {format_remaining_time(remaining)}"
    ]

    if entry.message:
        lines.append(entry.message)

    if entry.quote:
        lines.append(f"💬 {entry.quote}")

    new_text = "\n".join(lines)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=pin_id,
            text=new_text,
        )
    except Exception as e:
        logger.warning("Cannot edit countdown message: %s", e)

    # schedule next tick
    delay = choose_update_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )


async def repeat_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None:
        return

    entry: RepeatEntry = job.data
    text = entry.message or f"⏰ Repeat timer: {pretty_time_short(entry.interval)}"

    try:
        await context.bot.send_message(
            chat_id=entry.chat_id,
            text=text,
        )
    except Exception as e:
        logger.warning("Failed to send repeat timer message: %s", e)
