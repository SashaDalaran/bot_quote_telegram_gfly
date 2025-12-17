# ==================================================
# core/helpers.py — Generic Helper Utilities
# ==================================================
#
# This module contains small, reusable helper
# functions used across the project.
#
# Responsibilities:
# - Provide simple, generic utilities
# - Avoid duplication of common patterns
#
# IMPORTANT:
# - Functions here must remain generic
# - No Telegram-specific logic
# - No domain-specific business rules
#
# ==================================================

# ==================================================
# File helpers
# ==================================================
#
# Loads non-empty lines from a UTF-8 encoded text file.
#
# Behavior:
# - Strips whitespace from each line
# - Ignores empty lines
# - Fails gracefully if the file does not exist
#
# Returns:
# - list[str] containing cleaned lines
# - empty list if file is missing
#
def load_lines(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # Missing file is not treated as an error
        return []
