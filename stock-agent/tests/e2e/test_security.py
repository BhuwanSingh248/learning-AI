import pytest
import httpx
import asyncio
from unittest.mock import patch, AsyncMock
from main import app
from src.config.settings import settings
from src.security.middleware import rate_limiter, quota_manager

@pytest.fixture(autouse=True)
def reset_security_managers():
    # Clear rate limit and quota histories before/after each test
    rate_limiter.history.clear()
    quota_manager.usage.clear()
    yield
    rate_limiter.history.clear()
    quota_manager.usage.clear()

@pytest.mark.asyncio
async def test_authentication_disabled_by_default():
    """
    By default, auth is disabled. Standard requests should succeed without credentials.
    """
    # Ensure settings match default
    original_auth_enabled = settings.API_AUTH_ENABLED
    settings.API_AUTH_ENABLED = False
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/capabilities")
            assert response.status_code == 200
    finally:
        settings.API_AUTH_ENABLED = original_auth_enabled

@pytest.mark.asyncio
async def test_authentication_enabled_validation():
    """
    When auth is enabled, missing or invalid API keys must return HTTP 401.
    Valid keys must be accepted.
    """
    original_auth_enabled = settings.API_AUTH_ENABLED
    original_api_keys = settings.API_KEYS
    
    settings.API_AUTH_ENABLED = True
    settings.API_KEYS = "test-key-1,test-key-2"
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. No key -> 401
            res_missing = await client.get("/capabilities")
            assert res_missing.status_code == 401
            assert "Unauthorized" in res_missing.json()["detail"]
            
            # 2. Invalid key -> 401
            res_invalid = await client.get("/capabilities", headers={"X-API-Key": "bad-key"})
            assert res_invalid.status_code == 401
            
            # 3. Valid key via X-API-Key -> 200
            res_valid_header = await client.get("/capabilities", headers={"X-API-Key": "test-key-1"})
            assert res_valid_header.status_code == 200
            
            # 4. Valid key via Authorization Bearer token -> 200
            res_valid_bearer = await client.get("/capabilities", headers={"Authorization": "Bearer test-key-2"})
            assert res_valid_bearer.status_code == 200
    finally:
        settings.API_AUTH_ENABLED = original_auth_enabled
        settings.API_KEYS = original_api_keys

@pytest.mark.asyncio
async def test_rate_limiting_enforcement():
    """
    Repeated requests exceeding the configured limit must return HTTP 429.
    """
    original_limit = settings.RATE_LIMIT_DEFAULT
    # Set limit to a low value
    settings.RATE_LIMIT_DEFAULT = 2
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # First request -> OK
            r1 = await client.get("/capabilities")
            assert r1.status_code == 200
            
            # Second request -> OK
            r2 = await client.get("/capabilities")
            assert r2.status_code == 200
            
            # Third request -> 429
            r3 = await client.get("/capabilities")
            assert r3.status_code == 429
            assert "Rate limit" in r3.json()["detail"]
    finally:
        settings.RATE_LIMIT_DEFAULT = original_limit

@pytest.mark.asyncio
async def test_quota_limits_enforcement():
    """
    Client requests exceeding the daily quota limit must return HTTP 429.
    """
    original_quota = settings.QUOTA_REQUESTS_PER_DAY
    settings.QUOTA_REQUESTS_PER_DAY = 1
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # First request -> OK
            r1 = await client.get("/capabilities")
            assert r1.status_code == 200
            
            # Second request -> 429 Quota Exceeded
            r2 = await client.get("/capabilities")
            assert r2.status_code == 429
            assert "Daily quota exceeded" in r2.json()["detail"]
    finally:
        settings.QUOTA_REQUESTS_PER_DAY = original_quota

