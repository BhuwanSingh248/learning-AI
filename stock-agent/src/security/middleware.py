import time
import uuid
import asyncio
from typing import Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from src.config.logger import setup_logger, trace_id_var
from src.config.settings import settings
from src.security.security_manager import RateLimiter, QuotaManager, SecurityManager

logger = setup_logger(__name__)

# Instantiate global managers
rate_limiter = RateLimiter()
quota_manager = QuotaManager()
security_manager = SecurityManager()

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to enforce API authentication, rate limits, 
    daily client quotas, wall-clock timeouts, and trace-based audit logging.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # 1. Generate or extract Trace ID
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4().hex)
        token_ctx = trace_id_var.set(trace_id)
        
        # 2. Extract Client IP and Auth Credentials
        client_ip = request.client.host if request.client else "127.0.0.1"
        
        # Extract API key from header or Authorization Bearer token
        api_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            api_key = auth_header[7:].strip()
            
        path = request.url.path
        method = request.method
        
        # Redact headers for secure audit logging
        redacted_headers = {}
        for k, v in request.headers.items():
            if k.lower() in ("x-api-key", "authorization"):
                redacted_headers[k] = "[REDACTED]"
            else:
                redacted_headers[k] = v
            
        logger.info(
            "Audit | Request Start: %s %s | ClientIP=%s | Headers=%s",
            method, path, client_ip, redacted_headers
        )
        
        try:
            # 3. Authentication & Authorization check
            is_valid_key = security_manager.validate_key(api_key)
            
            if settings.API_AUTH_ENABLED:
                if not is_valid_key:
                    logger.warning("Audit | Unauthorized access attempt: path=%s IP=%s", path, client_ip)
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Unauthorized: Invalid or missing API key."}
                    )
            else:
                # If global auth is disabled, check if debug/admin route protection applies
                is_debug_route = path.startswith("/debug")
                if is_debug_route and not settings.DEBUG:
                    # In production, debug routes cannot be invoked anonymously
                    if not is_valid_key:
                        logger.warning("Audit | Forbidden anonymous debug access attempt: path=%s IP=%s", path, client_ip)
                        return JSONResponse(
                            status_code=403,
                            content={"detail": "Forbidden: Debug operations cannot be invoked anonymously in production."}
                        )
            
            # 4. Identify the client for rate limits/quotas
            client_id = security_manager.identify_client(api_key, client_ip)
            
            # 5. Enforce Daily Quotas
            if not await quota_manager.check_and_increment(client_id, settings.QUOTA_REQUESTS_PER_DAY):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many Requests: Daily quota exceeded."}
                )
                
            # 6. Enforce Endpoint-Specific Rate Limits
            if path == "/analyze":
                limit = settings.RATE_LIMIT_ANALYZE
            elif path == "/suggest":
                limit = settings.RATE_LIMIT_SUGGEST
            elif path.startswith("/debug"):
                limit = settings.RATE_LIMIT_DEBUG
            else:
                limit = settings.RATE_LIMIT_DEFAULT
                
            if await rate_limiter.is_rate_limited(client_id, path, limit):
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Too Many Requests: Rate limit of {limit} requests per minute exceeded."}
                )
                
            # 7. Execute request with Wall-Clock timeout
            try:
                async with asyncio.timeout(settings.MAX_WALL_CLOCK_SECONDS):
                    response = await call_next(request)
            except TimeoutError:
                logger.error(
                    "Audit | Timeout: %s %s timed out after %.2fs for client=%s",
                    method, path, settings.MAX_WALL_CLOCK_SECONDS, client_id
                )
                return JSONResponse(
                    status_code=504,
                    content={"detail": f"Request execution timed out (exceeded limit of {settings.MAX_WALL_CLOCK_SECONDS}s)."}
                )
                
            duration = time.time() - start_time
            # Add Trace ID to response headers
            response.headers["X-Trace-ID"] = trace_id
            
            logger.info(
                "Audit | Request End: %s %s | Status=%d | Client=%s | Duration=%.3fs",
                method, path, response.status_code, client_id, duration
            )
            return response
            
        finally:
            trace_id_var.reset(token_ctx)
