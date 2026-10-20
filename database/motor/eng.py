import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE = os.getenv("DATABASE", "sqlite+aiosqlite:///./data/data.db")
if DATABASE.startswith("sqlite:///"):
    DATABASE = "sqlite+aiosqlite:///" + DATABASE[len("sqlite:///"):]

if DATABASE.startswith("sqlite+aiosqlite:///"):
    folder = os.path.dirname(DATABASE.split(":///", 1)[1])
    if folder:
        os.makedirs(folder, exist_ok=True)

engine = create_async_engine(DATABASE, echo=os.getenv("SQL_ECHO", "0") == "1")
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def init_db():
    from backend.models import device, event, operation, system, track, user  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
