from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
)
from sqlalchemy import create_engine

DATABASE = "sqlite+aiosql:///./data.db"

engine = create_engine(
    DATABASE,
    echo=True,
    pool_timeout=10,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

def Base(declarative_base):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()