import os
import time
import requests
from datetime import datetime

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL_ID"]

TELEGRAM_LIMIT = 4096
SAFE_LIMIT = 3900


def format_digest(summaries: list, date_str: str | None = None) -> str:
    """Собирает HTML-текст поста из списка саммари."""
    if date_str is None:
        date_str = datetime.now().strftime("%d.%m.%Y")

    lines = [f"🇺🇾 <b>Дайджест новостей Уругвая — {date_str}</b>\n"]

    sorted_news = sorted(
        summaries,
        key=lambda x: x["summary"].get("importance", 0),
        reverse=True,
    )

    for i, item in enumerate(sorted_news, 1):
        s = item["summary"]
        tags = " · ".join(f"#{t}" for t in s.get("tags", []))
        title = s.get("title_ru", "Без заголовка")
        summary = s.get("summary_ru", "")
        link = item.get("link", "")
        source = item.get("source", "")

        block = (
            f"<b>{title}</b>\n"
            f"{summary}\n"
        )
        if link:
            block += f"<a href='{link}'>Источник: {source}</a>\n"

        lines.append(block)

    return "\n".join(lines)


def split_message(text: str, limit: int = SAFE_LIMIT) -> list[str]:
    """
    Разбивает длинный текст на части по границам абзацев,
    чтобы не разрывать HTML-теги посередине.
    """
    if len(text) <= limit:
        return [text]

    parts = []
    current = ""
    for block in text.split("\n\n"):
        if len(current) + len(block) + 2 > limit:
            if current:
                parts.append(current.strip())
            current = block
        else:
            current = (current + "\n\n" + block).strip() if current else block
    if current:
        parts.append(current.strip())
    return parts


def send_message(text: str) -> bool:
    """Отправляет одно сообщение в канал. Возвращает True при успехе."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"❌ Сетевая ошибка: {e}")
        return False

    if response.status_code == 200:
        return True

    if response.status_code == 429:
        retry_after = response.json().get("parameters", {}).get("retry_after", 5)
        print(f"⏳ Telegram просит подождать {retry_after} сек...")
        time.sleep(retry_after)
        return send_message(text)

    print(f"❌ Ошибка Telegram {response.status_code}: {response.text}")
    return False


def publish_digest(summaries: list, date_str: str | None = None) -> bool:
    """Собирает дайджест, разбивает на части и отправляет в канал."""

    text = format_digest(summaries, date_str)
    parts = split_message(text)

    print(f"📝 Дайджест: {len(summaries)} новостей, {len(text)} символов, "
          f"{len(parts)} сообщений")

    for i, part in enumerate(parts, 1):
        print(f"  Отправляю часть {i}/{len(parts)} ({len(part)} символов)...")
        if not send_message(part):
            print(f"  ❌ Часть {i} не отправлена")
            return False
        if i < len(parts):
            time.sleep(2)

    print(" Дайджест опубликован")
    return True