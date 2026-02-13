import os
import requests
from typing import List
from ..core.models import RawTrend
import xml.etree.ElementTree as ET

class NewsIngestion:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")

    def fetch_from_newsapi(self, query: str = "global news") -> List[RawTrend]:
        """Fetch trending news from NewsAPI."""
        if not self.api_key:
            return []

        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={self.api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            trends = []
            for article in data.get("articles", [])[:20]:
                trends.append(RawTrend(
                    title=article["title"],
                    source=article["source"]["name"],
                    url=article["url"],
                    timestamp=article["publishedAt"]
                ))
            return trends
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []

    def fetch_from_rss(self, feed_url: str) -> List[RawTrend]:
        """Fetch news from an RSS feed (e.g., BBC, Reuters)."""
        try:
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            trends = []
            for item in root.findall(".//item")[:10]:
                trends.append(RawTrend(
                    title=item.find("title").text,
                    source="RSS Feed",
                    url=item.find("link").text,
                    timestamp=item.find("pubDate").text if item.find("pubDate") is not None else None
                ))
            return trends
        except Exception as e:
            print(f"Error fetching from RSS: {e}")
            return []

    def get_all_trends(self, query: str = "global news", rss_url: Optional[str] = None) -> List[RawTrend]:
        """Aggregate trends from multiple sources with custom query and RSS."""
        trends = self.fetch_from_newsapi(query=query)

        rss_url = rss_url or "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        trends.extend(self.fetch_from_rss(rss_url))
        return trends
