import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()

RAW_DB = os.getenv('DATABASE', 'sqlite:///./data/data.db')
if RAW_DB.startswith('sqlite:///'):
    ASYNC_DB = RAW_DB.replace('sqlite:///', 'sqlite+aiosqlite:///')
    folder = os.path.dirname(RAW_DB.replace('sqlite:///', ''))
    if folder:
        os.makedirs(folder, exist_ok=True)
else:
    ASYNC_DB = RAW_DB

engine = create_async_engine(ASYNC_DB, echo=os.getenv('SQL_ECHO', '0') == '1', connect_args={'check_same_thread': False})
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    from backend.models import device, event, operation, system, track, user  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
