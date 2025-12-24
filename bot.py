# ==================================================
# bot.py — Telegram Bot Entry Point
# ==================================================

import logging
import traceback

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from core.settings import TELEGRAM_BOT_TOKEN, QUOTES_FILE, BANLU_QUOTES_FILE

from services.quotes_service import load_quotes
from services.banlu_service import load_banlu_quotes

from commands.chat_id import chat_id_command
from commands.start import start_command
from commands.help_cmd import help_command
from commands.quotes import quote_command

from commands.simple_timer import timer_command
from commands.date_timer import timerdate_command

from commands.cancel import cancel_command, cancel_callback

from commands.holidays_cmd import holidays_command
from commands.murloc_ai import murloc_ai_command

from daily.banlu.banlu_daily import setup_banlu_daily
from daily.holidays.holidays_daily import setup_holidays_daily


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    traceback.print_exception(
        type(context.error),
        context.error,
        context.error.__traceback__,
    )

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please check the command format."
        )


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    quotes = load_quotes(QUOTES_FILE)
    banlu_quotes = load_banlu_quotes(BANLU_QUOTES_FILE)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # shared state
    app.bot_data.setdefault("banlu_last_sent", None)
    app.bot_data.setdefault("holidays_last_sent", None)
    app.bot_data["quotes"] = quotes
    app.bot_data["banlu_quotes"] = banlu_quotes

    private_and_groups = filters.ChatType.PRIVATE | filters.ChatType.GROUPS
    channels = filters.ChatType.CHANNEL

    # commands
    app.add_handler(CommandHandler("chat_id", chat_id_command, filters=private_and_groups | channels))
    app.add_handler(CommandHandler("start", start_command, filters=private_and_groups))
    app.add_handler(CommandHandler("help", help_command, filters=private_and_groups))
    app.add_handler(CommandHandler("quote", quote_command, filters=private_and_groups))

    app.add_handler(CommandHandler("timer", timer_command, filters=private_and_groups))
    app.add_handler(CommandHandler("timerdate", timerdate_command, filters=private_and_groups))

    # ✅ cancel menu + callbacks (из commands/cancel.py)
    app.add_handler(CommandHandler("cancel", cancel_command, filters=private_and_groups))
    app.add_handler(CallbackQueryHandler(cancel_callback, pattern=r"^(cancel_one:|cancel_all:)"))

    app.add_handler(CommandHandler("holidays", holidays_command, filters=private_and_groups))
    app.add_handler(CommandHandler("murloc_ai", murloc_ai_command, filters=private_and_groups))

    # daily jobs
    setup_banlu_daily(app)
    setup_holidays_daily(app)

    app.add_error_handler(error_handler)

    logger.info("Bot started.")
    app.run_polling()


if __name__ == "__main__":
    main()
