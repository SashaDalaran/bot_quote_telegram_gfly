# commands/help_cmd.py

from telegram import Update
from telegram.ext import ContextTypes
from core.admin import is_admin


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📜 *Доступные команды*\n\n"

        "🔹 *Основные*\n"
        "/start — приветствие\n"
        "/help — список команд\n"
        "/quote — случайная цитата\n"
        "/murloc_ai — мурлокская мудрость 🐸\n\n"

        "⏱ *Таймеры*\n"
        "/timer — простой таймер\n"
        "Примеры:\n"
        "/timer 10s чай\n"
        "/timer 5m\n"
        "/timer 1h20m Boss pull\n\n"

        "/timerdate — таймер на конкретную дату\n"
        "Создаёт таймер, который сработает в указанное время\n\n"

        "Формат:\n"
        "/timerdate DD.MM.YYYY HH:MM +TZ текст [--pin]\n\n"

        "📌 Опция:\n"
        "--pin — закрепить сообщение таймера в чате\n\n"

        "Примеры:\n"
        "/timerdate 31.12.2025 23:59 +3 Новый год 🎆\n"
        "/timerdate 31.12.2025 23:59 +3 Новый год 🎆 --pin\n\n"


        "🎉 *Праздники*\n"
        "/holidays — праздники сегодня\n"
    )

    if is_admin(update):
        text += (
            "\n🛡 *Администратор*\n"
            "/cancel — отменить таймеры чата\n"
            "/cancelall — то же самое\n"
            "/chat_id — узнать chat_id\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
