import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
import uvicorn

# Import centralized configuration and base modules
from src.config.logger import logger
from src.config.settings import settings
from src.config.database import engine
from src.api.routes import router as api_router

async def init_db():
    try:
        # Check database connection asynchronously
        async with engine.begin() as connection:
            result = await connection.execute(text("SELECT 1"))
            logger.info("Database connection strictly verified via asyncpg! DB runs successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AI Stock Recommendation Agent...")
    if settings.DB_URL:
        logger.info("Environment variables logic checked. Configuration successfully loaded.")
        logger.info(f"App running: {settings.APP_NAME}")
        
    logger.info("Connecting to PostgreSQL database asynchronously...")
    await init_db()
    logger.info("Base architecture successfully boots! Service completely ready.")
    
    yield
    
    logger.info("Shutting down Application...")

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered stock recommendation engine",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Adjust as needed for production
)

# Connect Orchestration Agent endpoints
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
