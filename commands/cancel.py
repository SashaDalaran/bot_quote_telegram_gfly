# ==================================================
# commands/cancel.py
# ==================================================

from datetime import datetime, timezone
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from core.timers_store import get_timers, clear_timers
from core.formatter import format_remaining_time


# /cancel — выбрать таймер
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    timers = get_timers(chat_id)

    if not timers:
        await update.message.reply_text("No timers to cancel.")
        return

    # если один таймер — отменяем сразу
    if len(timers) == 1:
        await _cancel_entry(update, context, timers[0])
        return

    # если несколько — показываем кнопки
    buttons = []
    now = datetime.now(timezone.utc)

    for entry in timers:
        remaining = int((entry.target_time - now).total_seconds())
        label = format_remaining_time(max(remaining, 0))

        buttons.append([
            InlineKeyboardButton(
                text=f"⏰ {label}",
                callback_data=f"cancel:{entry.job_name}",
            )
        ])

    await update.message.reply_text(
        "Which timer do you want to cancel?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# callback для кнопок
async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, job_name = query.data.split(":", 1)
    chat_id = query.message.chat_id
    timers = get_timers(chat_id)

    for entry in timers:
        if entry.job_name == job_name:
            await _cancel_entry(update, context, entry)
            await query.edit_message_text("⛔ Timer cancelled.")
            return

    await query.edit_message_text("❌ Timer not found.")


# /cancel_all — отменить всё
async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    timers = get_timers(chat_id)

    if not timers:
        await update.message.reply_text("No timers to cancel.")
        return

    for entry in timers:
        for job in context.job_queue.jobs():
            if job.name == entry.job_name:
                job.schedule_removal()

        try:
            await context.bot.unpin_chat_message(
                chat_id=chat_id,
                message_id=entry.message_id,
            )
        except Exception:
            pass

    clear_timers(chat_id)
    await update.message.reply_text("⛔ All timers cancelled.")


# 🔧 внутренняя функция
async def _cancel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE, entry):
    chat_id = entry.chat_id

    for job in context.job_queue.jobs():
        if job.name == entry.job_name:
            job.schedule_removal()

    try:
        await context.bot.unpin_chat_message(
            chat_id=chat_id,
            message_id=entry.message_id,
        )
    except Exception:
        pass

    clear_timers(chat_id)
