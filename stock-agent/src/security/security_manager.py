import asyncio
import hmac
import time
from collections import defaultdict
from typing import Optional

from src.config.settings import settings
from src.config.logger import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """Thread-safe and async-safe in-memory sliding-window rate limiter."""

    def __init__(self):
        self.history = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_rate_limited(self, client_id: str, endpoint: str, limit: int, period: int = 60) -> bool:
        async with self._lock:
            now = time.time()
            key = f"{client_id}:{endpoint}"
            self.history[key] = [t for t in self.history[key] if now - t < period]
            if len(self.history[key]) >= limit:
                logger.warning(
                    "RateLimit | Limit tripped for client=%s endpoint=%s limit=%d/%ds current=%d",
                    client_id, endpoint, limit, period, len(self.history[key]),
                )
                return True
            self.history[key].append(now)
            return False


class QuotaManager:
    """In-memory daily request quota manager."""

    def __init__(self):
        self.usage = defaultdict(int)
        self.last_reset = time.time()
        self._lock = asyncio.Lock()

    async def check_and_increment(self, client_id: str, limit: int) -> bool:
        async with self._lock:
            now = time.time()
            if now - self.last_reset > 86400:
                self.usage.clear()
                self.last_reset = now
            if self.usage[client_id] >= limit:
                logger.warning("QuotaManager | Quota exceeded for client=%s", client_id)
                return False
            self.usage[client_id] += 1
            return True


class CircuitBreaker:
    """Simple async-safe circuit breaker for expensive API workloads."""

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.opened_at: Optional[float] = None
        self._lock = asyncio.Lock()

    async def allow(self) -> bool:
        async with self._lock:
            if self.opened_at is None:
                return True
            if time.monotonic() - self.opened_at >= self.reset_timeout:
                self.opened_at = None
                self.failures = 0
                return True
            return False

    async def record_success(self) -> None:
        async with self._lock:
            self.failures = 0
            self.opened_at = None

    async def record_failure(self) -> None:
        async with self._lock:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.opened_at = time.monotonic()
                logger.error("CircuitBreaker | Opened after %d failures", self.failures)


class SecurityManager:
    """Validates API keys without exposing or logging credential material."""

    @staticmethod
    def _keys(raw_keys: str) -> list[str]:
        return [key.strip() for key in raw_keys.split(",") if key.strip()]

    def validate_key(self, api_key: Optional[str], admin: bool = False) -> bool:
        if not api_key:
            return False
        configured = self._keys(settings.ADMIN_API_KEYS if admin else settings.API_KEYS)
        return any(hmac.compare_digest(api_key, key) for key in configured)

    def identify_client(self, api_key: Optional[str], client_ip: str) -> str:
        if api_key and self.validate_key(api_key):
            # Use a stable non-secret alias rather than logging any key prefix.
            for index, key in enumerate(self._keys(settings.API_KEYS), start=1):
                if hmac.compare_digest(api_key, key):
                    return f"client_{index}"
            return "client_unknown"
        return f"ip:{client_ip}"

    def has_api_keys(self) -> bool:
        return bool(self._keys(settings.API_KEYS))

    def has_admin_keys(self) -> bool:
        return bool(self._keys(settings.ADMIN_API_KEYS))
