import feedparser, httpx, asyncio
from datetime import datetime
from .base import BaseFetcher, RawItem

class RSSFetcher(BaseFetcher):
    async def fetch(self) -> list[RawItem]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(self.url, headers={"User-Agent":"AI-News-Bot/1.0"})
        feed = feedparser.parse(resp.text)
        items = []
        for e in feed.entries:
            published = None
            if hasattr(e, "published_parsed"):
                published = datetime(*e.published_parsed[:6])
            items.append({
                "url": e.link,
                "title": e.title,
                "published": published,
                "raw": e
            })
        return items
