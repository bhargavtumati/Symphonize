from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DB_POOL_SIZE = 83
WEB_CONCURRENCY = 9
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URI,
    connect_args={"options": "-csearch_path=public"},
    echo=True,
)

SessionLocal = sessionmaker(engine)

# Define a session dependency in FastAPI
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()