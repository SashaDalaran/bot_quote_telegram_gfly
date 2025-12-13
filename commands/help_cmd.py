from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "📖 **Just Quotes Bot — Command List**\n\n"

    "🎲 **Quotes**\n"
    "/quote — Random game quote\n"
    "/banlu — Ban’Lu wisdom\n"
    "/murloc_ai — Generate Murloc AI wisdom\n\n"

    "⏱ **Simple Timer**\n"
    "/timer 10m text\n"
    "_Supports:_ 10s, 5m, 1h, 1h20m\n"
    "_Example:_\n"
    "`/timer 30s Time to fight!`\n\n"

    "📅 **Date Timer**\n"
    "/timerdate DD.MM.YYYY HH:MM +TZ text --pin\n"
    "_Example:_\n"
    "`/timerdate 31.12.2025 23:59 +3 New Year! --pin`\n\n"
    "Countdown format: days / hours / minutes / seconds\n"
    "`--pin` is optional\n\n"

    "🎉 **Holidays**\n"
    "/holidays — Next upcoming holiday\n\n"

    "🛠 **Timer Management**\n"
    "/timers — list active timers\n"
    "/cancel <ID> — cancel one timer\n"
    "/cancelall — delete all timers in this channel\n\n"

    "🐸 *Murloc Edition*"
)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown"
    )
