# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

from core.formatter import choose_update_interval

logger = logging.getLogger(__name__)


def _format_left(seconds: int) -> str:
    if seconds < 0:
        seconds = 0

    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    sec = seconds % 60

    parts = []
    if days:
        parts.append(f"{days}д")
    if hours or days:
        parts.append(f"{hours}ч")
    if minutes or hours or days:
        parts.append(f"{minutes}м")
    parts.append(f"{sec}с")
    return " ".join(parts)


async def _safe_edit(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    text: str,
) -> None:
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except BadRequest as e:
        # Самые частые: "Message is not modified", "message to edit not found"
        msg = str(e).lower()
        if "message is not modified" in msg:
            return
        if "message to edit not found" in msg or "message can't be edited" in msg:
            logger.warning("Cannot edit timer message (chat=%s msg=%s): %s", chat_id, message_id, e)
            return
        logger.exception("BadRequest while editing timer message: %s", e)
    except TelegramError as e:
        logger.exception("TelegramError while editing timer message: %s", e)


def _remove_jobs_by_name(context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    """
    На всякий случай чистим дубликаты тиков (из-за гонок/двух запусков подряд).
    """
    try:
        jobs = context.job_queue.get_jobs_by_name(name)
    except Exception:
        jobs = []

    for j in jobs:
        try:
            j.schedule_removal()
        except Exception:
            # если job уже исчез — просто игнор
            pass


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Один тик. Мы используем run_once, поэтому:
    - текущий job одноразовый и сам исчезает;
    - НЕЛЬЗЯ делать schedule_removal() на текущем job (иначе JobLookupError).
    """
    job = context.job
    if job is None:
        return

    data: Dict[str, Any] = job.data or {}

    chat_id: Optional[int] = data.get("chat_id")
    message_id: Optional[int] = data.get("message_id")
    target_time: Optional[datetime] = data.get("target_time")
    label: str = data.get("label", "")
    job_name: str = data.get("job_name", job.name or "")

    if not chat_id or not message_id or not target_time:
        logger.warning("countdown_tick missing data: %s", data)
        return

    # нормализуем время
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    sec_left = int((target_time - now).total_seconds())

    # FINISH
    if sec_left <= 0:
        finish_text = f"⏰ Time is up!\n{label}".strip()
        await _safe_edit(context, chat_id, message_id, finish_text)
        return

    # UPDATE TEXT
    left_txt = _format_left(sec_left)
    text = f"⏳ {left_txt}\n{label}".strip()
    await _safe_edit(context, chat_id, message_id, text)

    # NEXT TICK (adaptive)
    interval = float(choose_update_interval(sec_left))

    # защита от дублей: перед планированием следующего тика чистим старые с тем же именем
    if job_name:
        _remove_jobs_by_name(context, job_name)

    context.job_queue.run_once(
        countdown_tick,
        when=interval,
        name=job_name,
        data={
            "chat_id": chat_id,
            "message_id": message_id,
            "target_time": target_time,
            "label": label,
            "job_name": job_name,
        },
    )
