# ==================================================
# core/countdown.py
# ==================================================

import logging
from datetime import datetime, timezone

from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    if job is None:
        return

    data = job.data or {}
    job_name = data.get("job_name")

    # ==================================================
    # 🔴 GUARD: если таймер отменён — УМЕРЕТЬ
    # ==================================================
    store = context.bot_data.get("timers_runtime", {})
    if not job_name or job_name not in store:
        try:
            job.schedule_removal()
        except Exception:
            pass
        return
    # ==================================================

    chat_id = data["chat_id"]
    message_id = data["message_id"]
    target_time = data["target_time"]
    label = data.get("label", "")

    now = _utc_now()
    remaining = int((target_time - now).total_seconds())

    # ---------- время вышло ----------
    if remaining <= 0:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⏰ Time is up!\n{label}" if label else "⏰ Time is up!",
            )
        except Exception:
            pass

        # удаляем runtime
        store.pop(job_name, None)

        try:
            job.schedule_removal()
        except Exception:
            pass
        return

    # ---------- формат времени ----------
    days, rem = divmod(remaining, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    parts = []
    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes:
        parts.append(f"{minutes}м")
    parts.append(f"{seconds}с")

    text = f"⏳ {' '.join(parts)}"
    if label:
        text += f"\n{label}"

    # ---------- обновляем сообщение ----------
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except Exception:
        pass

    # ---------- следующий тик ----------
    context.job_queue.run_once(
        countdown_tick,
        when=5,
        name=job_name,
        data=data,
    )
