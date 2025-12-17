from telegram import Update
from telegram.ext import ContextTypes
from services.timer_service import create_timer


async def timerdate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await create_timer(update, context)
