import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from core.admin import is_admin
from core.formatter import format_remaining_time
from core.timers import remove_timer_job
from core.timers_store import list_timers, remove_timer

logger = logging.getLogger(__name__)


async def _unpin_if_pinned(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int | None) -> None:
    """Unpin конкретное сообщение, если оно сейчас закреплено."""
    if not message_id:
        return
    try:
        chat = await context.bot.get_chat(chat_id)
        pinned = getattr(chat, "pinned_message", None)
        if pinned and pinned.message_id == message_id:
            await context.bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)

            # Подстраховка: иногда клиент показывает закреплённое, если оно не снялось.
            chat2 = await context.bot.get_chat(chat_id)
            pinned2 = getattr(chat2, "pinned_message", None)
            if pinned2 and pinned2.message_id == message_id:
                await context.bot.unpin_chat_message(chat_id=chat_id)
    except Exception as e:
        logger.warning("Unpin failed for chat=%s msg=%s: %s", chat_id, message_id, e)


def _short(text: str, limit: int = 26) -> str:
    text = (text or "").replace("\n", " ").strip()
    if not text:
        return ""
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _timer_label(entry) -> str:
    """Короткое, понятное имя таймера для кнопки."""
    now = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now).total_seconds())
    if remaining < 0:
        remaining = 0

    msg = _short(entry.message)
    if not msg:
        msg = "без текста"

    # Держим текст кнопки коротким (Telegram любит лимиты)
    # и добавляем id для уникальности/отладки
    return f"❌ {format_remaining_time(remaining)} — {msg} (#{entry.message_id})"


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Админ‑only
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Эта команда доступна только администраторам.")
        return

    chat_id = update.effective_chat.id
    timers = list_timers(chat_id)

    if not timers:
        await update.message.reply_text("Нет активных таймеров.")
        return

    # Сортируем по ближайшему окончанию
    timers.sort(key=lambda t: t.target_time)

    keyboard = []
    for t in timers:
        keyboard.append(
            [InlineKeyboardButton(_timer_label(t), callback_data=f"cancel_one:{chat_id}:{t.message_id}")]
        )

    # ВАЖНО: команду /cancelall убираем, но кнопку "удалить все" оставляем внутри /cancel
    keyboard.append(
        [InlineKeyboardButton("🧹 Отменить ВСЕ таймеры", callback_data=f"cancel_all:{chat_id}")]
    )

    await update.message.reply_text(
        "Выбери, что отменить:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    # Админ‑only (важно: кнопки может нажать кто угодно в группе)
    if not await is_admin(update, context):
        await query.answer("⛔ Только администратор", show_alert=True)
        return

    try:
        action, chat_id_str, *rest = query.data.split(":")
        chat_id = int(chat_id_str)
    except Exception:
        await query.answer("Некорректные данные", show_alert=True)
        return

    job_queue = context.job_queue

    if action == "cancel_one":
        if not rest:
            await query.answer("Некорректные данные", show_alert=True)
            return
        msg_id = int(rest[0])

        # Находим запись таймера (нужна для unpin)
        entry = next((t for t in list_timers(chat_id) if t.message_id == msg_id), None)
        if not entry:
            await query.answer("Таймер уже не найден.")
            return

        # Если это было закреплённое сообщение — снимаем закреп
        await _unpin_if_pinned(context, chat_id, entry.pin_message_id or msg_id)

        remove_timer_job(job_queue, chat_id, msg_id)
        remove_timer(chat_id, msg_id)

        # Обновляем текст самого таймера (если он ещё есть)
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text="⛔ Таймер отменён.",
            )
        except Exception as e:
            logger.warning("Edit cancelled timer message failed: %s", e)

        await query.answer("Ок")
        return

    if action == "cancel_all":
        entries = list_timers(chat_id)

        # Сначала снимаем pin (если pinned_message совпадает с таймером)
        for entry in entries:
            if entry.pin_message_id:
                await _unpin_if_pinned(context, chat_id, entry.pin_message_id)

        # Потом снимаем джобы + удаляем записи
        for entry in entries:
            remove_timer_job(job_queue, chat_id, entry.message_id)
            remove_timer(chat_id, entry.message_id)

        await query.answer("Ок")
        try:
            await query.edit_message_text("✅ Все таймеры отменены.")
        except Exception:
            # если не можем редактировать меню — просто молча
            pass
        return

    await query.answer("Неизвестное действие", show_alert=True)
