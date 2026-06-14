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

    # API Keys
    MARKETAUX_API_KEY: str = os.getenv("MARKETAUX_API_KEY", "")
    GNEWS_API_KEY: str = os.getenv("GNEWS_API_KEY", "")

    # LLM settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "phi3:mini")
    OLLAMA_LOCAL_URL: str = os.getenv("OLLAMA_LOCAL_URL", "http://localhost:11434")

    # chunking settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    CHAR_PER_TOKEN: int = int(os.getenv("CHAR_PER_TOKEN", "4"))

    # embedding settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "384"))

    # grounding settings
    GROUNDING_MIN_SCORE: float = float(os.getenv("GROUNDING_MIN_SCORE", "-5.0"))
    GROUNDING_MIN_AVERAGE_SCORE: float = float(os.getenv("GROUNDING_MIN_AVERAGE_SCORE", "-9.0"))
    GROUNDING_MIN_CHUNKS: int = int(os.getenv("GROUNDING_MIN_CHUNKS", "1"))

# Instantiate settings to be used across the app
settings = Settings()

