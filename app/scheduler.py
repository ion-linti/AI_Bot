import dotenv
dotenv.load_dotenv()

import asyncio, logging, os, json
from datetime import datetime, UTC
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.db import init_db, Session as DBSession, NewsItem
from app.config.sources_loader import load_sources
from app.fetchers.rss import RSSFetcher
from app.fetchers.api import JSONAPIFetcher
from app.fetchers.github import GitHubTrendingFetcher
from app.processor.ranker import compute_score
from app.processor.summarizer import summarize
from app.processor.semantic import embed, is_duplicate
from app.bot.bot import send_breaking, bot, CHANNEL_ID

logging.basicConfig(level=logging.INFO)

FETCHER_MAP = {
    "rss": RSSFetcher,
    "api": JSONAPIFetcher,
    "github": GitHubTrendingFetcher,
}

async def process_source(source_cfg):
    fetcher_cls = FETCHER_MAP.get(source_cfg.type)
    if not fetcher_cls:
        logging.warning("No fetcher for type %s", source_cfg.type)
        return
    fetcher = fetcher_cls(source_cfg.id, source_cfg.url)
    try:
        items = await fetcher.fetch()
    except Exception as e:
        logging.error("Fetcher %s error: %s", source_cfg.id, e)
        return

    summarization_tasks = []
    for raw in items:
        with DBSession() as s:
            if s.query(NewsItem).filter_by(url=raw["url"]).first():
                continue
            stars = raw.get("stars", 0)
            score = compute_score(stars, 0, source_cfg.weight, raw.get("published"))
            summarization_tasks.append((raw, score, source_cfg.weight))

    for raw, score, weight in summarization_tasks:
        try:
            data = await summarize(raw, weight)
        except Exception as e:
            logging.error("Summarize error: %s", e)
            continue
        emb = await embed(data["summary"])
        with DBSession() as s:
            existing_embs = [json.loads(e[0]) for e in s.query(NewsItem.embedding).filter(NewsItem.embedding != None)]
        if await is_duplicate(emb, existing_embs):
            continue
        with DBSession() as s:
            ni = NewsItem(
                url=raw["url"],
                title=raw["title"],
                source_id=source_cfg.id,
                published=raw.get("published"),
                score=score,
                impact=data["impact"],
                summary=data["summary"],
                why=data["why"],
                llm_model=data["llm_model"],
                cost_usd=data["cost_usd"],
                embedding=json.dumps(emb),
            )
            s.add(ni)
            s.commit()
            if ni.impact >= 4:
                await send_breaking(ni)

async def main_cycle():
    cfgs = load_sources()
    await asyncio.gather(*(process_source(c) for c in cfgs if c.active))

async def send_digest():
    with DBSession() as s:
        items = s.query(NewsItem).filter(NewsItem.sent == False, NewsItem.impact < 4).all()
        if not items:
            return
        lines = [f"★ {i.impact} — <a href='{i.url}'>{i.title}</a>" for i in items]
        text = "🗞 <b>Daily Digest</b>\n" + "\n".join(lines)
        await bot.send_message(CHANNEL_ID, text, disable_web_page_preview=True)
        for it in items:
            it.sent = True
        s.commit()

async def start():
    init_db()
    sched = AsyncIOScheduler(timezone="Europe/Kyiv")
    sched.add_job(main_cycle, "interval", minutes=15, next_run_time=datetime.now(UTC))
    sched.add_job(send_digest, "cron", hour=7, minute=30)
    sched.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start())
