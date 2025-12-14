# commands/help_cmd.py
from telegram import Update
from telegram.ext import ContextTypes
from core.admin import is_admin


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    text = (
        "📜 <b>Доступные команды</b>\n\n"
        "🔹 <b>Основные</b>\n"
        "/start — приветствие\n"
        "/help — список команд\n"
        "/quote — случайная цитата\n"
        "/murloc_ai — мурлокская мудрость 🐸\n\n"

        "⏱ <b>Таймеры</b>\n"
        "/timer — простой таймер\n"
        "/timerdate — таймер на дату\n\n"

        "🎉 <b>Праздники</b>\n"
        "/holidays — праздники сегодня\n"
    )

    if await is_admin(update, context):
        text += (
            "\n🛡 <b>Администратор</b>\n"
            "/cancel — отменить таймеры\n"
            "/cancelall — отменить все\n"
            "/chat_id — узнать chat_id\n"
        )

    # ✅ Универсальная отправка (работает ВЕЗДЕ)
    await context.bot.send_message(
        chat_id=chat.id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
