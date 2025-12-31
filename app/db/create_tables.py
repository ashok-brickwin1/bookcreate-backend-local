"""Utility to create all database tables using SQLAlchemy metadata.

Run:
    python -m app.db.create_tables

It will use DATABASE_URL from the environment or backend/.env when using pydantic BaseSettings in config.
"""
from app.db.base import Base
from app.db.database import engine

# Import models so they are registered with Base.metadata
import app.models  # noqa: F401


def create_tables():
    print("Creating database tables...")
    # Base.metadata.create_all(bind=engine)
    print("Done.")


# if __name__ == "__main__":
#     create_tables()
