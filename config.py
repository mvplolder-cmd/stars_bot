import os

# ─── Токены ───────────────────────────────────────────────────────────────────
# Получи токен у @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "8994569220:AAHlH3vTSMiD3H6sT6htUnxUnqEjhIQwtgs")

# Токен провайдера платежей.
# Для TON через @wallet или @CryptoBot — получи у них.
# Если используешь нативные Telegram Stars (XTR) — оставь пустую строку "".
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "594195:AA8t5lFCdyEHCPp3qr5riSRjYjcKbfe9sv4")

# ─── Пакеты звёзд ─────────────────────────────────────────────────────────────
# stars  — количество звёзд Telegram
# ton    — цена в TON (float)
# usd    — примерная цена в USD (для отображения)
# id     — уникальный идентификатор пакета (строка, без пробелов)
STARS_PACKAGES = [
    {"id": "50",   "stars": 50,   "ton": 0.5,  "usd": "1.0"},
    {"id": "100",  "stars": 100,  "ton": 0.9,  "usd": "1.8"},
    {"id": "250",  "stars": 250,  "ton": 2.1,  "usd": "4.2"},
    {"id": "500",  "stars": 500,  "ton": 4.0,  "usd": "8.0"},
    {"id": "1000", "stars": 1000, "ton": 7.5,  "usd": "15"},
    {"id": "2500", "stars": 2500, "ton": 17.5, "usd": "35"},
]
