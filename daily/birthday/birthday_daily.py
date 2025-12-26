# daily/birthday/birthday_daily.py

import logging
from datetime import date, datetime, timezone, timedelta, time
from typing import Dict, List

from telegram.ext import Application

from services.birthday_format import format_birthday_message
from services.birthday_service import get_today_birthday_payload, load_birthday_events
from services.channel_ids import parse_chat_ids

logger = logging.getLogger(__name__)

TZ = timezone(timedelta(hours=3))  # GMT+3 (как holidays/banlu)
SCHEDULED_AT = time(hour=10, minute=3)  # твои ожидаемые 10:03 (GMT+3)

def _parse_channel_ids() -> List[int]:
    return parse_chat_ids("BIRTHDAY_CHANNEL_ID")


async def send_birthday_daily(app: Application) -> None:
    channels = _parse_channel_ids()
    if not channels:
        logger.warning("Birthday daily: no BIRTHDAY_CHANNEL_ID configured")
        return

    # ✅ де-дуп по ЛОКАЛЬНОМУ дню (GMT+3), а не по UTC
    last_sent: Dict[int, str] = app.bot_data.setdefault("birthday_last_sent", {})
    now_local = datetime.now(TZ)
    today = now_local.date()
    today_key = now_local.strftime("%Y-%m-%d")

    events = load_birthday_events()
    payload = get_today_birthday_payload(events=events, today=today)

    if not payload:
        logger.info("Birthday daily: nothing to send today")
        return

    text = format_birthday_message(payload, today)

    for chat_id in channels:
        if last_sent.get(chat_id) == today_key:
            continue
        try:
            await app.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            last_sent[chat_id] = today_key
        except Exception as e:
            logger.exception("Birthday daily send failed for chat_id=%s: %s", chat_id, e)


def setup_birthday_daily(application: Application) -> None:
    # ✅ ежедневка в 10:03 GMT+3
    application.job_queue.run_daily(
        lambda ctx: send_birthday_daily(ctx.application),
        time=time(hour=SCHEDULED_AT.hour, minute=SCHEDULED_AT.minute, tzinfo=TZ),
        name="birthday_daily",
    )

    # ✅ catch-up — но только если бот стартанул ПОСЛЕ времени рассылки
    now_local = datetime.now(TZ).time()
    if now_local >= SCHEDULED_AT:
        application.job_queue.run_once(
            lambda ctx: send_birthday_daily(ctx.application),
            when=timedelta(seconds=8),
            name="birthday_catch_up",
        )
