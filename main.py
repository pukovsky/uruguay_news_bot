from fetcher import fetch_news
from extractor import enrich_with_text
from summarizer import summarize, deduplicate_summaries
from publisher import publish_digest
import time

def main():
    news = fetch_news(hours=24)

    news = news[:20]
    print(f"Обрабатываю {len(news)} новостей")

    enriched = enrich_with_text(news)

    summaries = []
    for i, article in enumerate(enriched, 1):
        if not article.get("full_text"):
            continue
        result = summarize(article["full_text"], article["title"])
        if result is None or not result.get("is_news", True):
            continue
        if result.get("importance", 0) < 3:
            print(f"  пропуск: низкая важность ({result.get('importance')})")
            continue
        summaries.append({**article, "summary": result})
        print(f"[{i}/{len(enriched)}] ✅ {result['title_ru']}")
        time.sleep(15)


    if summaries:
         summaries = deduplicate_summaries(summaries)
         publish_digest(summaries)
    else:
         print("После фильтрации не осталось новостей")

if __name__ == "__main__":
    main()