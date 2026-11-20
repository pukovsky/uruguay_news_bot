import trafilatura
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def extract_article(url: str, timeout: int = 15) -> dict:
    """
    Скачивает страницу и извлекает основной текст.
    Возвращает dict: {'url', 'text', 'error'}.
    """
    result = {"url": url, "text": None, "error": None}

    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'

        text = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
            deduplicate=True,
        )

        if not text or len(text.strip()) < 200:
            result["error"] = "текст не извлечён или слишком короткий"
            return result

        result["text"] = text.strip()
        return result

    except requests.exceptions.Timeout:
        result["error"] = "таймаут"
    except requests.exceptions.HTTPError as e:
        result["error"] = f"HTTP {e.response.status_code}"
    except Exception as e:
        result["error"] = str(e)

    return result


def enrich_with_text(news: list) -> list:
    """Для каждой новости добавляет поле 'full_text' (или None)."""
    enriched = []
    for i, item in enumerate(news, 1):
        print(f"[{i}/{len(news)}] {item['title'][:60]}...")
        extracted = extract_article(item["link"])
        item = {**item, "full_text": extracted["text"], "extract_error": extracted["error"]}
        if extracted["text"]:
            print(f"   ✅ {len(extracted['text'])} символов")
        else:
            print(f"   ❌ {extracted['error']}")
        enriched.append(item)
    return enriched