import os
import time
import requests
from datetime import datetime

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL_ID"]

TELEGRAM_LIMIT = 4096
SAFE_LIMIT = 3900


from datetime import datetime

TAG_ORDER = [
    "Политика",
    "Экономика и технологии",
    "Общество",
    "Безопасность и правопорядок",
    "Суды и законодательство",
    "Образование",
    "Экология",
    "Международные отношения",
]

EMOJI_MAP = {
    "Политика": "🏛️",
    "Экономика и технологии": "💻",
    "Общество": "👥",
    "Безопасность и правопорядок": "🚔",
    "Суды и законодательство": "⚖️",
    "Образование": "🎓",
    "Здоровье": "🏥",
    "Экология": "🌱",
    "Международные отношения": "🌍",
}


def format_digest(digest: list, date_str: str | None = None) -> str:
    """Собирает HTML-пост, группируя новости по тегам в заданном порядке."""
    if date_str is None:
        date_str = datetime.now().strftime("%d.%m.%Y")

    lines = [f"🇺🇾 <b>Уругвай: {date_str}</b>\n"]

    # Группируем по первой метке
    grouped: dict[str, list] = {}
    for item in digest:
        tags = item.get("tags") or ["Общество"]
        tag = tags[0]
        grouped.setdefault(tag, []).append(item)

    def render_block(tag: str, items: list) -> list[str]:
        emoji = EMOJI_MAP.get(tag, "📌")
        block = [f"\n{emoji} <b>{tag}</b>\n"]
        for item in items:
            block.append(f"<b>{item['title_ru']}</b>\n")
            block.append(f"{item['summary_ru']}\n")
            block.append(f"<a href='{item['link']}'>{item['source']}</a>\n")
        return block

    # Сначала рубрики в заданном порядке
    for tag in TAG_ORDER:
        if tag in grouped:
            lines.extend(render_block(tag, grouped[tag]))

    # Потом всё, что не попало в TAG_ORDER (на случай новых меток)
    for tag, items in grouped.items():
        if tag not in TAG_ORDER:
            lines.extend(render_block(tag, items))

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


def save_fallback_digest(text: str, filename: str = "unsent_digest.txt") -> None:
    """Сохраняет дайджест на диск, если отправка в Telegram не удалась."""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n=== {datetime.now().isoformat()} ===\n{text}\n")
    print(f"💾 Дайджест сохранён в {filename}")


def send_message_with_retry(
    text: str,
    retries: int = 4,
    timeout: int = 15,
) -> bool:
    """Отправляет одну часть через ваш send_message или напрямую в Telegram API с ретраями."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    for attempt in range(retries):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)

            if resp.status_code in (429, 500, 502, 503, 504):
                retry_after = resp.json().get("parameters", {}).get("retry_after")
                wait = int(retry_after) if retry_after else (2 ** attempt) * 2
                print(f"   ⚠️ Telegram {resp.status_code}, жду {wait}с (попытка {attempt + 1}/{retries})...")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            wait = (2 ** attempt) * 2  # 2с, 4с, 8с, 16с
            print(f"   ⚠️ Сетевая ошибка: {e}")
            if attempt < retries - 1:
                print(f"   Повтор через {wait}с (попытка {attempt + 1}/{retries})...")
                time.sleep(wait)

    return False


def publish_digest(summaries: list, date_str: str | None = None) -> bool:
    text = format_digest(summaries, date_str)
    parts = split_message(text)

    print(
        f"Дайджест: {len(summaries)} новостей, {len(text)} символов, "
        f"{len(parts)} сообщений"
    )

    for i, part in enumerate(parts, 1):
        print(f"  Отправляю часть {i}/{len(parts)} ({len(part)} символов)...")
        if not send_message_with_retry(part):
            print(f"  ❌ Часть {i} не отправлена")
            save_fallback_digest("\n\n".join(parts[i - 1 :]))
            return False
        if i < len(parts):
            time.sleep(2)

    print(" Дайджест опубликован")
    return True