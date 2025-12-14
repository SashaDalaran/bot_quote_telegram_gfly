# commands/help_cmd.py

from telegram import Update
from telegram.ext import ContextTypes
from core.admin import is_admin


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    text = (
        "📜 <b>Доступные команды</b>\n\n"

        "🔹 <b>Основные</b>\n"
        "/start — приветственное сообщение\n"
        "/help — показать это меню\n"
        "/quote — случайная цитата\n"
        "/murloc_ai — мурлокская мудрость 🐸\n\n"

        "⏱ <b>Таймеры</b>\n"
        "/timer — простой таймер\n"
        "Примеры:\n"
        "/timer 10s чай\n"
        "/timer 5m\n"
        "/timer 1h20m Boss pull\n\n"

        "/timerdate — таймер на конкретную дату\n"
        "Формат:\n"
        "/timerdate DD.MM.YYYY HH:MM +TZ текст [--pin]\n\n"
        "Примеры:\n"
        "/timerdate 31.12.2025 23:59 +3 Новый год 🎆\n"
        "/timerdate 31.12.2025 23:59 +3 Новый год 🎆 --pin\n\n"

        "📌 <b>Опция</b>\n"
        "--pin — закрепить сообщение таймера в чате\n\n"

        "🎉 <b>Праздники</b>\n"
        "/holidays — праздники сегодня\n\n"

        "ℹ️ <i>Команды работают в личных сообщениях и группах.\n"
        "Канал используется для автоматических публикаций.</i>\n"
    )

    if await is_admin(update, context):
        text += (
            "\n🛡 <b>Администратор</b>\n"
            "/cancel — отменить таймеры в чате\n"
            "/cancelall — отменить все таймеры\n"
            "/chat_id — узнать ID чата\n"
        )

    await context.bot.send_message(
        chat_id=chat.id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
