import pytest
from unittest.mock import AsyncMock

from src.config.settings import settings
from src.security.middleware import circuit_breakers, security_manager


def test_no_default_credentials_are_embedded():
    assert settings.API_KEYS == "" or all("secret-key" not in key for key in settings.API_KEYS.split(","))
    assert all("postgresql+asyncpg://stock_agent_admin:12345678" not in settings.DB_URL for _ in [0])


def test_api_key_validation_uses_configured_credentials():
    original = settings.API_KEYS
    settings.API_KEYS = "test-key"
    try:
        assert security_manager.validate_key("test-key")
        assert not security_manager.validate_key("test-key-wrong")
    finally:
        settings.API_KEYS = original


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_repeated_failures():
    breaker = circuit_breakers["/analyze"]
    original_threshold = breaker.failure_threshold
    original_timeout = breaker.reset_timeout
    breaker.failure_threshold = 2
    breaker.reset_timeout = 60
    breaker.failures = 0
    breaker.opened_at = None
    try:
        assert await breaker.allow()
        await breaker.record_failure()
        assert await breaker.allow()
        await breaker.record_failure()
        assert not await breaker.allow()
        await breaker.record_success()
        assert await breaker.allow()
    finally:
        breaker.failure_threshold = original_threshold
        breaker.reset_timeout = original_timeout
        breaker.failures = 0
        breaker.opened_at = None
