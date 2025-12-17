# ==================================================
# commands/murloc_ai.py — Murloc AI Wisdom Command
# ==================================================
#
# This module defines a fun, character-driven command
# that generates randomized "Murloc wisdom" phrases.
#
# Command:
# - /murloc_ai → receive a philosophical message
#                spoken in true murloc style 🐸
#
# Responsibilities:
# - Load phrase fragments from data files
# - Generate a randomized phrase
# - Cache loaded data for performance
#
# IMPORTANT:
# - Phrase data is loaded lazily on first use
# - Loaded data is cached in context.bot_data
# - This module contains no business logic
#
# ==================================================

import random
from telegram import Update
from telegram.ext import ContextTypes

from core.helpers import load_lines

# ==================================================
# Phrase data sources
# ==================================================
#
# These text files contain phrase fragments used
# to construct Murloc AI wisdom.
#
# Each file is expected to contain one phrase
# per line (UTF-8 encoded).
#

MURLOC_STARTS_FILE = "data/murloc_starts.txt"
MURLOC_MIDDLES_FILE = "data/murloc_middles.txt"
MURLOC_ENDINGS_FILE = "data/murloc_endings.txt"

# ==================================================
# Phrase generator
# ==================================================
#
# Combines three randomly selected fragments
# into a single Murloc-style wisdom phrase.
#
def generate_murloc_phrase(
    starts: list[str],
    middles: list[str],
    ends: list[str],
) -> str:

    # Guard against missing or empty data files
    if not (starts and middles and ends):
        return "❌ Murloc AI wisdom database is missing."

    start = random.choice(starts)
    middle = random.choice(middles)
    end = random.choice(ends)

    return (
        "🐸 *Murloc AI Wisdom*\n\n"
        f"{start} — {middle}, {end}\n\n"
        "_Mrrglglglgl!_"
    )

# ==================================================
# /murloc_ai command
# ==================================================
#
# Generates and sends a randomized Murloc AI phrase.
#
# Behavior:
# - Phrase data is loaded only once
# - Subsequent calls reuse cached data
#
async def murloc_ai_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    # --------------------------------------------------
    # Lazy-load phrase data
    # --------------------------------------------------
    #
    # Data is cached in bot_data to avoid
    # repeated file I/O on each command call.
    #
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
