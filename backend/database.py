"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://homecontrol:homecontrol123@db:5432/homecontrol"
)

# Railway provides DATABASE_URL as postgresql:// — convert to asyncpg format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Create all tables on startup and run safe schema migrations.
    Uses CREATE TABLE IF NOT EXISTS (via create_all) and ALTER TABLE ... IF NOT EXISTS
    so it is safe to run on every startup against an existing database.
    """
    async with engine.begin() as conn:
        # Import all models so SQLAlchemy is aware of them
        from models import User, Device, Relay, Schedule, PowerLog  # noqa: F401
        # Create any missing tables (idempotent — won't touch existing tables)
        await conn.run_sync(Base.metadata.create_all)

        # ── Safe column migrations for existing tables ────────────────────────
        # Add wattage column to relays table if it doesn't exist yet
        # (needed when upgrading from v2.0.0 → v2.1.0)
        await conn.execute(
            __import__("sqlalchemy").text(
                "ALTER TABLE relays ADD COLUMN IF NOT EXISTS wattage FLOAT DEFAULT 60.0"
            )
        )
