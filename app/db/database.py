from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import settings

_DATABASE_URL = settings.DATABASE_URL


if not _DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Please set it to a Postgres connection string.")

if _DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("This project requires Postgres. Your DATABASE_URL is configured for sqlite. Please update to a Postgres URL.")

# Create engine for Postgres (psycopg2 dialect or async variants may be used by users)
engine = create_engine(_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
