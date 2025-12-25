# ==================================================
# services/__init__.py — Services Package
# ==================================================
#
# Package marker for service-layer modules.
#
# Layer: Services
#
# Responsibilities:
# - Encapsulate domain logic and data access
# - Keep formatting rules consistent across commands and daily jobs
# - Provide stable functions consumed by commands/daily scripts
#
# Boundaries:
# - Services may use core utilities, but should avoid importing command modules.
# - Services should not perform Telegram network calls directly (commands/daily own messaging).
#
# ==================================================
