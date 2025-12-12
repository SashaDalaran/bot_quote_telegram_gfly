from telegram import Update
from telegram.ext import ContextTypes
from timers.service import (
    create_timer,
    cancel_all_timers,
    create_repeat,
    cancel_all_repeats,
    list_timers,
    clear_pins,
)
from config.settings import CLEANUP_PASSWORD

async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await create_timer(update, context, context.bot_data["quotes"])

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cancel_all_timers(update, context)

async def repeat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await create_repeat(update, context)

async def cancel_repeat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cancel_all_repeats(update, context)

async def timers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_timers(update, context)

async def clear_pins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = context.args[0] if context.args else ""
    await clear_pins(update, context, password, CLEANUP_PASSWORD)
