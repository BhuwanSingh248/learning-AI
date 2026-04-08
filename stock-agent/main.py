import sys
import asyncio
from sqlalchemy import text

# Import centralized configuration and base modules
from src.config.logger import logger
from src.config.settings import settings
from src.config.database import engine, get_db

async def init_db():
    try:
        # Check database connection asynchronously
        async with engine.begin() as connection:
            result = await connection.execute(text("SELECT 1"))
            logger.info("Database connection strictly verified via asyncpg! DB runs successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        sys.exit(1)

async def main():
    logger.info("Initializing AI Stock Recommendation Agent...")
    
    # 1. Log Config Load
    if settings.DB_URL:
        logger.info("Environment variables logic checked. Configuration successfully loaded.")
        logger.info(f"App running: {settings.APP_NAME}")
        logger.info(f"Vector Dimension limit: {settings.VECTOR_DIMENSION}, Top K queries: {settings.TOP_K}")

    # 2. Check Database Logic
    logger.info("Connecting to PostgreSQL database asynchronously...")
    await init_db()

    logger.info("Base architecture successfully boots! Service completely ready.")

if __name__ == "__main__":
    asyncio.run(main())
