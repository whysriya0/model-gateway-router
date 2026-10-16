
import asyncio
import httpx
import app.reliability 

from app.reliability import (
    CircuitBreaker,
    TokenBucket,
    retry_request,
    request_with_fallback
)


def test_circuit_breaker():
    breaker = CircuitBreaker(failure_limit=2)

    assert breaker.allow_request() is True

    breaker.record_failure()
    assert breaker.state == "closed"

    breaker.record_failure()
    assert breaker.state == "open"
    assert breaker.allow_request() is False

    breaker.record_success()
    assert breaker.state == "closed"


def test_rate_limiter():
    bucket = TokenBucket(rate=1, capacity=2)

    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is False


def test_retry():
    attempts = 0

    async def unstable_request():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise httpx.ConnectError("Temporary failure")

        return "Success"

    async def run():
        return await retry_request(
            unstable_request,
            max_attempts=3
        )

    result = asyncio.run(run())

    assert result == "Success"
    assert attempts == 3


def test_fallback():

    class FakeProvider:

        async def complete(self, req, model):

            if model == "small":
                raise httpx.ConnectError("Model unavailable")

            return "Strong response"

    async def run():
        return await request_with_fallback(
            req=None,
            provider=FakeProvider(),
            primary_model="small",
            fallback_model="strong"
        )

    result, used_fallback = asyncio.run(run())

    assert result == "Strong response"
    assert used_fallback is True
