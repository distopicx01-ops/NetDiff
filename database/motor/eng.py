import os
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
DATABASE = os.getenv('DATABASE', 'sqlite:///./data.db')
if DATABASE.startswith('sqlite:///'):
    folder = os.path.dirname(DATABASE.replace('sqlite:///', '', 1))
    if folder:
        os.makedirs(folder, exist_ok=True)
engine = create_engine(DATABASE, echo=os.getenv('SQL_ECHO', '0') == '1', pool_timeout=10, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
