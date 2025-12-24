from __future__ import annotations

from datetime import datetime, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time

CB_PREFIX = "cancel_timer:"


def _get_chat_timer_jobs(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    # JobQueue in python-telegram-bot is backed by APScheduler
    jobs = context.application.job_queue.jobs()
    return [j for j in jobs if j.name and j.name.startswith(f"timer:{chat_id}:")]


def _label_for_job(job) -> str:
    entry = getattr(job, "data", None)
    now = datetime.now(timezone.utc)

    # Best effort красивый текст
    if entry and hasattr(entry, "target_time"):
        remaining = int((entry.target_time - now).total_seconds())
        remaining = max(0, remaining)
        label = f"⏰ {format_remaining_time(remaining)}"
        if hasattr(entry, "message_id"):
            label += f" • msg {entry.message_id}"
        return label

    return f"⏰ {job.name}"


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    jobs = _get_chat_timer_jobs(context, chat_id)

    if not jobs:
        await update.message.reply_text("Нет активных таймеров.")
        return

    jobs = sorted(jobs, key=lambda j: (j.next_t if hasattr(j, "next_t") else 0))

    keyboard = []
    for job in jobs[:20]:  # чтобы не сделать гигантскую клаву
        keyboard.append(
            [InlineKeyboardButton(_label_for_job(job), callback_data=f"{CB_PREFIX}{job.name}")]
        )

    keyboard.append([InlineKeyboardButton("❌ Отменить ВСЕ таймеры", callback_data=f"{CB_PREFIX}__ALL__")])

    await update.message.reply_text(
        "Какой таймер отменить?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    jobs = _get_chat_timer_jobs(context, chat_id)

    if not jobs:
        await update.message.reply_text("Нет активных таймеров.")
        return

    for job in jobs:
        job.schedule_removal()

    await update.message.reply_text(f"✅ Отменил все таймеры: {len(jobs)}")


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    payload = query.data[len(CB_PREFIX):]

    if payload == "__ALL__":
        jobs = _get_chat_timer_jobs(context, chat_id)
        for job in jobs:
            job.schedule_removal()
        await query.edit_message_text(f"✅ Отменил все таймеры: {len(jobs)}")
        return

    # Найти job по имени
    jobs = [j for j in context.application.job_queue.jobs() if j.name == payload]

    if not jobs:
        await query.edit_message_text("❗ Этот таймер уже не найден (возможно, уже завершён).")
        return

    for job in jobs:
        job.schedule_removal()

    await query.edit_message_text("✅ Таймер отменён.")
