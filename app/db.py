from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DB_URL = os.getenv("DB_URL", "sqlite:///data.db")

engine = create_engine(DB_URL, echo=False, future=True, pool_pre_ping=True)
Session = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"
    id = Column(String, primary_key=True)
    name = Column(String)
    weight = Column(Integer, default=1)
    active = Column(Boolean, default=True)

class NewsItem(Base):
    __tablename__ = "news_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True)
    title = Column(String)
    source_id = Column(String, ForeignKey("sources.id"))
    published = Column(DateTime)
    score = Column(Float)
    impact = Column(Integer)
    summary = Column(Text)
    why = Column(Text)
    llm_model = Column(String)
    cost_usd = Column(Float)
    processed_at = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)
    embedding = Column(Text)  # store as JSON string list for semantic dedup

def init_db():
    Base.metadata.create_all(engine)
