"""Seed default sources into the database."""
from app.db import init_db, Session, Source
from app.config.sources_loader import load_sources


def main():
    init_db()
    with Session() as session:
        for src in load_sources():
            if not session.query(Source).filter_by(id=src.id).first():
                session.add(Source(
                    id=src.id,
                    name=src.id,
                    weight=src.weight
                ))
        session.commit()
    print("✅ sources seeded")

if __name__ == "__main__":
    main()
