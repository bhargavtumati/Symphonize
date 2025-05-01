from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Safe database connection pooling strategy
MAX_CONNECTIONS = 60
WEB_CONCURRENCY = 9
RESERVED_CONNECTIONS = 10  # for admin tools, migrations, etc.

# Calculate safe pool size per worker
AVAILABLE_CONNECTIONS = MAX_CONNECTIONS - RESERVED_CONNECTIONS
POOL_SIZE = max(AVAILABLE_CONNECTIONS // WEB_CONCURRENCY, 2)

# Set up SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URI,
    pool_size=POOL_SIZE,           # per-process pool size
    max_overflow=5,                # allows short burst capacity
    connect_args={
        "sslmode": "disable",  #"require",      # enforce SSL connection
        "options": "-csearch_path=public"  # set schema path
    },
    echo=True,
)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# FastAPI dependency for DB session
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
