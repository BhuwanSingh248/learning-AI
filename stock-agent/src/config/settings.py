import os
import sys
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
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t") or "pytest" in sys.modules

    # API Keys
    MARKETAUX_API_KEY: str = os.getenv("MARKETAUX_API_KEY", "")
    GNEWS_API_KEY: str = os.getenv("GNEWS_API_KEY", "")

    # LLM settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")
    OLLAMA_LOCAL_URL: str = os.getenv("OLLAMA_LOCAL_URL", "http://localhost:11434")

    # chunking settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    CHAR_PER_TOKEN: int = int(os.getenv("CHAR_PER_TOKEN", "4"))

    # embedding settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "384"))

    # grounding settings
    GROUNDING_MIN_SCORE: float = float(os.getenv("GROUNDING_MIN_SCORE", "-7.0"))
    GROUNDING_MIN_AVERAGE_SCORE: float = float(os.getenv("GROUNDING_MIN_AVERAGE_SCORE", "-10.5"))
    GROUNDING_MIN_CHUNKS: int = int(os.getenv("GROUNDING_MIN_CHUNKS", "1"))

    # Security & Auth Settings
    API_AUTH_ENABLED: bool = os.getenv("API_AUTH_ENABLED", "False").lower() in ("true", "1", "t")
    API_KEYS: str = os.getenv("API_KEYS", "secret-key-1,secret-key-2")
    
    # Rate Limiting (in requests per minute per client)
    RATE_LIMIT_ANALYZE: int = int(os.getenv("RATE_LIMIT_ANALYZE", "60"))
    RATE_LIMIT_SUGGEST: int = int(os.getenv("RATE_LIMIT_SUGGEST", "30"))
    RATE_LIMIT_DEBUG: int = int(os.getenv("RATE_LIMIT_DEBUG", "10"))
    RATE_LIMIT_DEFAULT: int = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
    
    # Request Budgets
    MAX_SYMBOLS: int = int(os.getenv("MAX_SYMBOLS", "5"))
    MAX_LOOKBACK_DAYS: int = int(os.getenv("MAX_LOOKBACK_DAYS", "365"))
    MAX_TOP_K: int = int(os.getenv("MAX_TOP_K", "20"))
    MAX_QUERY_CHARS: int = int(os.getenv("MAX_QUERY_CHARS", "1000"))
    MAX_PROMPT_CHARS: int = int(os.getenv("MAX_PROMPT_CHARS", "10000"))
    MAX_GENERATION_TOKENS: int = int(os.getenv("MAX_GENERATION_TOKENS", "1024"))
    MAX_WALL_CLOCK_SECONDS: float = float(os.getenv("MAX_WALL_CLOCK_SECONDS", "60.0"))
    MAX_CONCURRENT_LLM_CALLS: int = int(os.getenv("MAX_CONCURRENT_LLM_CALLS", "3"))
    
    # Quotas (limit per client per day)
    QUOTA_REQUESTS_PER_DAY: int = int(os.getenv("QUOTA_REQUESTS_PER_DAY", "1000"))

# Instantiate settings to be used across the app
settings = Settings()

