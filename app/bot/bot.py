import dotenv
dotenv.load_dotenv()

import os, logging, asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from app.db import Session as DBSession, NewsItem, Source, init_db
from app.config.sources_loader import load_sources

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TG_CHANNEL_ID")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()
dp = Dispatcher()
dp.include_router(router)

# -------- helper ----------
def fmt_money(val: float) -> str:
    return f"${val:.2f}"

# -------- commands ---------
@router.message(F.text.startswith("/start"))
async def start_cmd(message: Message):
    await message.answer("🤖 AI News Radar ready.\nCommands: /stats, /digest now, /toggle <source_id>")

@router.message(F.text.startswith("/stats"))
async def stats(message: Message):
    with DBSession() as s:
        day_ago = datetime.utcnow() - timedelta(days=1)
        count = s.query(NewsItem).filter(NewsItem.processed_at >= day_ago).count()
        cost = sum(v[0] or 0 for v in s.query(NewsItem.cost_usd).all())
    await message.answer(f"📰 <b>{count}</b> news (24 h)\n💰 <b>{fmt_money(cost)}</b> spent")

@router.message(F.text.startswith("/toggle"))
async def toggle(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply("Usage: /toggle <source_id>")
        return
    sid = args[1]
    with DBSession() as s:
        src = s.query(Source).filter_by(id=sid).first()
        if not src:
            await message.reply(f"Source {sid} not found.")
            return
        src.active = not src.active
        s.commit()
    await message.reply(f"Source <b>{sid}</b> is now {'✅ active' if src.active else '🚫 disabled'}.")

@router.message(F.text.startswith("/digest"))
async def digest_now(message: Message):
    if "now" not in message.text:
        await message.reply("Use /digest now")
        return
    from app.scheduler import send_digest
    await send_digest()
    await message.reply("✅ Digest sent.")

@router.message(F.text.startswith("/digest week"))
async def digest_week(message: Message):
    week_ago = datetime.utcnow() - timedelta(days=7)
    with DBSession() as s:
        items = (
            s.query(NewsItem)
            .filter(NewsItem.processed_at >= week_ago, NewsItem.impact >= 3)
            .order_by(NewsItem.impact.desc())
            .all()
        )
    if not items:
        await message.reply("📭 Nothing important this week.")
        return
    lines = [f"★ {i.impact} — <a href='{i.url}'>{i.title}</a>" for i in items]
    text = "🗓 <b>Weekly Digest</b>\n" + "\n".join(lines[:15])
    await message.reply(text, disable_web_page_preview=True)

# ------------- notifier -------------
async def send_breaking(item: NewsItem):
    text = (
        f"🚨 <b>{item.title}</b>\n"
        f"{item.summary}\n<i>{item.why}</i>\n"
        f"<a href='{item.url}'>читать подробнее</a>"
    )
    await bot.send_message(CHANNEL_ID, text, disable_web_page_preview=True)

# ------------- bootstrap -------------
async def run_bot():
    logging.basicConfig(level=logging.INFO)
    init_db()

    # Optional: auto-fill sources table if empty
    source_objs = load_sources()
    with DBSession() as s:
        for sc in source_objs:
            if not s.query(Source).filter_by(id=sc.id).first():
                s.add(Source(id=sc.id, name=sc.id, weight=sc.weight))
        s.commit()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())
