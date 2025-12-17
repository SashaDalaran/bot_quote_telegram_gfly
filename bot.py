# ==================================================
# bot.py — Telegram Bot Entry Point
# ==================================================
#
# This file is the main entry point of the Telegram bot.
#
# Responsibilities:
# - Initialize the Telegram application
# - Load configuration and persistent data
# - Register command and message handlers
# - Configure scheduled (daily) background jobs
# - Start the polling loop
#
# IMPORTANT:
# This file MUST NOT contain business logic.
# All logic must live in:
#   - core/        → generic bot mechanics (timers, models, helpers)
#   - services/    → domain-specific logic (quotes, holidays, banlu)
#   - commands/    → user-facing command handlers
#
# ==================================================

# ================== standard library ==================

import logging
import traceback

# ================== telegram framework ==================

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# ================== settings ==================
#
# Global configuration values.
# Loaded from environment variables or config files.
#
# TELEGRAM_BOT_TOKEN → Telegram bot authentication token
# QUOTES_FILE        → path to quotes storage
# BANLU_QUOTES_FILE  → path to Banlu quotes storage
#

from core.settings import (
    TELEGRAM_BOT_TOKEN,
    QUOTES_FILE,
    BANLU_QUOTES_FILE,
)

# ================== services ==================
#
# Services encapsulate domain-specific logic.
# They load, prepare and validate data used by the bot.
#

from services.quotes_service import load_quotes
from services.banlu_service import load_banlu_quotes

# ================== commands ==================
#
# Command handlers:
# - parse user input
# - call core/services logic
# - send formatted responses back to Telegram
#

from commands.chat_id import chat_id_command

from commands.start import start_command
from commands.help_cmd import help_command
from commands.quotes import quote_command

from commands.simple_timer import timer_command
from commands.date_timer import timerdate_command
from commands.cancel import cancel_command, cancel_all_command

from commands.holidays_cmd import holidays_command
from commands.murloc_ai import murloc_ai_command

# ================== daily jobs setup ==================
#
# Background scheduled tasks registered at startup.
#

from daily.banlu.banlu_daily import setup_banlu_daily
from daily.holidays.holidays_daily import setup_holidays_daily

# ================== logging ==================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ================== global error handler ==================
#
# Catches all unhandled exceptions raised during updates.
# Logs full traceback and sends a user-friendly message.
#

async def error_handler(update, context):
    traceback.print_exception(
        type(context.error),
        context.error,
        context.error.__traceback__,
    )

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please check the command format."
        )

# ================== main application entry ==================
#
# Initializes the bot, registers handlers,
# configures daily jobs and starts polling.
#

def main() -> None:

    # ---------- sanity check ----------
    #
    # Bot cannot start without a valid token.
    #
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    # ---------- load persistent data ----------
    #
    # Data is loaded once at startup and stored in bot_data.
    #
    quotes = load_quotes(QUOTES_FILE)
    banlu_quotes = load_banlu_quotes(BANLU_QUOTES_FILE)

    # ---------- build application ----------
    #
    # Creates the Telegram bot application instance.
    #
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # ================== shared application state ==================
    #
    # bot_data stores global persistent state
    # accessible from handlers and scheduled jobs.
    #
    app.bot_data.setdefault("banlu_last_sent", None)
    app.bot_data.setdefault("holidays_last_sent", None)
    app.bot_data["quotes"] = quotes
    app.bot_data["banlu_quotes"] = banlu_quotes

    # ---------- chat filters ----------
    #
    # Limit commands to specific chat types.
    #
    private_and_groups = filters.ChatType.PRIVATE | filters.ChatType.GROUPS
    channels = filters.ChatType.CHANNEL

    # ================== command handlers ==================

    app.add_handler(
        CommandHandler(
            "chat_id",
            chat_id_command,
            filters=private_and_groups | filters.ChatType.CHANNEL,
        )
    )

    app.add_handler(CommandHandler("start", start_command, filters=private_and_groups))
    app.add_handler(CommandHandler("help", help_command, filters=private_and_groups))
    app.add_handler(CommandHandler("quote", quote_command, filters=private_and_groups))

    app.add_handler(CommandHandler("timer", timer_command, filters=private_and_groups))
    app.add_handler(
        CommandHandler("timerdate", timerdate_command, filters=private_and_groups)
    )

    app.add_handler(CommandHandler("cancel", cancel_command, filters=private_and_groups))
    app.add_handler(
        CommandHandler("cancelall", cancel_all_command, filters=private_and_groups)
    )

    app.add_handler(
        CommandHandler("holidays", holidays_command, filters=private_and_groups)
    )
    app.add_handler(
        CommandHandler("murloc_ai", murloc_ai_command, filters=private_and_groups)
    )

    # ---------- channel commands ----------
    #
    # Allow /start and /help inside channels.
    #
    app.add_handler(
        MessageHandler(channels & filters.Regex(r"^/start"), start_command)
    )
    app.add_handler(
        MessageHandler(channels & filters.Regex(r"^/help"), help_command)
    )

    # ---------- error handler ----------
    app.add_error_handler(error_handler)

    # ================== scheduled daily jobs ==================

    setup_banlu_daily(app)
    setup_holidays_daily(app)

    # ---------- start bot ----------
    logger.info("🚀 Telegram bot started")
    app.run_polling()

# ================== script entry ==================
#
# Allows running the bot via:
#   python bot.py
#

if __name__ == "__main__":
    main()