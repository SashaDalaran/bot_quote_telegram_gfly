import random
from core.settings import BANLU_WOWHEAD_URL

def load_banlu_quotes(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def get_random_banlu_quote(quotes: list[str]) -> str | None:
    if not quotes:
        return None
    return random.choice(quotes)


def format_banlu_message(quote: str) -> str:
    return (
        "🐉 Бань Лу — спутник Великого Мастера\n\n"
        f"💬 {quote}\n\n"
        f"🔗 Подробнее: {BANLU_WOWHEAD_URL}"
    )
