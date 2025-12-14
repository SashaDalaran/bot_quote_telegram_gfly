# ==================================================
# bot.py — Telegram Bot Entry Point
# ==================================================

import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# ================== settings ==================

from core.settings import (
    TELEGRAM_BOT_TOKEN,
    QUOTES_FILE,
    BANLU_QUOTES_FILE,
)

# ================== services ==================

from services.quotes_service import load_quotes
from services.banlu_service import load_banlu_quotes

# ================== commands ==================
from commands.chat_id import chat_id_command

from commands.start import start_command
from commands.help_cmd import help_command
from commands.quotes import quote_command

from commands.simple_timer import timer_command
from commands.date_timer import timerdate_command
from commands.cancel import cancel_command

from commands.holidays_cmd import holidays_command
from commands.murloc_ai import murloc_ai_command

# ================== daily setup ==================

from daily.banlu.banlu_daily import setup_banlu_daily
from daily.holidays.holidays_daily import setup_holidays_daily

# ================== logging ==================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    # ---------- load data ----------
    quotes = load_quotes(QUOTES_FILE)
    banlu_quotes = load_banlu_quotes(BANLU_QUOTES_FILE)

    # ---------- app ----------
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.bot_data["quotes"] = quotes
    app.bot_data["banlu_quotes"] = banlu_quotes

    # ---------- filters ----------
    private_and_groups = filters.ChatType.PRIVATE | filters.ChatType.GROUPS
    channels = filters.ChatType.CHANNEL

    # ---------- commands ----------
    app.add_handler(CommandHandler("chat_id", chat_id_command, filters=private_and_groups | filters.ChatType.CHANNEL))

    app.add_handler(CommandHandler("start", start_command, filters=private_and_groups))
    app.add_handler(CommandHandler("help", help_command, filters=private_and_groups))
    app.add_handler(CommandHandler("quote", quote_command, filters=private_and_groups))

    app.add_handler(CommandHandler("timer", timer_command, filters=private_and_groups))
    app.add_handler(CommandHandler("timerdate", timerdate_command, filters=private_and_groups))
    app.add_handler(CommandHandler("cancel", cancel_command, filters=private_and_groups))

    app.add_handler(CommandHandler("holidays", holidays_command, filters=private_and_groups))
    app.add_handler(CommandHandler("murloc_ai", murloc_ai_command, filters=private_and_groups))

    app.add_handler(MessageHandler(channels & filters.Regex(r"^/start"), start_command))
    app.add_handler(MessageHandler(channels & filters.Regex(r"^/help"), help_command))

    # ---------- daily jobs ----------
    setup_banlu_daily(app)
    setup_holidays_daily(app)

    logger.info("🚀 Telegram bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
