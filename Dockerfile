# ==================================================
# Dockerfile — Production Build for Telegram Bot
# ==================================================
#
# This Dockerfile builds a lightweight, production-ready
# Docker image for the Telegram bot.
#
# Key goals:
# - Small image size
# - Fast startup
# - Reproducible builds
# - Secure runtime environment
#
# Python version: 3.11
# Target platform: Fly.io (Linux)
#
# ==================================================

# ==================================================
# Stage 1: Build dependencies
# ==================================================
#
# This stage installs all Python dependencies
# into a temporary directory to keep the final
# image clean and minimal.
#

FROM python:3.11-slim AS builder

# Disable .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build tools required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Working directory for dependency installation
WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies into a separate directory
RUN pip install --upgrade pip setuptools wheel \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt \
 && rm -rf /root/.cache/pip

# ==================================================
# Stage 2: Runtime image
# ==================================================
#
# Final minimal image containing only:
# - Python runtime
# - Installed dependencies
# - Application source code
#

FROM python:3.11-slim

# Runtime environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Optional micro-optimization:
# Remove unused Python test files to reduce image size
RUN rm -rf /usr/local/lib/python3.11/test \
 && rm -rf /usr/local/lib/python3.11/distutils/tests \
 && rm -rf /usr/local/lib/python3.11/unittest/test

# Create a non-root user for security
RUN useradd -m bot

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Set ownership to non-root user
RUN chown -R bot:bot /app

# Switch to non-root user
USER bot

# ==================================================
# Application startup
# ==================================================
#
# Start the Telegram bot using bot.py
#

CMD ["python", "bot.py"]
