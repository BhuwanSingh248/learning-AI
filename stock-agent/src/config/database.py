from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from src.config.settings import settings

# Create SQLAlchemy engine
# pool_pre_ping ensures the connections are verified before usage
engine = create_async_engine(
    settings.DB_URL, 
    pool_pre_ping=True
)

# Base class for SQLAlchemy models
Base = declarative_base()

# Configured "AsyncSessionLocal" class
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_db():
    """
    Generator function to provide a database async session.
    Closes the session after use.
    """
    async with AsyncSessionLocal() as db:
        yield db
