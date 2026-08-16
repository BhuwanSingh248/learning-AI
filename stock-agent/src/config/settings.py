import os
import sys
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_URL: str = os.getenv("DB_URL", "")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "384"))
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    APP_NAME: str = os.getenv("APP_NAME", "AI Stock Recommendation Agent")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t") or "pytest" in sys.modules

    MARKETAUX_API_KEY: str = os.getenv("MARKETAUX_API_KEY", "")
    GNEWS_API_KEY: str = os.getenv("GNEWS_API_KEY", "")

    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")
    OLLAMA_LOCAL_URL: str = os.getenv("OLLAMA_LOCAL_URL", "http://localhost:11434")

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    CHAR_PER_TOKEN: int = int(os.getenv("CHAR_PER_TOKEN", "4"))

    MODEL_NAME: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")

    GROUNDING_MIN_SCORE: float = float(os.getenv("GROUNDING_MIN_SCORE", "-7.0"))
    GROUNDING_MIN_AVERAGE_SCORE: float = float(os.getenv("GROUNDING_MIN_AVERAGE_SCORE", "-10.5"))
    GROUNDING_MIN_CHUNKS: int = int(os.getenv("GROUNDING_MIN_CHUNKS", "1"))

    # Security: authentication is fail-closed in production. API keys must be supplied
    # through the environment/secret manager; no credentials are stored in source.
    API_AUTH_ENABLED: bool = os.getenv("API_AUTH_ENABLED", "False").lower() in ("true", "1", "t")
    API_KEYS: str = os.getenv("API_KEYS", "")

    RATE_LIMIT_ANALYZE: int = int(os.getenv("RATE_LIMIT_ANALYZE", "60"))
    RATE_LIMIT_SUGGEST: int = int(os.getenv("RATE_LIMIT_SUGGEST", "30"))
    RATE_LIMIT_DEBUG: int = int(os.getenv("RATE_LIMIT_DEBUG", "10"))
    RATE_LIMIT_DEFAULT: int = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))

    MAX_SYMBOLS: int = int(os.getenv("MAX_SYMBOLS", "5"))
    MAX_LOOKBACK_DAYS: int = int(os.getenv("MAX_LOOKBACK_DAYS", "365"))
    MAX_TOP_K: int = int(os.getenv("MAX_TOP_K", "20"))
    MAX_QUERY_CHARS: int = int(os.getenv("MAX_QUERY_CHARS", "1000"))
    MAX_PROMPT_CHARS: int = int(os.getenv("MAX_PROMPT_CHARS", "10000"))
    MAX_GENERATION_TOKENS: int = int(os.getenv("MAX_GENERATION_TOKENS", "1024"))
    MAX_WALL_CLOCK_SECONDS: float = float(os.getenv("MAX_WALL_CLOCK_SECONDS", "60.0"))
    MAX_CONCURRENT_LLM_CALLS: int = int(os.getenv("MAX_CONCURRENT_LLM_CALLS", "3"))
    QUOTA_REQUESTS_PER_DAY: int = int(os.getenv("QUOTA_REQUESTS_PER_DAY", "1000"))


settings = Settings()
