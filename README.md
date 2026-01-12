<p align="center">
  <img src="Murloc-Fulltime-Logo.gif" width="220" alt="Murloc Bot Logo" />
</p>

<h1 align="center">bot_quote_telegram_gfly</h1>

<p align="center">
  A production Telegram bot built with <b>Python 3.11</b> and <b>python-telegram-bot 21.7</b>.<br/>
  Clean layered architecture (Commands → Services → Core) + scheduled daily posts via PTB <b>JobQueue</b> (APScheduler).
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/python--telegram--bot-21.7-7289DA?style=for-the-badge&logo=telegram" />
  <img src="https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/Fly.io-Machines-8A2BE2?style=for-the-badge" />
</p>

---

## ✨ Overview

**bot_quote_telegram_gfly** is a modular Telegram bot that combines:

- 💬 entertainment features (random quotes)
- 🐸 Murloc AI “wisdom generator” (phrases built from datasets)
- ⏱ timers (relative and absolute date/time)
- 🎉 holidays system (static JSON + dynamic rules)
- 📡 daily automated posts (Ban’Lu / Holidays / Birthday & Guild Events)

This project is intentionally structured as a **reference-quality architecture** bot:
clean layers, predictable behavior, easy extensibility, and production-friendly deployment.

---

## 📌 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Commands](#-commands)
  - [/start & /help](#start--help)
  - [Quotes](#quotes)
  - [Murloc AI](#murloc-ai)
  - [Timers](#timers)
  - [Holidays](#holidays)
  - [Admin: /cancel](#admin-cancel)
  - [/chat_id](#chat_id)
- [Daily Jobs](#-daily-jobs)
- [Datasets & Content](#-datasets--content)
- [Environment Variables](#-environment-variables)
- [Deployment (Fly.io)](#-deployment-flyio)
- [Logging & Security Notes](#-logging--security-notes)
- [Troubleshooting](#-troubleshooting)
- [Known Limitations](#-known-limitations)
- [Roadmap (safe improvements)](#-roadmap-safe-improvements)

---

## 🚀 Features

### ✅ Commands / user features

- 💬 **Random Quotes** — `/quote`
- 🐸 **Murloc AI** — `/murloc_ai`
- ⏱ **Countdown Timers**
  - `/timer` — relative (e.g. `10m`, `1h30m`)
  - `/timerdate` — absolute date/time with optional timezone offset
  - optional `--pin` flag (pins timer message if bot has permission)
  - timers update a single message (edit), no spam
- 🎉 **Holiday System** — `/holidays`
  - static holidays from JSON packs in `data/holidays/`
  - dynamic holidays from rules in `core/dynamic_holidays.py`
  - emoji/flag mapping in `services/holidays_flags.py`
- 🧹 **Admin timer management** — `/cancel`
  - cancel one timer or cancel all (via buttons)
- 🆔 **Utility** — `/chat_id`
  - prints chat/channel ID (useful for configuring channels via env vars)

### ✅ Production / deployment

- 🐳 Docker multi-stage build
- non-root runtime (safer container execution)
- Fly.io Machines ready (`fly.toml`)

---

## 🧠 Architecture

The bot follows a strict layered architecture:

```
Commands → Services → Core
```

### Commands (`commands/`)
User-facing Telegram handlers:
- read `Update` / `Context`
- parse input and flags
- call the domain services / core
- send/edit messages, build inline keyboards

### Services (`services/`)
Domain layer:
- data loading (datasets / holidays)
- Telegram-friendly formatting (HTML / text)
- orchestration helpers (what to send, where to send)
- parsing helpers for `/timer` and `/timerdate`
- channel ID parsing from environment variables

### Core (`core/`)
Core engine + infrastructure:
- timer scheduling wrapper + job store integration
- timer store helpers (add/list/remove)
- formatting helpers (human-readable countdown)
- admin checks and safety utilities
- dynamic holidays rules
- shared models

### Daily jobs (`daily/`)
Cron-like scheduled tasks wired via PTB JobQueue (APScheduler).

---

## 📁 Project Structure

> This is the **actual** folder layout in the repo.

```
bot_quote_telegram_gfly/
│
├── bot.py                        # Application entrypoint
│
├── commands/                   # Telegram commands (user-facing layer)
│   ├── __init__.py                 # package marker
│   ├── cancel.py                   # /cancel (admin)
│   ├── chat_id.py                  # /chat_id
│   ├── date_timer.py               # /timerdate (absolute)
│   ├── help_cmd.py                 # /help
│   ├── holidays_cmd.py             # /holidays
│   ├── murloc_ai.py                # /murloc_ai
│   ├── quotes.py                   # /quote
│   ├── simple_timer.py             # /timer (relative)
│   └── start.py                    # /start
│
├── services/                   # Service layer (formatting, data loading, parsing)
│   ├── __init__.py                 # package marker
│   ├── banlu_services/timer_service.py            # load Ban'Lu quotes from data/quotersbanlu.txt
│   ├── birthday_format.py          # Telegram-friendly formatting for guild events
│   ├── birthday_services/timer_service.py         # load birthday/challenge/hero events (data/birthday.json)
│   ├── channel_ids.py              # parse comma-separated channel IDs from env
│   ├── holidays_flags.py           # emoji/flag/category mapping
│   ├── holidays_format.py          # format holidays output
│   ├── holidays_services/timer_service.py         # merge static + dynamic holidays
│   ├── parser.py                   # duration & datetime parsing for timers
│   ├── quotes_services/timer_service.py           # load quotes from data/quotes.txt
│   └── timer_services/timer_service.py            # legacy wrapper (kept for compatibility)
│
├── core/                       # Core logic (timers, models, helpers)
│   ├── __init__.py                 # package marker
│   ├── admin.py                    # admin checks for /cancel
│   ├── countdown.py                # countdown tick / message editing logic
│   ├── dynamic_holidays.py         # dynamic holiday rules (e.g., Easter)
│   ├── formatter.py                # time/remaining formatting helpers
│   ├── helpers.py                  # misc helpers
│   ├── models.py                   # dataclasses (TimerEntry, etc.)
│   ├── parser.py                   # date parsing utilities (shared)
│   ├── settings.py                 # env + constants (token, file paths, timezone)
│   ├── timers.py                   # create/remove timers (JobQueue)
│   └── timers_store.py             # in-memory timer store per chat
│
├── daily/                       # Scheduled jobs (JobQueue)
│   ├── banlu/
│   │   ├── __init__.py           # package marker
│   │   └── banlu_daily.py        # Ban'Lu daily quote (10:00 GMT+3)
│   ├── birthday/
│   │   ├── __init__.py           # package marker
│   │   └── birthday_daily.py     # Birthday / guild events (10:07 UTC)
│   └── holidays/
│       ├── __init__.py           # package marker
│       └── holidays_daily.py     # Holidays broadcast (10:01 GMT+3)
│
├── data/                        # Content & datasets
│   ├── holidays/                  # holiday JSON packs
│   │   └── December.json
│   │   └── January.json
|   |   └── February.json
│   ├── __init__.py             # package marker
│   ├── birthday.json           # guild events dataset
│   ├── murloc_endings.txt      # Murloc AI dataset
│   ├── murloc_middles.txt      # Murloc AI dataset
│   ├── murloc_starts.txt       # Murloc AI dataset
│   ├── quotersbanlu.txt        # Ban'Lu quotes dataset
│   └── quotes.txt              # quotes dataset
│
├── Dockerfile
│
├── fly.toml
│
├── requirements.txt
│
├── Murloc-Fulltime-Logo.gif
│
├── .python-version
│
├── .dockerignore
│
├── .gitignore
```

---

## ⚡ Quick Start

### 1) Install deps (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Set environment variables

```bash
export TELEGRAM_BOT_TOKEN="xxx"
# optional channels:
export BANLU_CHANNEL_ID="-100123"
export HOLIDAYS_CHANNEL_ID="-100123,-100456"
export BIRTHDAY_CHANNEL_ID="-100123"
```

### 3) Run bot

```bash
python bot.py
```

Bot runs in polling mode (`app.run_polling()`).

---

## 🎮 Commands

### /start & /help

```text
/start   — greeting
/help    — help menu
```

> `/help` is HTML-formatted and shows the supported commands.

---

### Quotes

```text
/quote
```

Returns one random line from `data/quotes.txt`.

---

### Murloc AI

```text
/murloc_ai
```

Generates a phrase by combining random fragments from:

- `data/murloc_starts.txt`
- `data/murloc_middles.txt`
- `data/murloc_endings.txt`

---

## Timers

Timers are designed to be **chat-friendly**:

- the bot sends one “Timer started…” message
- the bot updates that same message over time (edit)
- a **Cancel** button is attached
- optional `--pin` pins the timer message

### /timer — relative timer

**Format**
```text
/timer <duration> [message...]
/timer <duration> --pin [message...]
```

**Supported duration units**
- `d, day, days`
- `h, hr, hour, hours`
- `m, min, mins, minute, minutes`
- `s, sec, secs, second, seconds`

**Examples**
```text
/timer 10s Tea
/timer 5m
/timer 1h30m Boss pull
/timer 10m --pin Tea time
```

**Important note (matches current implementation)**
- The `<duration>` part is parsed as **one token** (the 2nd token of the command).
  - ✅ `/timer 1h30m stretch`
  - ❌ `/timer 1h 30m stretch` (here only `1h` will be parsed as duration)

If you want to support spaced durations later, see [Roadmap](#-roadmap-safe-improvements).

---

### /timerdate — date/time timer

**Format**
```text
/timerdate <date> <time> [TZ] [message...]
/timerdate <date> <time> [TZ] --pin [message...]
```

**Supported date formats**
- `YYYY-MM-DD` (e.g. `2025-12-31`)
- `DD.MM.YYYY` (e.g. `31.12.2025`)

**Supported time formats**
- `HH:MM`
- `HH:MM:SS`

**Optional timezone offset token (TZ)**
- `+3`, `+03`, `+03:00`
- `-5`, `-05`, `-0530`
- etc.

**Default behavior**
- If TZ is omitted, the bot assumes **Asia/Dubai (UTC+4)** for parsing.
- Internally target time is stored/scheduled in **UTC**.

**Examples**
```text
/timerdate 2025-12-31 23:59 New Year!
/timerdate 31.12.2025 23:59 +3 Happy New Year 🎆
/timerdate 31.12.2025 23:59 +04:00 Party --pin
```

---

## Holidays

### /holidays

```text
/holidays
```

Shows upcoming holidays.

Implementation details:
- loads static holidays from `data/holidays/*.json`
- loads dynamic holidays from `core/dynamic_holidays.py`
- renders Telegram-friendly output via `services/holidays_format.py`
- uses emoji mappings from `services/holidays_flags.py`

---

## Admin: /cancel

```text
/cancel
```

Admin-only command:
- checks whether the user is an admin of the chat
- shows active timers
- allows canceling:
  - a specific timer
  - **all** timers in the chat (button action)

> Note: you can remove all chat timers via `/cancel` using the "Cancel all timers" button in the menu.

---

## /chat_id

```text
/chat_id
```

Prints current chat ID — useful for configuring:
- `BANLU_CHANNEL_ID`
- `HOLIDAYS_CHANNEL_ID`
- `BIRTHDAY_CHANNEL_ID`

Works in private chats, groups, and channels.

---

## 🔁 Daily Jobs

Daily jobs are scheduled via PTB JobQueue.

### Schedule (as implemented in code)

| Job | Module | Time | TZ | Env var |
|---|---|---:|---|---|
| Ban’Lu daily quote | `daily/banlu/banlu_daily.py` | 10:00 | GMT+3 | `BANLU_CHANNEL_ID` |
| Holidays broadcast | `daily/holidays/holidays_daily.py` | 10:01 | GMT+3 | `HOLIDAYS_CHANNEL_ID` |
| Birthday / Guild events | `daily/birthday/birthday_daily.py` | 10:07 | UTC | `BIRTHDAY_CHANNEL_ID` |

### Catch-up behavior
Each daily module schedules a small `run_once` job shortly after startup (best effort),
so a restart near the scheduled time doesn’t silently skip the daily post.

---

## 📦 Datasets & Content

### Quotes
- `data/quotes.txt` — one quote per line

### Ban’Lu quotes
- `data/quotersbanlu.txt` — dataset for daily quote posts

### Murloc AI datasets
- `data/murloc_starts.txt`
- `data/murloc_middles.txt`
- `data/murloc_endings.txt`

### Holidays packs
- `data/holidays/*.json` — static holidays
- `core/dynamic_holidays.py` — dynamic rules

---

## 🔐 Environment Variables

### Required

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |

### Optional (one or many, comma-separated)

| Variable | Description |
|---|---|
| `BANLU_CHANNEL_ID` | Channel(s) for Ban’Lu daily |
| `HOLIDAYS_CHANNEL_ID` | Channel(s) for Holidays daily |
| `BIRTHDAY_CHANNEL_ID` | Channel(s) for Birthday/Guild events daily |

**Multi-channel example**
```bash
fly secrets set BANLU_CHANNEL_ID="-100123"
fly secrets set HOLIDAYS_CHANNEL_ID="-100123,-100456"
fly secrets set BIRTHDAY_CHANNEL_ID="-100123"
```

---

## 🐳 Deployment (Fly.io)

### Deploy

```bash
fly deploy
fly logs
```

### Set secrets

```bash
fly secrets set TELEGRAM_BOT_TOKEN="xxx"
fly secrets set HOLIDAYS_CHANNEL_ID="-100123"
```

---

## 🧯 Logging & Security Notes

### ⚠️ Token in logs (important)

Telegram Bot API token is part of the request URL:
`https://api.telegram.org/bot<TOKEN>/method`

If your HTTP client logs full URLs (e.g. `httpx` at INFO),
your token can appear in logs.

**Recommended (safe, no behavior changes):**
Add this after logging setup in `bot.py`:

```py
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
```

### If token was ever posted publicly
- regenerate token via **@BotFather**
- update `fly secrets set TELEGRAM_BOT_TOKEN="..."`

---

## 🛠 Troubleshooting

### Bot starts but commands don’t work
- verify you deployed the correct version
- verify `TELEGRAM_BOT_TOKEN` is set
- check that the bot is not blocked and has permission in the chat
- for pin/unpin actions: bot must be admin (or have pin permission)

### Timers do not pin messages
- pin requires admin rights in the chat/channel
- some channels restrict pin permissions

### Daily jobs don’t post
- verify channel IDs (use `/chat_id`)
- verify env vars `*_CHANNEL_ID`
- check logs for warnings about missing/invalid IDs

### 401 / Unauthorized
- invalid token (revoked or incorrect) → set new token in secrets

---

## 🧩 Known Limitations

These are intentional “current behavior” notes that match the code:

- `/timer` duration parsing uses only the 2nd token:
  - ✅ `/timer 1h30m ...`
  - ❌ `/timer 1h 30m ...` (only `1h` will be parsed)
- `/timerdate` assumes **Asia/Dubai (UTC+4)** if TZ offset is not provided.

---

## 🗺 Roadmap (safe improvements)

Safe improvements = minimal risk, no refactor avalanche:

- [ ] **Disable httpx URL logging** by default (prevents token leaks)
- [ ] Sync README ↔ `/help` output (keep documentation identical to bot menu)
- [ ] Add a tiny “smoke check” script:
  - imports modules
  - validates env vars
  - runs minimal startup checks without contacting Telegram

Bigger UX changes (behavior changes; do later only if you want):
- [ ] Support spaced durations for `/timer` (e.g. `1h 30m`)
- [ ] Unify timezone policy across daily jobs (UTC vs GMT+3 vs Dubai)

---

<p align="center">
  <b>Murloc Edition 🐸 — Mrrglglglgl!</b>
</p>
