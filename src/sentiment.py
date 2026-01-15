import feedparser
from textblob import TextBlob

def fetch_news(symbol: str, max_items=8):
    url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)

    news = []
    for entry in feed.entries[:max_items]:
        news.append({
            "title": entry.title,
            "link": entry.link,
            "published": getattr(entry, "published", "")
        })
    return news

def sentiment_score(text: str) -> float:
    return float(TextBlob(text).sentiment.polarity)

def analyze_news_sentiment(symbol: str):
    news_items = fetch_news(symbol)
    if not news_items:
        return 0.0, []

    scores = []
    for item in news_items:
        s = sentiment_score(item["title"])
        item["sentiment"] = s
        scores.append(s)

    avg = sum(scores) / len(scores)
    return avg, news_items
