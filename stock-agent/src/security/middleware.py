import time
import uuid
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from src.config.logger import setup_logger, trace_id_var
from src.config.settings import settings
from src.security.security_manager import RateLimiter, QuotaManager, SecurityManager, CircuitBreaker

logger = setup_logger(__name__)
rate_limiter = RateLimiter()
quota_manager = QuotaManager()
security_manager = SecurityManager()
circuit_breakers = {
    "/analyze": CircuitBreaker(),
    "/suggest": CircuitBreaker(),
    "/ingest": CircuitBreaker(),
}


class SecurityMiddleware(BaseHTTPMiddleware):
    """Enforce authentication, budgets, quotas, rate limits, admin isolation and audit logging."""

    @staticmethod
    def _api_key(request: Request) -> str | None:
        api_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            api_key = auth_header[7:].strip()
        return api_key

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()
        trace_id = request.headers.get("X-Trace-ID") or uuid.uuid4().hex
        token_ctx = trace_id_var.set(trace_id)
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method
        api_key = self._api_key(request)
        is_admin_route = path.startswith(("/debug", "/admin", "/ingest"))

        # Never log credential-bearing headers or cookies.
        redacted_headers = {
            k: "[REDACTED]" if k.lower() in ("x-api-key", "authorization", "cookie", "set-cookie") else v
            for k, v in request.headers.items()
        }
        logger.info("Audit | Request Start: %s %s | ClientIP=%s | Headers=%s", method, path, client_ip, redacted_headers)

        try:
            # Admin/debug/ingestion routes are always separately protected.
            if is_admin_route:
                if not settings.DEBUG and not security_manager.validate_key(api_key, admin=True):
                    logger.warning("Audit | Forbidden admin access: path=%s IP=%s", path, client_ip)
                    return JSONResponse(status_code=403, content={"detail": "Forbidden: admin credentials required."})
            elif settings.API_AUTH_ENABLED and not security_manager.validate_key(api_key):
                logger.warning("Audit | Unauthorized access: path=%s IP=%s", path, client_ip)
                return JSONResponse(status_code=401, content={"detail": "Unauthorized: invalid or missing API key."})

            if settings.API_AUTH_ENABLED and not security_manager.has_api_keys() and not settings.DEBUG:
                return JSONResponse(status_code=503, content={"detail": "Authentication is enabled but no API keys are configured."})

            client_id = security_manager.identify_client(api_key, client_ip)
            if not await quota_manager.check_and_increment(client_id, settings.QUOTA_REQUESTS_PER_DAY):
                return JSONResponse(status_code=429, content={"detail": "Too Many Requests: daily quota exceeded."})

            if path == "/analyze":
                limit = settings.RATE_LIMIT_ANALYZE
            elif path == "/suggest":
                limit = settings.RATE_LIMIT_SUGGEST
            elif is_admin_route:
                limit = settings.RATE_LIMIT_DEBUG
            else:
                limit = settings.RATE_LIMIT_DEFAULT

            if await rate_limiter.is_rate_limited(client_id, path, limit):
                return JSONResponse(status_code=429, content={"detail": "Too Many Requests: rate limit exceeded."})

            breaker = circuit_breakers.get(path)
            if breaker and not await breaker.allow():
                return JSONResponse(status_code=503, content={"detail": "Service temporarily unavailable; upstream failures are being isolated."})

            try:
                async with asyncio.timeout(settings.MAX_WALL_CLOCK_SECONDS):
                    response = await call_next(request)
            except TimeoutError:
                if breaker:
                    await breaker.record_failure()
                return JSONResponse(status_code=504, content={"detail": "Request execution timed out."})

            if breaker:
                if response.status_code >= 500:
                    await breaker.record_failure()
                else:
                    await breaker.record_success()

            response.headers["X-Trace-ID"] = trace_id
            logger.info(
                "Audit | Request End: %s %s | Status=%d | Client=%s | Duration=%.3fs",
                method, path, response.status_code, client_id, time.monotonic() - start_time,
            )
            return response
        finally:
            trace_id_var.reset(token_ctx)
