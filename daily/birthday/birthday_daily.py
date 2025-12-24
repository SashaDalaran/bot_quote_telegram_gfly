import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from telegram.ext import Application

from services.birthday_format import format_birthday_message
from services.birthday_service import get_today_birthday_payload, load_birthday_events
from services.channel_ids import parse_chat_ids


logger = logging.getLogger(__name__)


def _parse_channel_ids() -> List[int]:
    """Read channels from env.

    Preferred: BIRTHDAY_CHANNEL_IDS="-100..,-100.."
    Backward compatible: BIRTHDAY_CHANNEL_ID="-100.."
    """
    # Preferred: BIRTHDAY_CHANNEL_ID (can contain one ID or many comma-separated IDs)
    # Back-compat: BIRTHDAY_CHANNEL_IDS
    return parse_chat_ids("BIRTHDAY_CHANNEL_ID", fallback_keys=("BIRTHDAY_CHANNEL_IDS",))


async def send_birthday_daily(app: Application) -> None:
    channels = _parse_channel_ids()
    if not channels:
        logger.warning("Birthday daily: no BIRTHDAY_CHANNEL_ID(S) configured")
        return

    # In-memory de-duplication per channel per UTC day.
    last_sent: Dict[int, str] = app.bot_data.setdefault("birthday_last_sent", {})
    today_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    events = load_birthday_events()
    payload = get_today_birthday_payload(events=events)

    if not any(payload.values()):
        logger.info("Birthday daily: nothing to send today")
        return

    text = format_birthday_message(payload)

    for chat_id in channels:
        if last_sent.get(chat_id) == today_key:
            continue
        try:
            await app.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            last_sent[chat_id] = today_key
        except Exception as e:
            logger.exception("Birthday daily send failed for chat_id=%s: %s", chat_id, e)


def setup_birthday_daily(application: Application) -> None:
    """Schedule the birthday/hero/challenge daily post.

    Uses UTC time to match other jobs.
    """

    # Run daily at 10:07 UTC (keeps separation from holidays at 10:05).
    application.job_queue.run_daily(
        lambda ctx: send_birthday_daily(ctx.application),
        time=datetime(1970, 1, 1, 10, 7, tzinfo=timezone.utc).timetz(),
        name="birthday_daily",
    )

    # Catch-up shortly after boot (best effort), like other modules.
    application.job_queue.run_once(
        lambda ctx: send_birthday_daily(ctx.application),
        when=timedelta(seconds=8),
        name="birthday_catch_up",
    )
