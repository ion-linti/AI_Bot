import httpx
from .base import BaseFetcher, RawItem

class JSONAPIFetcher(BaseFetcher):
    async def fetch(self) -> list[RawItem]:
        async with httpx.AsyncClient(timeout=20) as client:
            data = (await client.get(self.url)).json()
        items = []
        for obj in data:
            items.append({
                "url": obj.get("url") or obj.get("link"),
                "title": obj.get("title") or obj.get("name"),
                "published": None,
                "raw": obj
            })
        return items
