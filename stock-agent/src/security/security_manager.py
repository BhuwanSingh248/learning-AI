import time
import asyncio
from collections import defaultdict
from typing import Optional, Set
from src.config.settings import settings
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class RateLimiter:
    """
    Thread-safe and async-safe in-memory sliding window rate limiter.
    """
    def __init__(self):
        # Maps client_key (e.g. client_id:endpoint) to list of request timestamps
        self.history = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_rate_limited(self, client_id: str, endpoint: str, limit: int, period: int = 60) -> bool:
        """
        Check if the client has exceeded the limit of requests for the given endpoint.
        
        Args:
            client_id: Unique identifier for the client.
            endpoint: The API endpoint being accessed.
            limit: Maximum requests allowed in the period.
            period: Time window in seconds (default 60s).
            
        Returns:
            True if rate limited (rejected), False otherwise.
        """
        async with self._lock:
            now = time.time()
            key = f"{client_id}:{endpoint}"
            
            # Filter out timestamps older than the period
            self.history[key] = [t for t in self.history[key] if now - t < period]
            
            if len(self.history[key]) >= limit:
                logger.warning(
                    "RateLimit | Limit tripped for client=%s on endpoint=%s (limit=%d/%ds, current=%d)",
                    client_id, endpoint, limit, period, len(self.history[key])
                )
                return True
                
            self.history[key].append(now)
            return False


class QuotaManager:
    """
    In-memory daily request quota manager.
    """
    def __init__(self):
        # Maps client_id to number of requests made in the current daily period
        self.usage = defaultdict(int)
        self.last_reset = time.time()
        self._lock = asyncio.Lock()

    async def check_and_increment(self, client_id: str, limit: int) -> bool:
        """
        Check if client daily quota is exceeded, otherwise increment usage.
        
        Returns:
            True if within quota, False if quota is exceeded.
        """
        async with self._lock:
            now = time.time()
            
            # Reset daily quota if 24 hours have elapsed
            if now - self.last_reset > 86400:
                logger.info("QuotaManager | 24h passed, resetting daily usage quotas.")
                self.usage.clear()
                self.last_reset = now
                
            current_usage = self.usage[client_id]
            if current_usage >= limit:
                logger.warning(
                    "QuotaManager | Quota exceeded for client=%s (limit=%d, usage=%d)",
                    client_id, limit, current_usage
                )
                return False
                
            self.usage[client_id] += 1
            return True


class SecurityManager:
    """
    Validates API keys and formats client identifiers.
    """
    def validate_key(self, api_key: str) -> bool:
        """
        Validates whether the provided API key is registered.
        """
        if not api_key:
            return False
        valid_keys = {
            key.strip() for key in settings.API_KEYS.split(",") if key.strip()
        }
        return api_key in valid_keys

    def identify_client(self, api_key: Optional[str], client_ip: str) -> str:
        """
        Derives a client identifier.
        """
        if api_key and self.validate_key(api_key):
            # Mask key for identifier or map it
            return f"key:{api_key[:6]}..."
        return f"ip:{client_ip}"