@pytest.mark.asyncio
async def test_debug_endpoint_protection_in_production():
    """
    In production mode (DEBUG=False), debug endpoints must require a valid key
    even if global authentication is disabled. Anonymous access must return HTTP 403.
    """
    original_debug = settings.DEBUG
    original_auth = settings.API_AUTH_ENABLED
    original_keys = settings.API_KEYS
    
    settings.DEBUG = False
    settings.API_AUTH_ENABLED = False
    settings.API_KEYS = "prod-admin-key"
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Access debug endpoint anonymously -> 403 Forbidden
            r_anon = await client.post(
                "/debug/retrieval", 
                json={"symbol": "AAPL", "query": "test", "top_k": 3}
            )
            assert r_anon.status_code == 403
            assert "Forbidden" in r_anon.json()["detail"]
            
            # 2. Access with valid key -> Should bypass 403 (though might return 500/validation if DB mock is absent, but definitely not 403)
            with patch("src.rag.hybrid_retriever.HybridRetriever.search_detailed", new_callable=AsyncMock) as mock_search:
                mock_search.return_value = ([], [], [])
                r_auth = await client.post(
                    "/debug/retrieval",
                    headers={"X-API-Key": "prod-admin-key"},
                    json={"symbol": "AAPL", "query": "test", "top_k": 3}
                )
                assert r_auth.status_code == 200
    finally:
        settings.DEBUG = original_debug
        settings.API_AUTH_ENABLED = original_auth
        settings.API_KEYS = original_keys

@pytest.mark.asyncio
async def test_request_budget_validations():
    """
    Inputs exceeding limits (symbols, lookback days, top_k, query length)
    must trigger validation errors (422).
    """
    original_max_symbols = settings.MAX_SYMBOLS
    original_max_lookback = settings.MAX_LOOKBACK_DAYS
    original_max_top_k = settings.MAX_TOP_K
    original_max_query = settings.MAX_QUERY_CHARS
    
    settings.MAX_SYMBOLS = 2
    settings.MAX_LOOKBACK_DAYS = 30
    settings.MAX_TOP_K = 5
    settings.MAX_QUERY_CHARS = 10
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Symbols count budget
            res_symbols = await client.post("/suggest", json={"symbols": ["AAPL", "MSFT", "GOOG"], "lookback_days": 10})
            assert res_symbols.status_code == 422
            assert "symbols" in res_symbols.text
            
            # 2. Lookback days budget
            res_lookback = await client.post("/suggest", json={"symbols": ["AAPL"], "lookback_days": 100})
            assert res_lookback.status_code == 422
            assert "lookback_days" in res_lookback.text
            
            # 3. Top_k budget
            res_top_k = await client.post("/analyze", json={"symbol": "AAPL", "query": "test", "top_k": 10})
            assert res_top_k.status_code == 422
            assert "top_k" in res_top_k.text
            
            # 4. Query length budget
            res_query = await client.post("/analyze", json={"symbol": "AAPL", "query": "query exceeding ten chars", "top_k": 3})
            assert res_query.status_code == 422
            assert "query" in res_query.text
    finally:
        settings.MAX_SYMBOLS = original_max_symbols
        settings.MAX_LOOKBACK_DAYS = original_max_lookback
        settings.MAX_TOP_K = original_max_top_k
        settings.MAX_QUERY_CHARS = original_max_query

@pytest.mark.asyncio
async def test_wall_clock_timeout_enforcement():
    """
    Requests exceeding settings.MAX_WALL_CLOCK_SECONDS must time out and return HTTP 504.
    """
    from src.config.database import get_db

    async def slow_get_db():
        await asyncio.sleep(0.2)
        yield AsyncMock()

    app.dependency_overrides[get_db] = slow_get_db
    
    try:
        with patch.object(settings, "MAX_WALL_CLOCK_SECONDS", 0.05):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                res = await client.post(
                    "/analyze", 
                    json={"symbol": "AAPL", "query": "test", "top_k": 3}
                )
                assert res.status_code == 504
                assert "timed out" in res.json()["detail"]
    finally:
        app.dependency_overrides.clear()
