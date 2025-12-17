# ==================================================
# Dockerfile — Production Build for Telegram Bot
# ==================================================
#
# This Dockerfile builds a lightweight, production-ready
# image for the Telegram bot.
#
# Design goals:
# - Minimal final image size
# - Fast startup time
# - Reproducible builds
# - Secure, non-root runtime
#
# Python version:
# - 3.11
#
# Target platform:
# - Linux (Fly.io Machines)
#
# ==================================================


# ==================================================
# Stage 1 — Build Dependencies
# ==================================================
#
# This stage installs all Python dependencies
# into a temporary directory.
#
# Rationale:
# - Keeps build tools out of the final image
# - Reduces attack surface
# - Allows aggressive cleanup in runtime stage
#
FROM python:3.11-slim AS builder

# --------------------------------------------------
# Python runtime configuration
# --------------------------------------------------
#
# PYTHONDONTWRITEBYTECODE:
#   Prevent creation of .pyc files
#
# PYTHONUNBUFFERED:
#   Ensures immediate log flushing
#
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --------------------------------------------------
# System build dependencies
# --------------------------------------------------
#
# build-essential + gcc:
#   Required for compiling native Python extensions
#
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
 && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# Application workspace
# --------------------------------------------------
WORKDIR /app

# --------------------------------------------------
# Dependency installation
# --------------------------------------------------
#
# Copy only requirements.txt first to maximize
# Docker layer caching.
#
COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ==================================================
# Stage 2 — Runtime Image
# ==================================================
#
# Final production image containing ONLY:
# - Python runtime
# - Installed dependencies
# - Application source code
#
# No compilers, no build tools, no package caches.
#
FROM python:3.11-slim

# --------------------------------------------------
# Runtime environment configuration
# --------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --------------------------------------------------
# Aggressive Python cleanup
# --------------------------------------------------
#
# Remove unused standard library components
# to minimize image size.
#
# This has NO impact on runtime behavior
# of the application.
#
RUN rm -rf \
    /usr/local/lib/python3.11/test \
    /usr/local/lib/python3.11/distutils/tests \
    /usr/local/lib/python3.11/unittest/test \
    /usr/local/lib/python3.11/idlelib

# --------------------------------------------------
# Non-root runtime user
# --------------------------------------------------
#
# Running as non-root is a production best practice.
#
RUN useradd -m bot

# --------------------------------------------------
# Application workspace
# --------------------------------------------------
WORKDIR /app

# --------------------------------------------------
# Copy dependencies from build stage
# --------------------------------------------------
COPY --from=builder /install /usr/local

# --------------------------------------------------
# Copy application source code
# --------------------------------------------------
COPY --chown=bot:bot . .

# --------------------------------------------------
# Switch to non-root user
# --------------------------------------------------
USER bot

# ==================================================
# Application entrypoint
# ==================================================
#
# Start the Telegram bot.
#
CMD ["python", "bot.py"]
