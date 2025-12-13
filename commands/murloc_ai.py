# ==================================================
# commands/murloc_ai.py — Telegram Murloc AI Command
# ==================================================

import random
from telegram import Update
from telegram.ext import ContextTypes

from core.helpers import load_lines


# ===========================
# Data files
# ===========================
MURLOC_STARTS_FILE = "data/murloc_starts.txt"
MURLOC_MIDDLES_FILE = "data/murloc_middles.txt"
MURLOC_ENDINGS_FILE = "data/murloc_endings.txt"


# ===========================
# Phrase generator
# ===========================
def generate_murloc_phrase(starts, middles, ends) -> str:
    if not (starts and middles and ends):
        return "❌ Murloc AI wisdom database is missing."

    a = random.choice(starts)
    b = random.choice(middles)
    c = random.choice(ends)

    return f"🐸 *Murloc AI Wisdom*\n\n{a} — {b}, {c}\n\n_Mrrglglglgl!_"


# ===========================
# /murloc_ai command
# ===========================
async def murloc_ai_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    # Lazy-load or reuse cached data
    if "murloc_data" not in context.bot_data:
        context.bot_data["murloc_data"] = {
            "starts": load_lines(MURLOC_STARTS_FILE),
            "middles": load_lines(MURLOC_MIDDLES_FILE),
            "ends": load_lines(MURLOC_ENDINGS_FILE),
        }

    data = context.bot_data["murloc_data"]

    phrase = generate_murloc_phrase(
        data["starts"],
        data["middles"],
        data["ends"],
    )

    await update.message.reply_text(
        phrase,
        parse_mode="Markdown",
    )
