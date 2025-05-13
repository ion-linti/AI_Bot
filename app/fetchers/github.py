import httpx, bs4, re
from datetime import datetime
from .base import BaseFetcher, RawItem

class GitHubTrendingFetcher(BaseFetcher):
    async def fetch(self) -> list[RawItem]:
        async with httpx.AsyncClient(timeout=30) as client:
            html = (await client.get(self.url, headers={"User-Agent":"Mozilla/5.0"})).text
        soup = bs4.BeautifulSoup(html, "lxml")
        items=[]
        for repo in soup.select("article.Box-row"):
            a = repo.select_one("h2 a")
            if not a: continue
            title = a.get_text(strip=True)
            href = "https://github.com"+a["href"]
            star_tag = repo.select_one("a[href$='/stargazers']")
            stars = int(re.sub(r'\D', '', star_tag.text)) if star_tag else 0
            items.append({
                "url": href,
                "title": title,
                "stars": stars,
                "published": datetime.utcnow(),
                "raw": {}
            })
        return items
