import os
from dotenv import load_dotenv

# Load explicitly the .env from the current working directory, or let dotenv find it
load_dotenv()

class Settings:
    # Database connection URL
    DB_URL: str = os.getenv(
        "DB_URL", "postgresql+asyncpg://stock_agent_admin:12345678@localhost:5432/stock_agent"
    )
    
    # Vector DB settings
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "384"))
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    
    # General app settings
    APP_NAME: str = os.getenv("APP_NAME", "AI Stock Recommendation Agent")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Instantiate settings to be used across the app
settings = Settings()
