import feedparser
import requests
from collections import defaultdict
from urllib.parse import urlparse

SOURCES = {
    "El País": "https://www.elpais.com.uy/rss/latest",
    "Montevideo": "http://www.montevideo.com.uy/anxml.aspx?59",
    "La Diaria": "https://ladiaria.com.uy/feeds/articulos/",
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_url_section(link: str) -> str:
    """Извлекает секцию из URL La Diaria: /politica/articulo/... -> 'politica'."""
    path = urlparse(link).path.strip("/")
    parts = path.split("/")
    # Первая часть пути — обычно секция (politica, deporte, cultura...)
    return parts[0] if parts else ""


def inspect():
    for source_name, url in SOURCES.items():
        print(f"\n{'=' * 70}")
        print(f"ИСТОЧНИК: {source_name}")
        print(f"{'=' * 70}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            feed = feedparser.parse(response.text)

            if not feed.entries:
                print("  ⚠️ записей нет")
                continue

            # Счётчики: сколько раз встречается каждая категория/секция
            tag_counter = defaultdict(int)
            section_counter = defaultdict(int)

            for entry in feed.entries:
                title = entry.get("title", "").strip()[:60]
                link = entry.get("link", "")
                tags = [t.get("term", "") for t in entry.get("tags", [])]
                section = get_url_section(link)

                for t in tags:
                    tag_counter[t] += 1
                if section:
                    section_counter[section] += 1

                print(f"\n  {title}...")
                print(f"    tags:    {tags if tags else '—'}")
                print(f"    section: {section or '—'}")

            # Итоговая статистика
            print(f"\n  {'-' * 60}")
            print(f"  СТАТИСТИКА ПО ТЕГАМ ({len(tag_counter)} уникальных):")
            for tag, count in sorted(tag_counter.items(), key=lambda x: -x[1]):
                print(f"    {count:3d}  {tag}")

            print(f"\n  СТАТИСТИКА ПО СЕКЦИЯМ URL ({len(section_counter)} уникальных):")
            for sec, count in sorted(section_counter.items(), key=lambda x: -x[1]):
                print(f"    {count:3d}  {sec}")

        except Exception as e:
            print(f"  ❌ Ошибка: {e}")


if __name__ == "__main__":
    inspect()