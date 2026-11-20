import feedparser
import requests
from datetime import datetime, timedelta
from categories import category_decision
from filter import is_relevant

SOURCES = {
    "El País": "https://www.elpais.com.uy/rss/latest",
   # "Montevideo": "http://www.montevideo.com.uy/anxml.aspx?59",
    "La Diaria": "https://ladiaria.com.uy/feeds/articulos/"
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_news(hours=24):
    """Собирает новости за последние N часов из всех источников."""
    cutoff = datetime.now() - timedelta(hours=hours)
    all_news = []

    for source_name, url in SOURCES.items():
        print(f"Читаю {source_name}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'

            feed = feedparser.parse(response.text)

            for entry in feed.entries:

                decision = category_decision(entry)

                if decision == "block":
                    continue

                if decision == "unknown":
                    if not is_relevant(entry.get("title", "")):
                        continue


                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                if published and published >= cutoff:
                    all_news.append({
                        "source": source_name,
                        "title": entry.get("title", "").strip(),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", "").strip(),
                        "published": published.isoformat(),
                    })

            print(f"  ✅ {source_name}: {len(feed.entries)} всего, "
                  f"{len([n for n in all_news if n['source'] == source_name])} за сутки")

        except Exception as e:
            print(f"  ❌ {source_name}: ошибка — {e}")

    return all_news


if __name__ == "__main__":
    news = fetch_news()
    print(f"\nВсего свежих новостей: {len(news)}")
    for n in news[:25]:
        print(f"- [{n['source']}] {n['title']}")