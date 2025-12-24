# ==================================================
# commands/cancel.py — /cancel + inline cancel buttons
# ==================================================

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _get_chat_timer_jobs(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    jobs = []
    for job in context.job_queue.jobs():
        data = getattr(job, "data", None)
        if getattr(data, "chat_id", None) == chat_id:
            jobs.append(job)
    return jobs


def _cancel_jobs(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int | None = None) -> int:
    jobs = _get_chat_timer_jobs(context, chat_id)

    removed = 0
    for job in jobs:
        data = getattr(job, "data", None)
        if message_id is not None and getattr(data, "message_id", None) != message_id:
            continue
        job.schedule_removal()
        removed += 1

    # опционально почистить store
    try:
        if message_id is None:
            from core.timers_store import remove_all_timers_for_chat
            remove_all_timers_for_chat(chat_id)
        else:
            from core.timers_store import remove_timer
            remove_timer(chat_id, message_id)
    except Exception:
        pass

    return removed


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/cancel -> показать кнопки отмены."""
    chat_id = update.effective_chat.id
    jobs = _get_chat_timer_jobs(context, chat_id)

    if not jobs:
        await update.message.reply_text("Активных таймеров нет ✅")
        return

    # собираем уникальные message_id таймеров
    message_ids = []
    for job in jobs:
        data = getattr(job, "data", None)
        mid = getattr(data, "message_id", None)
        if isinstance(mid, int) and mid not in message_ids:
            message_ids.append(mid)

    rows = []
    for mid in message_ids[:20]:
        rows.append([InlineKeyboardButton(f"❌ Отменить таймер (msg {mid})", callback_data=f"cancel_one|{mid}")])

    rows.append([InlineKeyboardButton("🧹 Cancel ALL timers", callback_data=f"cancel_all|{chat_id}")])

    await update.message.reply_text(
        "Выбери, что отменить:",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик inline cancel."""
    query = update.callback_query
    if not query:
        return

    data = query.data or ""
    await query.answer()

    chat_id = query.message.chat_id if query.message else None
    if chat_id is None:
        return

    # 1) cancel_timer:<message_id> (кнопка в самом таймере)
    if data.startswith("cancel_timer:"):
        try:
            mid = int(data.split(":", 1)[1])
        except Exception:
            await query.edit_message_text("⚠️ Некорректные данные cancel.")
            return

        removed = _cancel_jobs(context, chat_id, message_id=mid)

        # пытаемся обновить текст именно таймер-сообщения
        try:
            await query.edit_message_text(f"❌ Timer cancelled. (removed jobs: {removed})")
        except Exception:
            # если не получилось edit (например, уже изменено) — просто шлём сообщение
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Timer cancelled. (removed jobs: {removed})")
        return

    # 2) cancel_one|<message_id>
    if data.startswith("cancel_one|"):
        try:
            mid = int(data.split("|", 1)[1])
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Некорректные данные cancel_one.")
            return

        removed = _cancel_jobs(context, chat_id, message_id=mid)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Cancelled timer {mid}. (removed jobs: {removed})")
        return

    # 3) cancel_all|<chat_id>
    if data.startswith("cancel_all|"):
        removed = _cancel_jobs(context, chat_id, message_id=None)
        await context.bot.send_message(chat_id=chat_id, text=f"🧹 Cancelled ALL timers. (removed jobs: {removed})")
        return

    logger.info("Unknown cancel callback data: %s", data)
