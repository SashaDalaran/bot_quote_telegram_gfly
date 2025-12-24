<p align="center">
  <img src="Murloc-Fulltime-Logo.gif" width="220" alt="Murloc Bot Logo" />
</p>

<h1 align="center">bot-quote-telegram</h1>

<p align="center">
  A production-ready Telegram bot built with <b>Python 3.11</b>, <b>python-telegram-bot</b>, and <b>Fly.io Machines</b>.<br/>
  Designed with clean architecture, predictable async behavior, and long-term maintainability in mind.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/python--telegram--bot-21.x-7289DA?style=for-the-badge&logo=telegram" />
  <img src="https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/Fly.io-Machines-8A2BE2?style=for-the-badge" />
</p>

---

## ✨ Overview!

**bot-quote-telegram** is a modular Telegram bot that combines:

* entertainment features (quotes, Murloc AI),
* utility tools (timers),
* and automated daily content (holidays, Ban’Lu quotes).

The project was built as a **reference-quality bot architecture**, not a one-off script.

### Key goals:

* clean separation of responsibilities
* predictable async execution
* minimal runtime state
* easy extensibility
* production-safe deployment

---

## 🚀 Features

* 💬 **Random Quotes**
* 🐸 **Murloc AI Wisdom Generator**
* ⏱ **Countdown Timers**

  * relative (`/timer 10m`)
  * absolute date/time (`/timerdate DD.MM.YYYY HH:MM +TZ`)
* 📅 **Holiday System**

  * static JSON holidays
  * dynamic holidays (e.g. Easter)
* 📡 **Daily Automated Jobs**

  * Ban’Lu quote (10:00 MSK)
  * Holidays broadcast (10:01 MSK)
* 🐳 **Optimized Docker image (~40 MB)**
* ☁️ **Fly.io zero-downtime deployment**

---

## 🧠 Architectural Philosophy

The bot follows a **strict layered architecture**:

```
Commands  →  Services  →  Core
```

### Core

Pure logic and infrastructure:

* no Telegram API
* no formatting
* no user input

### Services

Application/domain logic:

* loading data
* formatting domain messages
* orchestration helpers

### Commands

User-facing layer:

* parse user input
* delegate to services/core
* send replies

This separation allows:

* easy testing
* safe refactoring
* predictable growth

---

## 📁 Project Structure (Actual)

```
bot_quote_telegram/
│
├── bot.py                     # Application entrypoint
│
├── commands/                  # Telegram commands (user-facing)
│   ├── start.py
│   ├── help_cmd.py
│   ├── simple_timer.py
│   ├── date_timer.py
│   ├── cancel.py
│   ├── chat_id.py
│   ├── quotes.py
│   ├── holidays_cmd.py
│   └── murloc_ai.py
│
├── core/                      # Core engine & infrastructure
│   ├── admin.py
│   ├── countdown.py
│   ├── timers.py
│   ├── models.py
│   ├── parser.py
│   ├── formatter.py
│   ├── dynamic_holidays.py
│   ├── helpers.py
│   └── settings.py
│
├── services/                  # Application services
│   ├── quotes_service.py
│   ├── banlu_service.py
│   ├── holidays_service.py
│   ├── holidays_format.py
│   └── holidays_flags.py
│   └── timer_service.py
│
├── daily/                     # Scheduled jobs
│   ├── banlu/
│   │   └── banlu_daily.py
│   └── holidays/
│       └── holidays_daily.py
│
├── data/                      # Content & datasets
│   ├── holidays/              # Holiday JSON files
│   ├── quotes.txt
│   ├── quotersbanlu.txt
│   ├── murloc_starts.txt
│   ├── murloc_middles.txt
│   └── murloc_endings.txt
│
├── Dockerfile
├── fly.toml
├── requirements.txt
├── README.md
└── Murloc-Fulltime-Logo.gif
```

---

## 🎮 Commands

### 💬 Quotes

```
/quote        — random quote
/murloc_ai    — Murloc wisdom 🐸
```

---

### ⏱ Simple Timer

```
/timer 10m
/timer 1h30m Boss pull
```

Supported units: `s`, `m`, `h`, `d`
Plain numbers are interpreted as **minutes**.

---

### 📅 Date Timer

```
/timerdate DD.MM.YYYY HH:MM [+TZ] [text]
```

Example:

```
/timerdate 31.12.2025 23:59 +3 Happy New Year 🎆
```

---

### 🧹 Timer Management (Admin)

```
/cancel        — cancel specific timer
```

Через /cancel также можно удалить **все** таймеры чата кнопкой в меню.

---

### 🎉 Holidays

```
/holidays      — show upcoming holidays
```

Displays:

* one holiday per source
* country flags
* category emojis

---

## 🔁 Daily Scheduled Jobs

### 🕙 Ban’Lu Daily Quote — **10:00 MSK**

* Source: `data/quotersbanlu.txt`
* Posts one quote to the configured channel

### 🕙 Holidays Broadcast — **10:01 MSK**

* Checks all static & dynamic holidays
* Posts today’s holidays
* Executes once on startup if missed

---

## 🔐 Environment Variables

| Variable               | Description                                 |
| ---------------------- | ------------------------------------------- |
| `TELEGRAM_BOT_TOKEN`   | Telegram bot token                          |
| `BANLU_CHANNEL_ID`     | Channel ID(s) for Ban’Lu daily post         |
| `HOLIDAYS_CHANNEL_ID`  | Channel ID(s) for Holidays daily post       |
| `BIRTHDAY_CHANNEL_ID`  | Channel ID(s) for Birthday daily post       |

Notes:
- Each `*_CHANNEL_ID` can contain **one** ID or **many** IDs separated by commas.
  Example: `-100123,-100456`

Example:

```sh
fly secrets set TELEGRAM_BOT_TOKEN=xxx
fly secrets set BANLU_CHANNEL_ID="-100123"
fly secrets set HOLIDAYS_CHANNEL_ID="-100123,-100456"
fly secrets set BIRTHDAY_CHANNEL_ID="-100123"
```

---

## 🐳 Deployment (Fly.io)

```sh
fly deploy
fly logs
```

* multi-stage Docker build
* non-root user
* minimal runtime footprint

---

## 🏁 Final Notes

This project is intentionally **over-engineered for its feature set** —
because it serves as a **reference architecture** for future bots.

<p align="center">
  <b>Murloc Edition 🐸 — Mrrglglglgl!</b>
</p>
